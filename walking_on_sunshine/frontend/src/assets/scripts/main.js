async function searchAlbum() {
    const albumName = document.getElementById('albumSearch').value;
    const resultDiv = document.getElementById('result');
    
    // Show loading state
    resultDiv.innerHTML = '<p>Searching...</p>';
    
    try {
        const response = await fetch(`/generate_route?album_name=${encodeURIComponent(albumName)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <h3>Route Generated!</h3>
                <p>Album: ${data.album_name}</p>
                <p>Length: ${data.length_minutes}</p>
                <p>Walking Distance: ${data.distance_km} km</p>
                <a href="${data.maps_url}" target="_blank" class="maps-link">Open Route in Google Maps</a>
            `;
        } else {
            resultDiv.innerHTML = `<p class="error">Error: ${data.detail}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}