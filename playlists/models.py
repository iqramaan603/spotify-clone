from django.db import models
from django.conf import settings
from music.models import Song
from datetime import timedelta

class Playlist(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='playlist_covers/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playlists')
    songs = models.ManyToManyField(Song, through='PlaylistSong', related_name='playlists')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} by {self.user.get_display_name()}"

    @property
    def song_count(self):
        return self.songs.count()

    @property
    def total_duration(self):
        return sum((song.duration for song in self.songs.all()), start=timedelta())

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']
        unique_together = ['playlist', 'song']

    def __str__(self):
        return f"{self.song.title} in {self.playlist.title}"

class PlaylistFollow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'playlist']

    def __str__(self):
        return f"{self.user.get_display_name()} follows {self.playlist.title}"
