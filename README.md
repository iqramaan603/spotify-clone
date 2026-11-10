# Spotify Clone (Django)

A music streaming web app inspired by Spotify, built with Django. Users can sign up, upload songs and albums, browse music, and build their own playlists.

## Features

- Sign up and log in with email (django-allauth), with email verification and password reset
- User and artist dashboards, plus profile pages
- Upload songs and create albums with cover images
- Browse albums and songs by genre
- Create, edit and delete playlists, and add songs to them
- Built-in music player with audio playback
- REST API with filtering, search and pagination (Django REST Framework)
- Secrets kept out of the code using a `.env` file

## Tech stack

- Python and Django 5.2
- Django REST Framework, django-filter, django-cors-headers
- django-allauth, django-crispy-forms (Bootstrap 5)
- SQLite database
- HTML, CSS and JavaScript

## Screenshots

<!-- Add screenshots here later, for example: -->
<!-- ![Home page](screenshots/home.png) -->

## How to run it on your computer

1. Install Python 3.12 or newer.

2. Download the project and open a terminal in its folder (the one with `manage.py`).

3. Install the libraries:

   ```
   pip install -r requirements.txt
   ```

4. Create a file named `.env` next to `manage.py` and add:

   ```
   SECRET_KEY=put-any-long-random-text-here
   DEBUG=True
   ```

   `DEBUG=True` is needed to run the app locally over http.

5. Set up the database:

   ```
   python manage.py migrate
   python manage.py create_default_genres
   ```

6. Start the server:

   ```
   python manage.py runserver
   ```

7. Open http://127.0.0.1:8000 in your browser.

**Note:** Email verification emails are printed in the terminal (not sent), so copy the verification link from there after signing up.

## About the songs

Songs are not included in this repository. Upload your own audio files through the app (Upload song page) after you create an account. Please only use music you have the right to use.

## Project structure

- `accounts/` users, login, profiles and dashboards
- `music/` songs, albums and genres
- `playlists/` playlists and the songs in them
- `templates/` HTML pages
- `static/js/` music player script
- `spotify_clone/` project settings

## Author

Iqra Maan, [GitHub](https://github.com/iqramaan603)