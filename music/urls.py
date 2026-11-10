from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('songs/', views.song_list, name='song_list'),
    path('songs/<int:song_id>/', views.song_detail, name='song_detail'),
    path('songs/upload/', views.upload_song, name='upload_song'),
    path('songs/<int:song_id>/edit/', views.edit_song, name='edit_song'),
    path('songs/<int:song_id>/like/', views.toggle_like, name='toggle_like'),
    path('songs/<int:song_id>/play/', views.record_play, name='record_play'),
    path('songs/random/', views.get_random_song, name='random_song'),
    path('search/', views.search_songs, name='search_songs'),
    
    path('albums/', views.album_list, name='album_list'),
    path('albums/create/', views.create_album, name='create_album'),
    path('albums/<int:album_id>/', views.album_detail, name='album_detail'),
] 