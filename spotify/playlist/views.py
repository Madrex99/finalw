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

from .models import User
# Create your views here.

def home(request):
    return render(request, 'playlist/home.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been successfully logged in.')
            return render(request, 'playlist/index.html')
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

""""
def auth_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.success(request, ("There was an error logging in, try again..."))
                return redirect('auth')
        elif action == 'register':
            username = request.POST['register_username']
            email = request.POST['register_email']
            password = request.POST['register_password']
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except IntegrityError:
                messages.success(request, ("There was an error registering, try again..."))
                return redirect('login')
            login(request, user)
            messages.success(request, ("Registration Successful!"))
            return render(request, 'playlist/index.html')
    
    else:
        return render(request, 'playlist/login.html')
"""