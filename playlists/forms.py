from django import forms
from .models import Playlist

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'description', 'cover_image', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        } 