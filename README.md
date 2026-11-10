# Spotify Clone

A full-stack Spotify-style web application built with Django.

## Features

- Custom User Authentication (Email-based)
- Profile Management
- Music Browsing & Search
- Playlist Management
- Music Upload (for Artists)
- Music Streaming & Playback
- Subscription Management
- Notifications & Alerts
- Admin Dashboard
- Analytics & Insights

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spotify-clone.git
cd spotify-clone
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root and add the following:
```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

For production deployment, make sure to:
- Set DEBUG=False
- Use a strong SECRET_KEY
- Configure proper ALLOWED_HOSTS
- Set up proper email settings
- Configure SSL/TLS certificates
- Set up proper CORS settings

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Visit http://127.0.0.1:8000 in your browser

## Project Structure

- `accounts/` - Custom user authentication and profile management
- `music/` - Music-related models and views (Artists, Albums, Songs)
- `playlists/` - Playlist management functionality

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 