from django.contrib import admin
from .models import Genre, Album, Song, PlayCount, LikedSong, ListeningHistory

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'release_date', 'genre', 'song_count']
    list_filter = ['release_date', 'genre', 'is_featured']
    search_fields = ['title', 'artist__username']
    date_hierarchy = 'release_date'

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'album', 'genre', 'duration', 'total_plays', 'is_featured']
    list_filter = ['genre', 'is_explicit', 'is_featured']
    search_fields = ['title', 'artist__username', 'album__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['total_plays']
    fieldsets = [
        (None, {
            'fields': ['title', 'artist', 'album', 'genre']
        }),
        ('Media', {
            'fields': ['cover_image', 'audio_file', 'duration']
        }),
        ('Settings', {
            'fields': ['is_explicit', 'is_featured', 'total_plays']
        })
    ]

@admin.register(PlayCount)
class PlayCountAdmin(admin.ModelAdmin):
    list_display = ['song', 'user', 'played_at']
    list_filter = ['played_at']
    search_fields = ['song__title', 'user__username']
    date_hierarchy = 'played_at'

@admin.register(LikedSong)
class LikedSongAdmin(admin.ModelAdmin):
    list_display = ['user', 'song', 'liked_at']
    list_filter = ['liked_at']
    search_fields = ['song__title', 'user__username']
    date_hierarchy = 'liked_at'

@admin.register(ListeningHistory)
class ListeningHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'song', 'played_at', 'play_duration']
    list_filter = ['played_at']
    search_fields = ['song__title', 'user__username']
    date_hierarchy = 'played_at'
