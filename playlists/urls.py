from django.urls import path
from . import views

app_name = 'playlists'

urlpatterns = [
    path('', views.playlist_list, name='playlist_list'),
    path('create/', views.create_playlist, name='create_playlist'),
    path('<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('<int:pk>/edit/', views.edit_playlist, name='edit_playlist'),
    path('<int:pk>/delete/', views.delete_playlist, name='delete_playlist'),
    path('<int:pk>/add-song/', views.add_song_to_playlist, name='add_song'),
    path('<int:pk>/remove-song/<int:song_id>/', views.remove_song_from_playlist, name='remove_song'),
    path('<int:pk>/reorder/', views.reorder_playlist, name='reorder_playlist'),
    path('<int:pk>/follow/', views.toggle_follow_playlist, name='follow_playlist'),
    path('add-song/', views.choose_playlist, name='choose_playlist'),
] 