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
const stepper = $('stepper');
const albumStepPanel = $('albumStep');
const albumPreview = $('albumPreview');
const albumArt = $('albumArt');
const albumArtBack = $('albumArtBack');
const albumArtCard = $('albumArtCard');
const albumPreviewTitle = $('albumPreviewTitle');
const albumPreviewArtist = $('albumPreviewArtist');
const locationStep = $('locationStep');
const stepProgress = $('stepProgress');
const resultCard = $('result');

// State for autocomplete
let aborter;
let activeIndex = -1;
let items = [];
let placesLoadPromise;
let placesDisabled = false;
let addressAutocomplete;
let selectedAlbum = null;
const accentCache = new Map();
const canvasEl = document.createElement('canvas');
const canvasCtx = canvasEl.getContext('2d', { willReadFrequently: true }) || null;
const DEFAULT_ACCENT = '#4f46e5';

function setPanelHidden(panel) {
    if (!panel) return;
    panel.classList.remove('is-active');
    panel.classList.add('is-hidden');
    panel.setAttribute('hidden', '');
    panel.setAttribute('aria-hidden', 'true');
}

function setPanelActive(panel) {
    if (!panel) return;
    panel.classList.remove('is-hidden');
    panel.removeAttribute('hidden');
    panel.setAttribute('aria-hidden', 'false');
    requestAnimationFrame(() => panel.classList.add('is-active'));
}

function setActiveStep(step = 1) {
    if (!stepper) return;
    stepper.querySelectorAll('[data-step]').forEach((el) => {
        const idx = Number(el.dataset.step);
        el.classList.toggle('active', idx === step);
    });
}

function updateProgress(step = 1) {
    if (!stepProgress) return;
    const pct = step === 2 ? 100 : 50;
    stepProgress.style.setProperty('--progress-pct', `${pct}%`);
}

function goToStep(step = 1) {
    setActiveStep(step);
    if (step === 1) {
        setPanelActive(albumStepPanel);
        albumStepPanel?.classList.remove('is-dimmed');
        setPanelHidden(locationStep);
    } else if (step === 2) {
        setPanelActive(albumStepPanel);
        albumStepPanel?.classList.remove('is-dimmed');
        setPanelActive(locationStep);
    }
    updateProgress(step);
}

function showAlbumPreview(album) {
    if (!albumPreview) return;
    const hasImage = Boolean(album.image);
    if (albumArt) {
        if (hasImage) {
            albumArt.src = album.image;
            albumArt.alt = `${album.name} album art`;
            albumArt.classList.remove('is-placeholder');
            albumArt.removeAttribute('hidden');
            if (albumArtBack) {
                albumArtBack.style.backgroundImage = `url('${album.image}')`;
                albumArtBack.setAttribute('aria-hidden', 'true');
            }
            applyAlbumAccent(album.image);
        } else {
            albumArt.removeAttribute('src');
            albumArt.alt = 'Album art not available';
            albumArt.classList.add('is-placeholder');
            albumArt.setAttribute('hidden', '');
            if (albumArtBack) {
                albumArtBack.style.removeProperty('background-image');
            }
            albumArtCard?.classList.remove('is-flipped');
            applyAccentColor(DEFAULT_ACCENT);
        }
    }
    if (albumPreviewTitle) albumPreviewTitle.textContent = album.name || 'Unknown album';
    if (albumPreviewArtist) albumPreviewArtist.textContent = album.artist ? `by ${album.artist}` : '';
    albumPreview.hidden = false;
    albumPreview.classList.remove('pop-in');
    void albumPreview.offsetWidth;
    albumPreview.classList.add('pop-in');
}

function applyAccentColor(color) {
    const root = document.documentElement;
    root.style.setProperty('--accent', color);
    if (albumPreview) {
        albumPreview.style.setProperty('--accent', color);
    }
    if (resultCard) {
        resultCard.style.setProperty('--accent', color);
    }
}

