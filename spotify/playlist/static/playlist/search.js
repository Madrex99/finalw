document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search');
    const playlistContainer = document.getElementById('playlist-container');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const searchTerm = searchInput.value.trim();
        
        // Show loading indicator
        playlistContainer.innerHTML = '<div class="loading">Searching...</div>';

        // Perform AJAX request
        fetch(`/search_playlists/?query=${encodeURIComponent(searchTerm)}`)
            .then(response => response.text())
            .then(html => {
                playlistContainer.innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                playlistContainer.innerHTML = '<div class="error">An error occurred while searching. Please try again.</div>';
            });
    });

    // Implement real-time search as user types (optional)
    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            searchForm.dispatchEvent(new Event('submit'));
        }, 300); // Wait for 300ms after the user stops typing
    });
});