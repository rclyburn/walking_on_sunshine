console.log('main.js loaded');

// Utilities
function $(id) { return document.getElementById(id); }
function escapeHTML(s) {
    return String(s).replace(/[&<>\"']/g, (m) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
}
// Debounce helper
function debounce(fn, ms = 250) {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// Elements
const albumInput = $('albumSearch');
const addrInput = $('addressSearch');
const dropdown = $('albumDropdown');
const form = $('searchForm');
const resultDiv = $('result');
const submitBtn = $('submitBtn');
const useLocBtn = $('useLocationBtn');

// State for autocomplete
let aborter;
let activeIndex = -1;
let items = [];
let placesLoadPromise;
let placesDisabled = false;
let addressAutocomplete;

// Init
document.addEventListener('DOMContentLoaded', () => {
    if (albumInput) albumInput.value = '';
    if (addrInput) addrInput.value = '';
    albumInput?.focus();
});

// Album autocomplete: fetch to /search_albums?query=
const updateAlbums = debounce(async () => {
    const q = albumInput.value.trim();
    if (!q) {
        dropdown.innerHTML = "";
        dropdown.style.display = "none";
        albumInput.setAttribute('aria-expanded', 'false');
        return;
    }

    aborter?.abort();
    aborter = new AbortController();

    try {
        const res = await fetch(`/search_albums?query=${encodeURIComponent(q)}`, { signal: aborter.signal });
        const data = await res.json();
        items = Array.isArray(data.results) ? data.results : [];
        if (!items.length) {
            dropdown.innerHTML = `<div class="dropdown-item" aria-disabled="true">No results</div>`;
            dropdown.style.display = 'block';
            albumInput.setAttribute('aria-expanded', 'true');
            activeIndex = -1;
            return;
        }

        dropdown.innerHTML = items.map((a, i) => `
      <div class="dropdown-item" role="option" aria-selected="${i === activeIndex}" data-name="${escapeHTML(a.name)}" data-artist="${escapeHTML(a.artist || '')}">
        <strong>${escapeHTML(a.name)}</strong> <em>${a.artist ? 'by ' + escapeHTML(a.artist) : ''}</em>
      </div>
    `).join("");
        dropdown.style.display = 'block';
        albumInput.setAttribute('aria-expanded', 'true');
        activeIndex = -1;
    } catch (e) {
        if (e.name !== 'AbortError') {
            dropdown.innerHTML = `<div class="dropdown-item">Error fetching albums</div>`;
            dropdown.style.display = 'block';
            albumInput.setAttribute('aria-expanded', 'true');
        }
    }
}, 250);

albumInput.addEventListener('input', updateAlbums);
albumInput.addEventListener('keydown', (e) => {
    if (!['ArrowDown', 'ArrowUp', 'Enter', 'Escape'].includes(e.key)) return;
    const options = [...dropdown.querySelectorAll('.dropdown-item[data-name]')];
    if (e.key === 'ArrowDown') {
        activeIndex = Math.min(activeIndex + 1, options.length - 1);
        e.preventDefault();
    }
    if (e.key === 'ArrowUp') {
        activeIndex = Math.max(activeIndex - 1, 0);
        e.preventDefault();
    }
    if (e.key === 'Enter' && activeIndex >= 0) {
        const el = options[activeIndex];
        albumInput.value = el.dataset.name;
        dropdown.style.display = 'none';
        e.preventDefault();
    }
    if (e.key === 'Escape') { dropdown.style.display = 'none'; }
    options.forEach((el, i) => el.setAttribute('aria-selected', i === activeIndex));
});
document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target) && e.target !== albumInput) {
        dropdown.style.display = 'none';
    }
});
dropdown.addEventListener('click', (e) => {
    const item = e.target.closest('.dropdown-item');
    if (item && item.dataset.name) {
        albumInput.value = item.dataset.name;
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
    }
});