function applyAlbumAccent(imageUrl) {
    if (!imageUrl || !canvasCtx) {
        applyAccentColor(DEFAULT_ACCENT);
        return;
    }
    if (accentCache.has(imageUrl)) {
        applyAccentColor(accentCache.get(imageUrl));
        return;
    }
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.referrerPolicy = 'no-referrer';
    img.src = imageUrl;
    img.onload = () => {
        const size = 80;
        canvasEl.width = size;
        canvasEl.height = size;
        try {
            canvasCtx.drawImage(img, 0, 0, size, size);
        } catch (err) {
            applyAccentColor(DEFAULT_ACCENT);
            return;
        }
        let imageData;
        try {
            imageData = canvasCtx.getImageData(0, 0, size, size);
        } catch (err) {
            applyAccentColor(DEFAULT_ACCENT);
            return;
        }
        const { data } = imageData;
        let r = 0; let g = 0; let b = 0; let count = 0;
        for (let i = 0; i < data.length; i += 16) { // sample every fourth pixel
            const alpha = data[i + 3];
            if (alpha < 128) continue;
            r += data[i];
            g += data[i + 1];
            b += data[i + 2];
            count += 1;
        }
        if (!count) {
            applyAccentColor(DEFAULT_ACCENT);
            return;
        }
        r = Math.round(r / count);
        g = Math.round(g / count);
        b = Math.round(b / count);
        const accent = `rgb(${r}, ${g}, ${b})`;
        accentCache.set(imageUrl, accent);
        applyAccentColor(accent);
    };
    img.onerror = () => applyAccentColor(DEFAULT_ACCENT);
}

function triggerAlbumFlip(shouldFlip) {
    if (!albumArtCard) return;
    albumArtCard.classList.remove('is-flipped');
    if (!shouldFlip) return;
    void albumArtCard.offsetWidth;
    albumArtCard.classList.add('is-flipped');
}

function pickBestAddress(results) {
    if (!Array.isArray(results) || !results.length) return null;
    const priority = new Set([
        'street_address',
        'premise',
        'subpremise',
        'route',
        'intersection',
        'neighborhood',
    ]);
    for (const candidate of results) {
        const types = candidate?.types || [];
        if (types.some((t) => priority.has(t))) {
            return candidate.formatted_address || candidate.name || null;
        }
    }
    const first = results[0];
    return first?.formatted_address || first?.name || null;
}

