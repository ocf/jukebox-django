# Jukebox

A Django-based music player for the OCF. Submit YouTube URLs to play music through the server.

## Getting Started

### Option 1: Using UV

Requirements:
- Python 3.12
- [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/ocf/jukebox-django
cd jukebox-django
uv run python manage.py runserver
```

Go to `http://127.0.0.1:8000/` to access the jukebox.

### Option 2: Using Nix

```bash
nix develop
uv run python manage.py runserver
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