// Address autocomplete (Google Places)
async function loadGoogleMapsScript(apiKey) {
    if (window.google?.maps?.places) return;

    const existing = document.querySelector('script[data-google-maps="places"]');
    if (existing) {
        await new Promise((resolve, reject) => {
            existing.addEventListener('load', resolve, { once: true });
            existing.addEventListener('error', () => reject(new Error('Google Maps script failed to load')), {
                once: true,
            });
        });
        return;
    }

    await new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
        script.async = true;
        script.defer = true;
        script.dataset.googleMaps = 'places';
        script.onload = resolve;
        script.onerror = () => reject(new Error('Google Maps script failed to load'));
        document.head.appendChild(script);
    });
}

async function ensurePlacesLibrary() {
    if (placesDisabled) return false;
    if (window.google?.maps?.places) return true;
    if (!placesLoadPromise) {
        placesLoadPromise = (async () => {
            try {
                const res = await fetch('/maps_config');
                if (!res.ok) return false;
                const data = await res.json();
                if (!data?.places_autocomplete_enabled || !data?.google_maps_api_key) {
                    placesDisabled = true;
                    return false;
                }
                await loadGoogleMapsScript(data.google_maps_api_key);
                return !!window.google?.maps?.places;
            } catch (err) {
                console.error('Failed to initialise Google Places', err);
                return false;
            }
        })();
    }
    const loaded = await placesLoadPromise;
    if (!loaded && !placesDisabled) placesLoadPromise = null;
    return loaded;
}

async function initAddressAutocomplete() {
    if (addressAutocomplete || !addrInput) return;
    const loaded = await ensurePlacesLibrary();
    if (!loaded || !window.google?.maps?.places) return;

    addressAutocomplete = new google.maps.places.Autocomplete(addrInput, {
        fields: ['formatted_address', 'geometry', 'name'],
        types: ['geocode'],
    });
    addressAutocomplete.addListener('place_changed', () => {
        const place = addressAutocomplete.getPlace();
        const formatted = place?.formatted_address || place?.name;
        if (formatted) addrInput.value = formatted;
    });
}

addrInput?.addEventListener('focus', () => { initAddressAutocomplete(); });

// Use my location
useLocBtn.addEventListener('click', () => {
    if (!navigator.geolocation) return alert('Geolocation not supported');
    navigator.geolocation.getCurrentPosition((pos) => {
        const { latitude, longitude } = pos.coords;
        addrInput.value = `${latitude},${longitude}`;
    }, () => alert('Could not get location'));
});

// Main submit handler
form.addEventListener('submit', (e) => {
    e.preventDefault();
    searchAlbum();
});

// Core action
async function searchAlbum() {
    const albumName = albumInput.value.trim();
    const startAddress = addrInput.value.trim();

    if (!albumName) {
        albumInput.focus();
        return;
    }
    if (!startAddress) {
        addrInput.focus();
        return;
    }

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = `<div class="loading">Generating route…</div>`;

    const params = new URLSearchParams({
        album_name: albumName,
        start_address: startAddress,
    });

    submitBtn.disabled = true;
    try {
        // Adjust this path if your backend differs
        const url = `/generate_route?${params.toString()}`;
        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            const message = data && data.error ? data.error : `Error: ${response.status}`;
            resultDiv.innerHTML = `<p>${escapeHTML(message)}</p>`;
            return;
        }

        // Validate & format
        const name = data.album_name ?? albumName;
        const artist = data.artist || '';
        const lengthMin = Number(data.length_minutes);
        const distanceKm = Number(data.distance_km);
        const mapsUrl = data.maps_url || '#';

        const chips = [];
        if (!Number.isNaN(lengthMin)) chips.push(`⏱️ ${lengthMin} min`);
        if (!Number.isNaN(distanceKm)) chips.push(`🚶 ${distanceKm} km`);
        if (artist) chips.push(`🎧 ${escapeHTML(artist)}`);

        resultDiv.innerHTML = `
      <h2>${escapeHTML(name)}</h2>
      <div class="stat-row">
        ${chips.map(c => `<span class="chip">${escapeHTML(c)}</span>`).join('')}
      </div>
      <p>Start: ${escapeHTML(startAddress)}</p>
      <p><a href="${encodeURI(mapsUrl)}" target="_blank" rel="noopener" class="maps-link">View Route in Google Maps</a></p>
    `;
    } catch (err) {
        resultDiv.innerHTML = `<p>Something went wrong. Please try again.</p>`;
        console.error(err);
    } finally {
        submitBtn.disabled = false;
    }
}
