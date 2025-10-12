async function searchAlbum() {
    const albumName = document.getElementById('albumSearch').value;
    const resultDiv = document.getElementById('result');
    
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
                <p>Album: ${albumName}</p>
                <a href="${data.maps_url}" target="_blank">Open Route in Google Maps</a>
            `;
        } else {
            resultDiv.innerHTML = `<p class="error">Error: ${data.detail}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}