document.addEventListener('DOMContentLoaded', function() {
  const spotifyBtn = document.getElementById('spotify-btn');
  const youtubeBtn = document.getElementById('youtube-btn');
  const playlistContent = document.getElementById('playlist-content');
  const playlistResults = document.getElementById('playlist-results');
  const loadingIndicator = document.querySelector('.loading');

  function loadContent(url) {
      playlistContent.style.display = 'block';
      playlistContent.classList.remove('visible');
      loadingIndicator.style.display = 'block';
      playlistResults.innerHTML = '';

      fetch(url)
          .then(response => response.text())
          .then(html => {
              const parser = new DOMParser();
              const doc = parser.parseFromString(html, 'text/html');
              const content = doc.querySelector('.search-results').innerHTML;
              playlistResults.innerHTML = content;
              loadingIndicator.style.display = 'none';
              setTimeout(() => {
                  playlistContent.classList.add('visible');
              }, 50);
              history.pushState(null, '', url);
              addTransferListeners();
          })
          .catch(error => {
              console.error('Error:', error);
              playlistResults.innerHTML = '<p>Error loading playlists. Please try again.</p>';
              loadingIndicator.style.display = 'none';
              playlistContent.classList.add('visible');
          });
  }

  function addTransferListeners() {
      const transferButtons = document.querySelectorAll('.btn-transfer');
      transferButtons.forEach(button => {
          button.addEventListener('click', function(e) {
              e.preventDefault();
              const url = this.href;
              fetch(url)
                  .then(response => {
                      if (response.ok) {
                          alert('Transfer successful!');
                          // Reload the current playlist view
                          loadContent(window.location.href);
                      } else {
                          throw new Error('Transfer failed');
                      }
                  })
                  .catch(error => {
                      console.error('Error:', error);
                      alert('Error transferring playlist. Please try again.');
                  });
          });
      });
  }

  spotifyBtn.addEventListener('click', function() {
      loadContent("{% url 'playlist' %}");
      this.classList.add('btn-spotify-active');
      youtubeBtn.classList.remove('btn-youtube-active');
  });

  youtubeBtn.addEventListener('click', function() {
      loadContent("{% url 'youtube_playlists' %}");
      this.classList.add('btn-youtube-active');
      spotifyBtn.classList.remove('btn-spotify-active');
  });

  window.addEventListener('popstate', function() {
      location.reload();
  });
});
