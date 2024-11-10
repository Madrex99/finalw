from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_view, name='register'),
    path('signout/', views.signout_user, name='signout'),
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('youtube/callback/', views.youtube_callback, name='youtube_callback'),
    path('youtube/login/', views.youtube_login, name='youtube_login'),
    path('playlist/', views.playlist, name="playlist"),
    path('youtube_playlists', views.youtube_playlist, name="youtube_playlists"),
    path('youtube/<str:spotify_playlist_id>', views.transfer_spotify_playlist_to_youtube, name="sp_to_yt")
]
