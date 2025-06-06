from django.db import models
from django.contrib.auth.models import AbstractUser
from cryptography.fernet import Fernet
from django.conf import settings
# Create your models here.

class User(AbstractUser):
    pass

class SpotifyToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Spotify Token"

    def encypt(token):
        fernet = Fernet(settings.ENCRYPTION_KEY)
        encrypted_token = fernet.encrypt(token.encode()).decode()
        return encrypted_token
    
    def decrypt(encrypted_token):
        fernet = Fernet(settings.ENCRYPTION_KEY)
        decrypted_token = fernet.decrypt(encrypted_token).decode()
        return decrypted_token

class Spotify_Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    spotify_playlist_id = models.CharField(max_length=255, unique=True, null=True)
    image_url = models.URLField(default="/static/playlist/noimage.jpg")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class YoutubeToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s YouTube Token"
    

class Youtube_Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    youtube_playlist_id = models.CharField(max_length=255, unique=True, null=True)
    image_url = models.URLField(default="/static/playlist/noimage.jpg")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name