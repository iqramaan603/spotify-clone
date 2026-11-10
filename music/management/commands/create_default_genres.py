from django.core.management.base import BaseCommand
from music.models import Genre

class Command(BaseCommand):
    help = 'Creates default music genres if they do not exist'

    def handle(self, *args, **kwargs):
        default_genres = [
            'Pop',
            'Rock',
            'Hip Hop',
            'R&B',
            'Jazz',
            'Classical',
            'Electronic',
            'Country',
            'Folk',
            'Blues',
            'Metal',
            'Reggae',
            'Latin',
            'Alternative',
            'Indie'
        ]

        created_count = 0
        for genre_name in default_genres:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created genre: {genre_name}'))

        if created_count == 0:
            self.stdout.write(self.style.SUCCESS('All default genres already exist.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} new genres.')) 