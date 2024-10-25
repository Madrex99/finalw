from django.db import models
from django.contrib.auth.models import AbstractUser
from cryptography.fernet import Fernet
from django.conf import settings
# Create your models here.

class User(AbstractUser):
    pass

class SpotifyToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)

    def encypt(token):
        fernet = Fernet(settings.ENCRYPTION_KEY)
        encrypted_token = fernet.encrypt(token.encode()).decode()
        return encrypted_token
    
    def decrypt(encrypted_token):
        fernet = Fernet(settings.ENCRYPTION_KEY)
        decrypted_token = fernet.decrypt(encrypted_token).decode()
        return decrypted_token

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
