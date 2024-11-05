import requests
import base64
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
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

from .models import User, SpotifyToken, YoutubeToken
# Create your views here.

def home(request):
    return render(request, 'playlist/home.html')

@login_required(login_url='login')
def index(request):
    sp(request)
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
        print("Error response from Spotify:", response.text)
        messages.error(request, "Failed to authenticate with Spotify")
        return redirect('index')

    token_info = response.json()
    
    # Debug print
    print("Spotify response:", token_info)
    
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
        request.session['access_token']['spotify'] = access_token
        request.session['expires_at']['spotify'] = token_expires_at.isoformat()
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
        print(f"KeyError: {str(e)} not found in response")
        print("Full response:", token_info)
        messages.error(request, "Invalid response from Spotify")
        return redirect('index')


@login_required(login_url='login')
def spotify_refresh_token(request):
    # Check if access token is still valid
    access_token = request.session.get('access_token', {}).get('spotify')
    expires_at = request.session.get('expires_at', {}).get('spotify')

    if access_token and expires_at and now() < expires_at:
        print(access_token)
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
        print(f"Error refreshing token: {response.json()}")
        
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
    request.session['access_token']['spotify'] = new_access_token
    request.session['expires_at']['spotify'] = expires_at.isoformat()
    print(new_access_token)

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
    request.session['access_token']['youtube'] = access_token
    request.session['expires_at']['youtube'] = expires_at.timestamp()

    # Save refresh token in database
    user = request.user
    print(f"refresh_token {refresh_token}")
    print(f"expires_at {expires_at}")
    print(f"access_token {access_token}")
    if refresh_token:
        YoutubeToken.objects.update_or_create(
            user=user,
            defaults={
                'refresh_token': refresh_token,
            }
        )

    return redirect('index')


@login_required(login_url='login')
def youtube_refresh_token(request):
    user = request.user
    access_token = request.session.get('access_token')['youtube']
    expires_at = request.session.get('expires_at')['youtube']

    user_tokens = YoutubeToken.objects.get(user=user)

    if access_token and expires_at and now() < expires_at:
        return access_token
    
    credentials = Credentials(
        access_token,
        refresh_token=user_tokens.refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.YOUTUBE_CLIENT_ID,
        client_secret=settings.YOUTUBE_CLIENT_SECRET,
    )

    # refresh the token if expired
    if credentials.expired: 
        credentials.refresh(Request())
        # update access token in session
        request.session['access_token']['youtube'] = credentials.token
        request.session['expires_at']['youtube'] = str(datetime.now() + timedelta(seconds=credentials.expiry))

    return credentials.token

#==========================================
# playlists
#==========================================
"""def playlist(request):
    access_token = spotify_refresh_token(request)
    headers = {
        'Authorization': f"Bearer {access_token}"
    }

    playlist_url = 'https://api.spotify.com/v1/me/playlists'
    response = requests.get(playlist_url, headers=headers)

    if response.status_code == 200:
        playlists_data = response.json().get('items', [])
"""

def sp(request):
    spotify_refresh_token(request)