function renderRoutePreview(containerId, coords) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!Array.isArray(coords) || coords.length < 2) {
        container.innerHTML = `<div class="map-preview-fallback">Map preview unavailable</div>`;
        return;
    }

    const validPoints = coords
        .map((pt) => ({
            lon: Number(pt.lon),
            lat: Number(pt.lat),
        }))
        .filter((pt) => Number.isFinite(pt.lon) && Number.isFinite(pt.lat));

    if (validPoints.length < 2) {
        container.innerHTML = `<div class="map-preview-fallback">Map preview unavailable</div>`;
        return;
    }

    const width = container.clientWidth || container.offsetWidth || 360;
    const height = container.clientHeight || 240;
    const padding = Math.min(width, height) * 0.18;

    let minLon = Infinity;
    let maxLon = -Infinity;
    let minLat = Infinity;
    let maxLat = -Infinity;

    validPoints.forEach(({ lon, lat }) => {
        if (lon < minLon) minLon = lon;
        if (lon > maxLon) maxLon = lon;
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
    });

    const lonSpan = Math.max(maxLon - minLon, 0.0001);
    const latSpan = Math.max(maxLat - minLat, 0.0001);

    const innerWidth = width - padding * 2;
    const innerHeight = height - padding * 2;

    const points = validPoints.map(({ lon, lat }) => ({
        x: padding + ((lon - minLon) / lonSpan) * innerWidth,
        y: padding + ((maxLat - lat) / latSpan) * innerHeight,
    }));

    const pathD = points
        .map(({ x, y }, index) => `${index ? 'L' : 'M'}${x.toFixed(2)} ${y.toFixed(2)}`)
        .join(' ');

    const gridSpacing = 32;
    const cols = Math.ceil(width / gridSpacing);
    const rows = Math.ceil(height / gridSpacing);
    let gridLines = '';
    for (let i = 0; i <= cols; i += 1) {
        const x = (i * width) / cols;
        gridLines += `<line x1="${x.toFixed(2)}" y1="0" x2="${x.toFixed(2)}" y2="${height}" />`;
    }
    for (let j = 0; j <= rows; j += 1) {
        const y = (j * height) / rows;
        gridLines += `<line x1="0" y1="${y.toFixed(2)}" x2="${width}" y2="${y.toFixed(2)}" />`;
    }

    const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent') || DEFAULT_ACCENT;
    const startPoint = points[0];
    const endPoint = points[points.length - 1];

    container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <g class="map-canvas__grid">${gridLines}</g>
      <path class="map-canvas__route" d="${pathD}" stroke="${accent.trim() || DEFAULT_ACCENT}"></path>
      <circle class="map-canvas__marker" cx="${startPoint.x.toFixed(2)}" cy="${startPoint.y.toFixed(2)}" r="7"></circle>
      <circle class="map-canvas__marker map-canvas__marker--end" cx="${endPoint.x.toFixed(2)}" cy="${endPoint.y.toFixed(2)}" r="7"></circle>
    </svg>
  `;
}

function setupCopyRouteButton(url) {
    const btn = resultDiv.querySelector('.copy-link-btn');
    if (!btn) return;
    const routeUrl = btn.dataset.route || url;
    const handleClick = async () => {
        if (!navigator.clipboard) {
            alert('Copy not supported on this browser');
            return;
        }
        const originalText = btn.textContent;
        try {
            await navigator.clipboard.writeText(routeUrl);
            btn.textContent = 'Copied!';
            btn.classList.add('copied');
            setTimeout(() => {
                btn.textContent = originalText;
                btn.classList.remove('copied');
            }, 1600);
        } catch (copyErr) {
            console.error('Failed to copy link', copyErr);
            btn.textContent = 'Copy failed';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 2000);
        }
    };

    btn.onclick = handleClick;
}

function resetAlbumSelection({ keepInput = true } = {}) {
    selectedAlbum = null;
    if (!keepInput && albumInput) albumInput.value = '';
    if (albumPreview) {
        albumPreview.hidden = true;
        albumPreview.classList.remove('pop-in');
    }
    if (albumPreviewTitle) albumPreviewTitle.textContent = '';
    if (albumPreviewArtist) albumPreviewArtist.textContent = '';
    albumArtCard?.classList.remove('is-flipped');
    if (albumArt) {
        albumArt.setAttribute('hidden', '');
        albumArt.classList.add('is-placeholder');
        albumArt.removeAttribute('src');
    }
    albumArtBack?.style.removeProperty('background-image');
    applyAccentColor(DEFAULT_ACCENT);
    goToStep(1);
}

function handleAlbumSelection(album) {
    if (!album) return;
    selectedAlbum = album;
    if (albumInput) albumInput.value = album.name || albumInput.value;
    dropdown.innerHTML = '';
    dropdown.style.display = 'none';
    showAlbumPreview(album);
    triggerAlbumFlip(Boolean(album.image));
    goToStep(2);
    setTimeout(() => addrInput?.focus(), 150);
}

function selectAlbumByIndex(idx) {
    if (idx < 0 || idx >= items.length) return;
    handleAlbumSelection(items[idx]);
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    if (albumInput) albumInput.value = '';
    if (addrInput) addrInput.value = '';
    goToStep(1);
    if (albumPreview) albumPreview.hidden = true;
    applyAccentColor(DEFAULT_ACCENT);
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
      <div class="dropdown-item" role="option" aria-selected="${i === activeIndex}" data-index="${i}" data-name="${escapeHTML(a.name)}" data-artist="${escapeHTML(a.artist || '')}">
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
        selectAlbumByIndex(activeIndex);
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
    if (item) {
        const idx = Number(item.dataset.index);
        if (!Number.isNaN(idx)) {
            selectAlbumByIndex(idx);
        }
    }
});

albumInput.addEventListener('input', () => {
    if (selectedAlbum && albumInput.value.trim() !== (selectedAlbum.name || '').trim()) {
        resetAlbumSelection({ keepInput: true });
    }
    updateAlbums();
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
useLocBtn.addEventListener('click', async () => {
    if (!navigator.geolocation) return alert('Geolocation not supported');
    navigator.geolocation.getCurrentPosition(async (pos) => {
        const { latitude, longitude } = pos.coords;

        const loaded = await ensurePlacesLibrary();
        if (!loaded || !window.google?.maps?.Geocoder) {
            addrInput.value = `${latitude},${longitude}`;
            return;
        }

        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: { lat: latitude, lng: longitude } }, (results, status) => {
            if (status === 'OK' && results?.length) {
                const formatted = pickBestAddress(results);
                addrInput.value = formatted || `${latitude},${longitude}`;
                return;
            }
            addrInput.value = `${latitude},${longitude}`;
        });
    }, () => alert('Could not get location'), {
        enableHighAccuracy: true,
        maximumAge: 30000,
        timeout: 15000,
    });
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

    const effectiveAlbumName = selectedAlbum?.name || albumName;
    const params = new URLSearchParams({
        album_name: effectiveAlbumName,
        start_address: startAddress,
    });
    if (selectedAlbum?.id) {
        params.set('album_id', selectedAlbum.id);
    }

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
        const name = data.album_name ?? effectiveAlbumName;
        const artist = data.artist || '';
        const lengthMin = Number(data.length_minutes);
        const albumDurationLabel = data.album_duration_label || '';
        const distanceKm = Number(data.distance_km);
        const mapsUrl = data.maps_url || '#';
        const hasMapsLink = !!mapsUrl && mapsUrl !== '#';
        const resolvedStartAddress = (data.start_address && String(data.start_address).trim()) || startAddress;
        const trackCount = Number(data.track_count);
        const releaseYear = data.release_year ? String(data.release_year) : '';

        if (addrInput && resolvedStartAddress) {
            addrInput.value = resolvedStartAddress;
        }

        if (data.album_image_url && albumArt) {
            albumArt.src = data.album_image_url;
            albumArt.alt = `${name} album art`;
            albumArt.classList.remove('is-placeholder');
            albumArt.removeAttribute('hidden');
            albumArtBack?.style.setProperty('background-image', `url("${data.album_image_url}")`);
            applyAlbumAccent(data.album_image_url);
        }

        if (albumPreviewTitle && name) {
            albumPreviewTitle.textContent = name;
        }

        if (albumPreviewArtist) {
            albumPreviewArtist.textContent = artist ? `by ${artist}` : '';
        }

        const chips = [];

        const detailsExtras = [];
        if (releaseYear) detailsExtras.push(`<span class="album-detail">${escapeHTML(releaseYear)}</span>`);
        if (!Number.isNaN(trackCount) && trackCount > 0) {
            detailsExtras.push(`<span class="album-detail">${escapeHTML(trackCount.toString())} tracks</span>`);
        }

        const chipMarkup = chips.map(c => `<span class="chip">${escapeHTML(c)}</span>`).join('');
        const hasDistance = !Number.isNaN(distanceKm);
        const hasLength = !Number.isNaN(lengthMin);
        const previewCoords = Array.isArray(data.route_preview)
            ? data.route_preview
                .map((pt) => ({ lat: Number(pt.lat), lon: Number(pt.lon) }))
                .filter((pt) => Number.isFinite(pt.lat) && Number.isFinite(pt.lon))
            : [];
        const canRenderMap = previewCoords.length >= 2;
        const mapEmbedHtml = typeof data.map_embed_html === 'string' ? data.map_embed_html : '';

        let mapSection;
        if (mapEmbedHtml) {
            mapSection = `
        <div class="map-canvas map-canvas--embed">
          <iframe src="${mapEmbedHtml}" title="Route preview map" loading="lazy" allowfullscreen></iframe>
        </div>`;
        } else if (canRenderMap) {
            mapSection = `<div id="mapPreview" class="map-canvas" aria-label="Route preview map"></div>`;
        } else {
            mapSection = `<div class="map-preview-fallback">Map preview unavailable</div>`;
        }

        const albumHeader = `
      <div class="album-header">
        <div class="album-header__info">
          <h2>${escapeHTML(name)}</h2>
          ${detailsExtras.length ? `<div class="album-details">${detailsExtras.join('<span class="dot">•</span>')}</div>` : ''}
        </div>
      </div>`;

        resultDiv.innerHTML = `
      ${albumHeader}
      <div class="stat-row">
        ${chipMarkup}
      </div>
      ${mapSection}
      <p>Start: ${escapeHTML(resolvedStartAddress)}</p>
      ${hasDistance || hasLength ? `<p>${hasDistance ? `${escapeHTML(distanceKm.toFixed(2))} km` : ''}${hasDistance && hasLength ? ' • ' : ''}${hasLength ? `Approx ${escapeHTML(Math.round(lengthMin))} min` : ''}</p>` : ''}
      ${hasMapsLink ? `<div class="result-actions">
        <a href="${encodeURI(mapsUrl)}" target="_blank" rel="noopener" class="maps-link">View Route in Google Maps</a>
        <button type="button" class="secondary copy-link-btn" data-route="${escapeHTML(mapsUrl)}">Copy route link</button>
      </div>` : ''}
    `;

        if (!mapEmbedHtml && canRenderMap) {
            requestAnimationFrame(() => renderRoutePreview('mapPreview', previewCoords));
        }

        if (hasMapsLink) {
            setupCopyRouteButton(mapsUrl);
        }
    } catch (err) {
        resultDiv.innerHTML = `<p>Something went wrong. Please try again.</p>`;
        console.error(err);
    } finally {
        submitBtn.disabled = false;
    }
}
