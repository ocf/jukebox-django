# New Jukebox

Jukebox rewrite with Django - currently newstaff project Fa24

## Getting started

### Option 1: Using Poetry (Standard method)

Requirements:

- Python 3.10-3.12
- [Poetry](https://python-poetry.org/)

Clone this repo and enter it:

```
git clone https://github.com/ocf/jukebox-django
cd jukebox-django
```

Install dependencies:

```
poetry install
```

Activate the Poetry environment:

```
poetry shell
```

### Option 2: Using Nix (Recommended for NixOS deployments)

This project includes Nix support for reproducible environments with all dependencies, including system libraries like PortAudio which PyAudio requires.

Requirements:
- Nix package manager (https://nixos.org/download.html)

#### With flakes enabled:

```bash
# Development shell
nix develop

# Build the package
nix build
```

#### Without flakes:

```bash
# Development shell
nix-shell
```

The Nix configuration automatically creates a Python virtual environment (.venv) and installs all required packages, including those not available in nixpkgs.

## Running the project

#### Starting the Server

Enter the `backend` directory, then run `runner.py`:

```
cd backend/
python3 runner.py
```

#### Starting the Website

Enter the `jukebox` directory, and run the project:

```
cd jukebox/
python manage.py runserver
```

Go to `http://127.0.0.1:8000/YTUSRN/` to access the website.

## Deployment on NixOS

To deploy this application on a NixOS system, you can import the flake directly in your NixOS configuration:

```nix
{
  inputs.jukebox-django.url = "github:ocf/jukebox-django";
  
  outputs = { self, nixpkgs, jukebox-django, ... }: {
    nixosConfigurations.yourSystem = nixpkgs.lib.nixosSystem {
      # ...
      modules = [
        # ...
        ({ pkgs, ... }: {
          environment.systemPackages = [
            jukebox-django.packages.${pkgs.system}.default
          ];
        })
      ];
    };
  };
}
```