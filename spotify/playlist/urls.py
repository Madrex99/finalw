from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_view, name='register'),
    path('signout/', views.signout_user, name='signout'),
    path('spotify_login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('youtube/callback/', views.youtube_callback, name='youtube_callback'),
    path('youtube_login/', views.youtube_login, name='youtube_login'),
]
