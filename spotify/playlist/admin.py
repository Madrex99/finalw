from django.contrib import admin
from .models import User, Playlist, SpotifyToken, YoutubeToken
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(User)
admin.site.register(Playlist)
admin.site.register(SpotifyToken)
admin.site.register(YoutubeToken)
