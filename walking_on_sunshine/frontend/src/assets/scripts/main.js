console.log('main.js loaded');

async function searchAlbum() {
    // Debug element existence
    const albumInput = document.getElementById('albumSearch');
    const addressInput = document.getElementById('addressSearch');
    
    console.log('Album input element:', albumInput);
    console.log('Address input element:', addressInput);
    
    if (!albumInput || !addressInput) {
        console.error('One or both input elements not found!');
        return;
    }

    const albumName = albumInput.value.trim();
    const startAddress = addressInput.value.trim();
    const resultDiv = document.getElementById('result');
    
    console.log('Album Name:', albumName);
    console.log('Start Address:', startAddress);
    
    console.log('Album name value:', albumName);
    console.log('Start address value:', startAddress);

    if (!albumName || !startAddress) {
        console.log('Missing required values:', {
            albumName: Boolean(albumName),
            startAddress: Boolean(startAddress)
        });
        alert('Please enter both an album name and starting address');
        return;
    }

    resultDiv.innerHTML = '<div class="loading">Loading...</div>';
    resultDiv.style.display = 'block';

    const url = `/generate_route?album_name=${encodeURIComponent(albumName)}&start_address=${encodeURIComponent(startAddress)}`;
    console.log('Full request URL:', url);

    try {
        const response = await fetch(url);
        console.log('Response status:', response.status);
        const data = await response.json();

        console.log('Response data:', data);
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <h2>${data.album_name}</h2>
                <p>Starting Location: ${startAddress}</p>
                <p>Album Length: ${data.length_minutes}</p>
                <p>Walking Distance: ${data.distance_km} km</p>
                <p><a href="${data.maps_url}" target="_blank" class="maps-link">View Route in Google Maps</a></p>
            `;
        } else {
            resultDiv.innerHTML = `<p class="error">Error: ${data.detail || 'Unknown error occurred'}</p>`;
        }
    } catch (error) {
        console.error('Error:', error);
        resultDiv.innerHTML = `<p class="error">Error: ${error.message || 'Could not process request'}</p>`;
    }
}

// Allow Enter key to trigger search
document.getElementById('albumSearch').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        searchAlbum();
    }
});

document.getElementById('addressSearch').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        searchAlbum();
    }
});

const albumInput = document.getElementById('albumSearch');
const dropdown = document.getElementById('albumDropdown');

albumInput.addEventListener('input', async function() {
    const query = albumInput.value.trim();
    if (!query) {
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
        return;
    }
    try {
        const res = await fetch(`/search_albums?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (data.results && data.results.length > 0) {
            dropdown.innerHTML = data.results.map(album =>
                `<div class="dropdown-item" data-name="${album.name}">
                    <strong>${album.name}</strong> <em>by ${album.artist}</em>
                </div>`
            ).join('');
            dropdown.style.display = 'block';
        } else {
            dropdown.innerHTML = '<div class="dropdown-item">No results</div>';
            dropdown.style.display = 'block';
        }
    } catch (e) {
        dropdown.innerHTML = '<div class="dropdown-item">Error fetching albums</div>';
        dropdown.style.display = 'block';
    }
});

dropdown.addEventListener('click', function(e) {
    const item = e.target.closest('.dropdown-item');
    if (item && item.dataset.name) {
        albumInput.value = item.dataset.name;
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
    }
});