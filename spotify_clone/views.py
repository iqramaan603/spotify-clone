from django.views.generic import TemplateView
from music.models import Song, Album
from playlists.models import Playlist

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_songs'] = Song.objects.filter(is_featured=True)[:4]
        context['featured_albums'] = Album.objects.filter(is_featured=True)[:4]
        context['featured_playlists'] = Playlist.objects.filter(is_public=True)[:4]
        return context 