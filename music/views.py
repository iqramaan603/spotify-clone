from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Album, Song, Genre, LikedSong, ListeningHistory, PlayCount
from .forms import AlbumForm, SongForm, GenreForm
from random import choice

def song_list(request):
    query = request.GET.get('q', '')
    genre_id = request.GET.get('genre')
    
    songs = Song.objects.select_related('artist', 'album', 'genre').all()
    
    if query:
        songs = songs.filter(
            Q(title__icontains=query) |
            Q(artist__username__icontains=query) |
            Q(album__title__icontains=query)
        )
    
    if genre_id:
        try:
            genre_id = int(genre_id)
            songs = songs.filter(genre_id=genre_id)
        except (ValueError, TypeError):
            pass
    
    paginator = Paginator(songs, 20)
    page = request.GET.get('page')
    songs = paginator.get_page(page)
    
    genres = Genre.objects.all().order_by('name')
    
    return render(request, 'music/song_list.html', {
        'songs': songs,
        'genres': genres,
        'selected_genre': genre_id
    })

def song_detail(request, song_id):
    song = get_object_or_404(Song.objects.select_related('artist', 'album', 'genre'), id=song_id)
    is_liked = request.user.is_authenticated and LikedSong.objects.filter(user=request.user, song=song).exists()
    
    return render(request, 'music/song_detail.html', {
        'song': song,
        'is_liked': is_liked
    })

@login_required
def upload_song(request):
    if not request.user.is_artist:
        messages.error(request, 'Only artists can upload songs.')
        return redirect('music:song_list')
    
    if request.method == 'POST':
        form = SongForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.artist = request.user
            song.save()
            messages.success(request, 'Song uploaded successfully!')
            return redirect('music:song_detail', song_id=song.id)
    else:
        form = SongForm(request.user)
    
    return render(request, 'music/upload_song.html', {'form': form})

@login_required
def edit_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    
    if request.user != song.artist:
        messages.error(request, 'You can only edit your own songs.')
        return redirect('music:song_detail', song_id=song.id)
    
    if request.method == 'POST':
        form = SongForm(request.user, request.POST, request.FILES, instance=song)
        if form.is_valid():
            form.save()
            messages.success(request, 'Song updated successfully!')
            return redirect('music:song_detail', song_id=song.id)
    else:
        form = SongForm(request.user, instance=song)
    
    return render(request, 'music/edit_song.html', {'form': form, 'song': song})

@login_required
def create_album(request):
    if not request.user.is_artist:
        messages.error(request, 'Only artists can create albums.')
        return redirect('music:album_list')
    
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save(commit=False)
            album.artist = request.user
            album.save()
            messages.success(request, 'Album created successfully!')
            return redirect('music:album_detail', album_id=album.id)
    else:
        form = AlbumForm()
    
    return render(request, 'music/create_album.html', {'form': form})

def album_list(request):
    albums = Album.objects.select_related('artist', 'genre').all()
    
    # Handle search
    query = request.GET.get('q')
    if query:
        albums = albums.filter(
            Q(title__icontains=query) |
            Q(artist__username__icontains=query)
        )
    
    # Handle genre filter
    genre_id = request.GET.get('genre')
    if genre_id:
        try:
            genre_id = int(genre_id)
            albums = albums.filter(genre_id=genre_id)
        except (ValueError, TypeError):
            pass
    
    # Get all genres for the filter dropdown
    genres = Genre.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(albums, 12)
    page = request.GET.get('page')
    albums = paginator.get_page(page)
    
    return render(request, 'music/album_list.html', {
        'albums': albums,
        'query': query,
        'genres': genres,
        'selected_genre': genre_id
    })

def album_detail(request, album_id):
    album = get_object_or_404(Album.objects.select_related('artist', 'genre'), id=album_id)
    songs = album.songs.select_related('genre').all()
    genres = Genre.objects.all().order_by('name')
    
    # Get other albums by the same artist with genres
    other_albums = Album.objects.select_related('genre').filter(
        artist=album.artist
    ).exclude(id=album.id)[:4]
    
    return render(request, 'music/album_detail.html', {
        'album': album,
        'songs': songs,
        'genres': genres,
        'other_albums': other_albums,
        'selected_genre': None  # No genre selected in the sidebar for album detail
    })

@require_POST
def record_play(request, song_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    song = get_object_or_404(Song, id=song_id)
    
    # Record the play
    PlayCount.objects.create(song=song, user=request.user)
    
    # Update song's play count
    song.total_plays = song.playcount_set.count()
    song.save()
    
    return JsonResponse({
        'status': 'success',
        'play_count': song.total_plays
    })

@require_POST
@login_required
def toggle_like(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    
    if request.user in song.likes.all():
        song.likes.remove(request.user)
        is_liked = False
    else:
        song.likes.add(request.user)
        is_liked = True
    
    return JsonResponse({
        'status': 'success',
        'is_liked': is_liked,
        'likes_count': song.likes.count()
    })

def get_random_song(request):
    songs = Song.objects.all()
    if songs.exists():
        random_song = choice(list(songs))
        return JsonResponse({
            'id': random_song.id,
            'title': random_song.title,
            'artist': random_song.artist.get_display_name(),
            'url': random_song.audio_file.url,
            'image': random_song.cover_image.url if random_song.cover_image else (
                random_song.album.cover_image.url if random_song.album and random_song.album.cover_image else None
            )
        })
    return JsonResponse({'error': 'No songs found'}, status=404)

def search_songs(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'songs': []})
    
    songs = Song.objects.select_related('artist', 'album').filter(
        Q(title__icontains=query) |
        Q(artist__username__icontains=query) |
        Q(album__title__icontains=query)
    )[:10]  # Limit to 10 results for performance
    
    results = []
    for song in songs:
        song_data = {
            'id': song.id,
            'title': song.title,
            'artist': song.artist.get_display_name(),
            'image': song.cover_image.url if song.cover_image else (
                song.album.cover_image.url if song.album and song.album.cover_image else None
            )
        }
        results.append(song_data)
    
    return JsonResponse({'songs': results})
