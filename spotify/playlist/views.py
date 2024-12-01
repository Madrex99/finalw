import requests
import base64
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.timezone import now, timezone
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import json
from django.template.loader import render_to_string

from .models import User, SpotifyToken, YoutubeToken, Spotify_Playlist, Youtube_Playlist
# Create your views here.

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'playlist/home.html')

@login_required(login_url='login')
def index(request):
    return render(request, 'playlist/index.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been successfully logged in.')
            return redirect('index')
        else:
            messages.success(request, 'There was an error logging in. Please try again.')
            return redirect('login')
    else:
        return render(request, 'playlist/login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.success(request, ("There was an error registering, try again..."))
            return redirect('register')
        login(request, user)
        messages.success(request, ("Registration Successful!"))
        return render(request, 'playlist/index.html')
    else:
        return render(request, 'playlist/register.html')


def signout_user(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

#==========================================
# Spotify
#==========================================
@login_required(login_url='login')
def spotify_login(request):
    spotify_auth_url = 'https://accounts.spotify.com/authorize'
    spotify_client_id = settings.SPOTIFY_CLIENT_ID
    spotify_redirect_uri = settings.SPOTIFY_REDIRECT_URI
    scope = 'user-library-read playlist-read-private playlist-modify-public playlist-modify-private user-library-modify'

    # redirect user to spotify's authorization page
    auth_url = f"{spotify_auth_url}?client_id={spotify_client_id}&response_type=code&redirect_uri={spotify_redirect_uri}&scope={scope}"
    return redirect(auth_url)


@login_required(login_url='login')
def spotify_callback(request):
    code = request.GET.get('code')

    user_creds = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    encoded_creds = base64.b64encode(user_creds.encode()).decode()

    token_url = 'https://accounts.spotify.com/api/token'
    
    headers = {
        'Authorization': f'Basic {encoded_creds}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
    }

    response = requests.post(token_url, headers=headers, data=data)
    
    # Add error handling and debugging
    if response.status_code != 200:
        messages.error(request, "Failed to authenticate with Spotify")
        return redirect('index')

    token_info = response.json()
    
    
    try:
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        token_expires_in = token_info['expires_in']
        token_expires_at = datetime.now() + timedelta(seconds=token_expires_in)

        # Initialize the dictionaries if they don't exist
        if 'access_token' not in request.session:
            request.session['access_token'] = {}
        if 'expires_at' not in request.session:
            request.session['expires_at'] = {}

        # Save access token in session
        request.session['spotify'] = {
            'access_token': access_token,
            'expires_at': token_expires_at.timestamp(),
        }
        request.session.modified = True

        # Save info to database
        user = request.user
        SpotifyToken.objects.update_or_create(
            user=user,
            defaults={
                'refresh_token': refresh_token,
            },
        )
        
        messages.success(request, "Successfully connected to Spotify!")
        return redirect('index')
        
    except KeyError as e:
        messages.error(request, "Invalid response from Spotify")
        return redirect('index')


@login_required(login_url='login')
def spotify_refresh_token(request):
    # Check if access token is still valid
    access_token = request.session.get('access_token', {}).get('spotify')
    expires_at_str = request.session.get('expires_at', {}).get('spotify')

    if access_token and expires_at_str:
        expires_at = datetime.fromisoformat(expires_at_str).date()
        date = datetime.now().date()
        if date < expires_at:
            return access_token
    
    # If access token is expired
    refresh_token = SpotifyToken.objects.get(user=request.user).refresh_token
    token_url = 'https://accounts.spotify.com/api/token'

    response = requests.post(token_url, data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    })
    if response.status_code != 200:
        # Log the error for debugging purposes
        
        # Redirect user to the login page to re-authenticate
        return redirect('login')
    
    token_info = response.json()

    # Initialize the dictionaries if they don't exist
    if 'access_token' not in request.session:
        request.session['access_token'] = {}
    if 'expires_at' not in request.session:
        request.session['expires_at'] = {}

    # Update session with the new access token
    new_access_token = token_info['access_token']
    expires_in = token_info['expires_in']
    expires_at = datetime.now() + timedelta(seconds=expires_in)
    request.session['spotify'] = {
        'access_token': access_token,
        'expires_at': expires_at.timestamp(),
    }

    return new_access_token

#==========================================
# Youtube
#==========================================
@login_required(login_url='login')
def youtube_login(request):
    CLIENT_SECRET_FILE = settings.YOUTUBE_SECRET_FILE
    SCOPES = settings.YOUTUBE_SCOPES

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=settings.YOUTUBE_REDIRECT_URI,
    )

    flow.redirect_uri = settings.YOUTUBE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    request.session['state'] = state

    return redirect(authorization_url)

