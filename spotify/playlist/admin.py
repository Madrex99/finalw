from django.contrib import admin
from .models import User, Playlist
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(User)
admin.site.register(Playlist)
