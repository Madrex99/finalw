Playlist Transfer - Spotify to YouTube and Vice Versa
====================================================

Description:
------------
Playlist Transfer is a web application that allows users to transfer playlists between Spotify and YouTube. Users can easily move their favorite playlists from one platform to the other, making it convenient to manage and enjoy their music across different services.

Features:
---------
1. User authentication and account management
2. Spotify integration for playlist retrieval and creation
3. YouTube integration for playlist retrieval and creation
4. Transfer playlists from Spotify to YouTube
5. Transfer playlists from YouTube to Spotify
6. Search functionality for playlists
7. Responsive design for various devices

Prerequisites:
--------------
- Python 3.x
- Django
- Spotify Developer Account
- Google Developer Account with YouTube Data API enabled

Installation:
-------------
1. Clone the repository:
   git clone [repository_url]
   cd [project_directory]

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install required packages:
   pip install -r requirements.txt

4. Set up environment variables:
   Create a .env file in the project root and add the following:
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=your_spotify_redirect_uri
   YOUTUBE_REDIRECT_URI=your_youtube_redirect_uri

5. Set up the YouTube client secret:
   Place your YouTube client secret JSON file in the project root and name it 'client_secret.json'

6. Run database migrations:
   python manage.py migrate

7. Create a superuser (admin):
   python manage.py createsuperuser

Configuration:
--------------
1. Spotify API:
   - Go to the Spotify Developer Dashboard and create a new app
   - Set the redirect URI in your Spotify app settings
   - Update the .env file with your Spotify app credentials

2. YouTube API:
   - Go to the Google Developer Console and create a new project
   - Enable the YouTube Data API v3
   - Create credentials (OAuth 2.0 Client ID) for a web application
   - Download the client secret JSON file and place it in the project root
   - Set the authorized redirect URIs in your Google Console project settings
   - Add your email to the test users

Usage:
------
1. Start the Django development server:
   python manage.py runserver

2. Open a web browser and navigate to http://localhost:8000

3. Register for an account or log in

4. Connect your Spotify and YouTube accounts

5. Use the interface to transfer playlists between Spotify and YouTube

Additional Notes:
-----------------
- This application uses Django's built-in SQLite database by default. For production use, consider using a more robust database system like PostgreSQL.
- Ensure that your Spotify and YouTube API credentials are kept secure and not shared publicly.
- The application uses Django's built-in authentication system. Customize the User model as needed for additional fields or functionality.