@login_required(login_url='login')
def youtube_callback(request):
    flow = Flow.from_client_secrets_file(
        settings.YOUTUBE_SECRET_FILE,
        scopes=settings.YOUTUBE_SCOPES,
        redirect_uri=settings.YOUTUBE_REDIRECT_URI,
        state=request.session['state'],
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    try:
        credentials = flow.credentials
        access_token = credentials.token
        refresh_token = credentials.refresh_token
        if isinstance(credentials.expiry, (int, float)):
            expires_at = datetime.now() + timedelta(seconds=credentials.expiry)
        elif isinstance(credentials.expiry, datetime):
            expires_at = credentials.expiry

        # Initialize the dictionaries if they don't exist
        if 'access_token' not in request.session:
            request.session['access_token'] = {}
        if 'expires_at' not in request.session:
            request.session['expires_at'] = {}

        # save access token in session
        request.session['youtube'] = {
            'access_token': access_token,
            'expires_at': expires_at.timestamp(),
        }
        # Save refresh token in database
        user = request.user
        
        if refresh_token:
            YoutubeToken.objects.update_or_create(
                user=user,
                defaults={
                    'refresh_token': refresh_token,
                }
            )
        messages.success(request, "Successfully connected to Youtube!")
        return redirect('index')
        
    except KeyError as e:
        messages.error(request, "Invalid response from Youtube")
        return redirect('index')



@login_required(login_url='login')
def youtube_refresh_token(request):
    user = request.user
    session = request.session

    session.setdefault('access_token', {})
    session.setdefault('expires_at', {})

    access_token = request.session.get('youtube', {}).get('access_token')
    expires_at_str = request.session.get('youtube', {}).get('expires_at')

    # Check if access token is still valid
    if isinstance(expires_at_str, str):
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() < expires_at:
                return access_token
        except ValueError:
            pass  # Invalid format, proceed to refresh the token
    else:
        expires_at = None

    # Get the user's refresh token from the database
    try:
        user_tokens = YoutubeToken.objects.get(user=user)
        refresh_token = user_tokens.refresh_token
    except YoutubeToken.DoesNotExist:
        logger.error(f"No YouTube token found for user {user.id}")
        messages.error(request, "YouTube authentication required. Please connect your YouTube account.")
        return redirect('youtube_login')


    # Load the client secrets file and initialize credentials
    try:
        with open(settings.YOUTUBE_SECRET_FILE, 'r') as f:
            client_info = json.load(f)['web']
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error loading YouTube client secrets: {str(e)}")
        messages.error(request, "An error occurred while accessing YouTube. Please try again later.")

    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_info["client_id"],
        client_secret=client_info["client_secret"],
    )

    try:
        credentials.refresh(Request())
    except RefreshError as e:
        logger.error(f"Refresh token expired for user {user.id}: {str(e)}")
        user_tokens.delete()
        messages.warning(request, "Your YouTube connection has expired. Please reconnect your account.")
        return redirect('youtube_login')
    except Exception as e:
        logger.error(f"Error refreshing YouTube token for user {user.id}: {str(e)}")
        messages.error(request, "An error occurred while refreshing your YouTube connection. Please try again later.")

    # Update session and database
    if isinstance(credentials.expiry, datetime):
        expires_at = credentials.expiry
    elif credentials.expiry:
        expires_at = datetime.now() + timedelta(seconds=credentials.expiry)
    else:
        expires_at = datetime.now() + timedelta(hours=1)  # Default expiry

    request.session['youtube'] = {
        'access_token': credentials.token,
        'expires_at': expires_at.isoformat(),
    }

    if credentials.refresh_token and credentials.refresh_token != refresh_token:
        user_tokens.refresh_token = credentials.refresh_token
        user_tokens.save()

    return credentials.token


