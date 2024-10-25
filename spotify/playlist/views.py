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

from .models import User
# Create your views here.

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

def spotify_login(request):
    spotify_auth_url = 'https://accounts.spotify.com/authorize'
    spotify_client_id = settings.SPOTIFY_CLIENT_ID
    spotify_redirect_uri = settings.SPOTIFY_REDIRECT_URI
    scope = 'user-library-read playlist-read-private playlist-modify-public playlist-modify-private user-library-modify'

    # redirect user to spotify's authorization page
    auth_url = f"{spotify_auth_url}?client_id={spotify_client_id}&response_type=code&redirect_uri={spotify_redirect_uri}&scope={scope}"
    return redirect(auth_url)

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
    token_info = response.json()
    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']
    token_expires_in = token_info['expires_in']

    #save info to database
    expires_at = datetime.now() + timedelta(seconds = token_expires_in)
    

    return redirect('index')
