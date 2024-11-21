from django.contrib import admin
from .models import User, Spotify_Playlist, Youtube_Playlist, SpotifyToken, YoutubeToken
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(User)
admin.site.register(Spotify_Playlist)
admin.site.register(Youtube_Playlist)
admin.site.register(SpotifyToken)
admin.site.register(YoutubeToken)
