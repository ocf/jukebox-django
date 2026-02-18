# Jukebox

A Django-based music player for the OCF. Submit YouTube URLs to play music through the server.

## Getting Started

### Option 1: Using Poetry

Requirements:
- Python 3.10-3.12
- [Poetry](https://python-poetry.org/)
- FFmpeg (for audio processing)

```bash
git clone https://github.com/ocf/jukebox-django
cd jukebox-django
poetry install
poetry run python manage.py runserver
```

Go to `http://127.0.0.1:8000/` to access the jukebox.

### Option 2: Using Nix

```bash
nix develop
python manage.py runserver
```

Or run:

```bash
nix run github.com/ocf/jukebox-django
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

## Deployment on NixOS

```nix
{
  inputs.jukebox-django.url = "github:ocf/jukebox-django";
  
  outputs = { self, nixpkgs, jukebox-django, ... }: {
    nixosConfigurations.yourSystem = nixpkgs.lib.nixosSystem {
      modules = [
        ({ pkgs, ... }: {
          systemd.services.jukebox = {
            description = "Jukebox Service";
            wantedBy = [ "multi-user.target" ];
            after = [ "network.target" ];
            serviceConfig = {
              ExecStart = "${jukebox-django.packages.${pkgs.system}.default}/bin/jukebox-django 8000";
              Restart = "always";
            };
          };
        })
      ];
    };
  };
}
```