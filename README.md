# Jukebox

A Django-based music player for the OCF. Submit YouTube URLs to play music through the server.

## Getting Started

### Option 1: Using uv

Requirements:
- Python 3.12
- [uv](https://github.com/astral-sh/uv)
- FFmpeg (for audio processing)

For dev
```bash
git clone https://github.com/ocf/jukebox-django
cd jukebox-django
uv run python manage.py migrate
uv run python manage.py collectstatic
uv run python manage.py runserver
```
For prod
```bash
git clone https://github.com/ocf/jukebox-django
cd jukebox-django
uv run python manage.py migrate
uv run python manage.py collectstatic
uv run daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

Go to `http://127.0.0.1:8000/` to access the jukebox.

### Option 2: Using Nix

```bash
nix develop
python manage.py runserver
```

Or run:

```bash
nix run github:ocf/jukebox-django
```

## Project Structure

```
jukebox-django/
├── manage.py           # Django management script
├── config/             # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py         # ASGI config with WebSocket routing
├── jukebox/            # Main application
│   ├── views.py        # Dashboard view
│   ├── consumers.py    # WebSocket handler
│   ├── controller.py   # Audio playback controller
│   ├── lyrics.py       # Lyrics fetching
│   ├── templates/      # HTML templates
│   └── static/         # CSS, JS, images
└── pyproject.toml
```

## How It Works

1. User submits a YouTube URL via the web interface
2. The URL is sent to the server via WebSocket
3. `yt-dlp` downloads the audio
4. `just-playback` plays the audio on the server
5. Real-time updates (now playing, queue, lyrics) are pushed to all connected clients