#==========================================
# playlists
#==========================================
def playlist(request):
    access_token = spotify_refresh_token(request)
    user = request.user
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    playlist_url = 'https://api.spotify.com/v1/me/playlists'
    response = requests.get(playlist_url, headers=headers)

    if response.status_code == 200:
        playlists_data = response.json().get('items', [])

        
        ## print the data
        return render(request, "playlist/playlist.html", {
            "playlists": playlists_data
        })


    else:
        return None
    

def youtube_playlist(request):
    access_token = youtube_refresh_token(request)
    headers={
        "Authorization":f"Bearer {access_token}"
    }

    url = "https://www.googleapis.com/youtube/v3/playlists"
    params={
        "part":"snippet,contentDetails",
        "mine": "true"
    }

    # Make the request
    response = requests.get(url=url, headers=headers, params=params)

    if response.status_code == 200:
        playlists_data = response.json().get('items', [])

        return render(request, "playlist/youtube.html", {
            "playlists": playlists_data
        })
    else:
        return redirect('index')


def transfer_spotify_playlist_to_youtube(request, spotify_playlist_id):
    try:
        # Get access tokens using existing functions
        spotify_token = spotify_refresh_token(request)  # Assume this function exists
        youtube_token = youtube_refresh_token(request)
        
        # Initialize Spotify and YouTube clients
        sp = spotipy.Spotify(auth=spotify_token)
        youtube = build('youtube', 'v3', credentials=Credentials(token=youtube_token))

        # Get Spotify playlist details
        playlist = sp.playlist(spotify_playlist_id)
        playlist_name = playlist['name']
        playlist_description = playlist['description']
        playlist_image_url = playlist['images'][0]['url'] if playlist['images'] else None
        tracks = playlist['tracks']['items']
        
        # Fetch Spotify playlist details
        playlist = sp.playlist(spotify_playlist_id)
        playlist_name = playlist['name']
        tracks = playlist['tracks']['items']
        
        # Create YouTube playlist
        youtube_playlist = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": f"Spotify Import: {playlist_name}",
                    "description": f"Imported from Spotify playlist: {playlist_name}"
                },
                "status": {"privacyStatus": "private"}
            }
        ).execute()
        youtube_playlist_id = youtube_playlist['id']
        logger.info(f"Created YouTube playlist: {youtube_playlist_id}")
        
        # Transfer tracks
        for item in tracks:
            track = item['track']
            search_query = f"{track['name']} {' '.join([artist['name'] for artist in track['artists']])}"
            
            try:
                search_response = youtube.search().list(
                    q=search_query,
                    type="video",
                    part="id,snippet",
                    maxResults=1
                ).execute()
                
                if search_response['items']:
                    video_id = search_response['items'][0]['id']['videoId']
                    youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": youtube_playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    ).execute()
                    logger.info(f"Added video {video_id} to YouTube playlist")
                else:
                    logger.warning(f"No video found for: {search_query}")
            except HttpError as e:
                logger.error(f"Error adding video to playlist: {str(e)}")
        
        logger.info(f"Playlist transfer completed. YouTube playlist ID: {youtube_playlist_id}")

        try:
            Youtube_Playlist.objects.create(
                user=request.user,
                name=playlist_name,
                description=f"Imported from Spotify playlist: {playlist_name}",
                spotify_playlist_id=youtube_playlist_id,
                image_url=playlist_image_url
            )
            logger.info(f"Saved YouTube playlist info to database. Spotify playlist ID: {spotify_playlist_id}")
        except Exception as e:
            logger.error(f"Error saving playlist to database: {str(e)}")


        return redirect('youtube_playlists')
    
    except spotipy.SpotifyException as e:
        logger.error(f"Spotify API error: {str(e)}")
    except HttpError as e:
        logger.error(f"YouTube API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    
    return redirect("index")


def transfer_youtube_playlist_to_spotify(request, youtube_playlist_id):
    try:
        # Get access tokens using existing functions
        youtube_token = youtube_refresh_token(request)  # Assume this function exists
        spotify_token = spotify_refresh_token(request)  # Assume this function exists
        
        # Initialize YouTube and Spotify clients
        youtube = build('youtube', 'v3', credentials=Credentials(token=youtube_token))
        sp = spotipy.Spotify(auth=spotify_token)
        
        # Fetch YouTube playlist details
        playlist_response = youtube.playlists().list(
            part="snippet",
            id=youtube_playlist_id
        ).execute()
        
        if not playlist_response['items']:
            logger.error(f"YouTube playlist not found: {youtube_playlist_id}")
            return None
        
        playlist_title = playlist_response['items'][0]['snippet']['title']
        playlist_description = playlist_response['items'][0]['snippet']['description']
        
        # Create Spotify playlist
        user_id = sp.me()['id']
        spotify_playlist = sp.user_playlist_create(user_id, f"YouTube Import: {playlist_title}", public=False)
        spotify_playlist_id = spotify_playlist['id']
        logger.info(f"Created Spotify playlist: {spotify_playlist_id}")
        
        # Fetch YouTube playlist items
        playlist_items = []
        next_page_token = None
        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=youtube_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            playlist_items.extend(response['items'])
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        # Transfer tracks
        spotify_track_uris = []
        for item in playlist_items:
            video_title = item['snippet']['title']
            channel_title = item['snippet']['videoOwnerChannelTitle']
            search_query = f"{video_title} {channel_title}"
            
            try:
                results = sp.search(q=search_query, type='track', limit=1)
                if results['tracks']['items']:
                    track_uri = results['tracks']['items'][0]['uri']
                    spotify_track_uris.append(track_uri)
                    logger.info(f"Found Spotify track for: {search_query}")
                else:
                    logger.warning(f"No Spotify track found for: {search_query}")
            except SpotifyException as e:
                logger.error(f"Error searching Spotify: {str(e)}")
        
        # Add tracks to Spotify playlist in batches
        batch_size = 100
        for i in range(0, len(spotify_track_uris), batch_size):
            batch = spotify_track_uris[i:i+batch_size]
            sp.user_playlist_add_tracks(user_id, spotify_playlist_id, batch)
        
        logger.info(f"Playlist transfer completed. Spotify playlist ID: {spotify_playlist_id}")

        try:
            current_time = datetime.now()
            playlist_image_url = Spotify_Playlist['images'][0]['url'] if Spotify_Playlist['images'] else "/static/playlist/noimage.jpg"
            
            Youtube_Playlist.objects.create(
                user=request.user,
                name=playlist_title,
                description=playlist_description,
                youtube_playlist_id=spotify_playlist_id,
                image_url=playlist_image_url,
                created_at=current_time
            )
            logger.info(f"Saved Spotify playlist to database: {spotify_playlist_id}")
        except Exception as e:
            logger.error(f"Error saving playlist to database: {str(e)}")

        return redirect('playlist')
    
    except HttpError as e:
        logger.error(f"YouTube API error: {str(e)}")
    except SpotifyException as e:
        logger.error(f"Spotify API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    
    return redirect("index")



@login_required
def search_playlists(request):
    query = request.GET.get('query', '')
    access_token = spotify_refresh_token(request)
    
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            'https://api.spotify.com/v1/me/playlists',
            headers=headers,
            params={'limit': 50}
        )
        response.raise_for_status()
        
        playlists_data = response.json()['items']
        
        # Filter playlists based on search query
        filtered_playlists = [
            playlist for playlist in playlists_data
            if query.lower() in playlist['name'].lower()
        ]
        
        html = render_to_string('playlist/playlist_cards.html', {
            'playlists': filtered_playlists
        })
        
        return JsonResponse({
            'status': 'success',
            'html': html
        })
        
    except Exception as e:
        logger.error(f"Error searching Spotify playlists: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to search playlists'
        }, status=500)

@login_required
def youtube_search(request):
    query = request.GET.get('query', '')
    access_token = youtube_refresh_token(request)
    
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/playlists',
            headers=headers,
            params={
                'part': 'snippet,contentDetails',
                'mine': 'true',
                'maxResults': 50
            }
        )
        response.raise_for_status()
        
        playlists_data = response.json()['items']
        
        # Filter playlists based on search query
        filtered_playlists = [
            playlist for playlist in playlists_data
            if query.lower() in playlist['snippet']['title'].lower()
        ]
        
        html = render_to_string('playlist/youtube_card.html', {
            'playlists': filtered_playlists
        })
        
        return JsonResponse({
            'status': 'success',
            'html': html
        })
        
    except Exception as e:
        logger.error(f"Error searching YouTube playlists: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to search playlists'
        }, status=500)