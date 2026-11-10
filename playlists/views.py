from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .models import Playlist, PlaylistSong, PlaylistFollow
from music.models import Song
from .forms import PlaylistForm

@login_required
def playlist_list(request):
    user_playlists = request.user.playlists.all()
    followed_playlists = Playlist.objects.filter(followers__user=request.user)
    public_playlists = Playlist.objects.filter(is_public=True).exclude(user=request.user)
    
    return render(request, 'playlists/playlist_list.html', {
        'user_playlists': user_playlists,
        'followed_playlists': followed_playlists,
        'public_playlists': public_playlists
    })

@login_required
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST, request.FILES)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            messages.success(request, 'Playlist created successfully!')
            return redirect('playlists:playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm()
    
    return render(request, 'playlists/create_playlist.html', {'form': form})

def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    songs = PlaylistSong.objects.filter(playlist=playlist).select_related('song', 'song__artist')
    is_following = request.user.is_authenticated and playlist.followers.filter(user=request.user).exists()
    
    return render(request, 'playlists/playlist_detail.html', {
        'playlist': playlist,
        'songs': songs,
        'is_following': is_following
    })

@login_required
def edit_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PlaylistForm(request.POST, request.FILES, instance=playlist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Playlist updated successfully!')
            return redirect('playlists:playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm(instance=playlist)
    
    return render(request, 'playlists/edit_playlist.html', {
        'form': form,
        'playlist': playlist
    })

@login_required
def delete_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        playlist.delete()
        messages.success(request, 'Playlist deleted successfully!')
        return redirect('playlists:playlist_list')
    
    return render(request, 'playlists/delete_playlist.html', {'playlist': playlist})

@login_required
def add_song_to_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        song_ids = request.POST.getlist('songs')
        position = PlaylistSong.objects.filter(playlist=playlist).count()
        
        for song_id in song_ids:
            song = get_object_or_404(Song, id=song_id)
            PlaylistSong.objects.get_or_create(
                playlist=playlist,
                song=song,
                defaults={'position': position}
            )
            position += 1
        
        messages.success(request, 'Songs added to playlist successfully!')
        return redirect('playlists:playlist_detail', pk=playlist.pk)
    
    # Get songs not in the playlist
    existing_song_ids = PlaylistSong.objects.filter(playlist=playlist).values_list('song_id', flat=True)
    available_songs = Song.objects.exclude(id__in=existing_song_ids)
    
    return render(request, 'playlists/add_song.html', {
        'playlist': playlist,
        'available_songs': available_songs
    })

@login_required
def remove_song_from_playlist(request, pk, song_id):
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    playlist_song = get_object_or_404(PlaylistSong, playlist=playlist, song_id=song_id)
    
    if request.method == 'POST':
        playlist_song.delete()
        messages.success(request, 'Song removed from playlist successfully!')
    
    return redirect('playlists:playlist_detail', pk=playlist.pk)

@login_required
def reorder_playlist(request, pk):
    if request.method == 'POST':
        playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
        positions = request.POST.getlist('positions[]')
        
        with transaction.atomic():
            for index, song_id in enumerate(positions):
                PlaylistSong.objects.filter(
                    playlist=playlist,
                    song_id=song_id
                ).update(position=index)
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def toggle_follow_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    
    if request.user == playlist.user:
        messages.error(request, "You can't follow your own playlist.")
        return redirect('playlists:playlist_detail', pk=playlist.pk)
    
    if request.method == 'POST':
        if playlist.followers.filter(user=request.user).exists():
            playlist.followers.filter(user=request.user).delete()
            messages.success(request, f'Unfollowed {playlist.title}')
        else:
            playlist.followers.create(user=request.user)
            messages.success(request, f'Following {playlist.title}')
    
    return redirect('playlists:playlist_detail', pk=playlist.pk)

@login_required
def choose_playlist(request):
    song_id = request.GET.get('song')
    if not song_id:
        messages.error(request, 'No song specified.')
        return redirect('music:song_list')
    
    song = get_object_or_404(Song, id=song_id)
    user_playlists = request.user.playlists.all()
    
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist')
        if playlist_id:
            playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
            position = PlaylistSong.objects.filter(playlist=playlist).count()
            
            # Check if song already exists in playlist
            if not PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                PlaylistSong.objects.create(
                    playlist=playlist,
                    song=song,
                    position=position
                )
                messages.success(request, f'Added "{song.title}" to "{playlist.title}"')
            else:
                messages.info(request, 'Song already exists in this playlist.')
            
            return redirect('playlists:playlist_detail', pk=playlist.id)
        else:
            messages.error(request, 'Please select a playlist.')
    
    return render(request, 'playlists/choose_playlist.html', {
        'song': song,
        'playlists': user_playlists
    })
