# New Jukebox

Jukebox rewrite with Django - currently newstaff project Fa24

## Getting started

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

## Using Nix (recommended for NixOS deployments)

This project includes Nix flake support for reproducible environments with all dependencies:

### With flakes enabled:

```
# Development shell
nix develop

# Build the package
nix build
```

### Without flakes:

```
# Development shell
nix-shell
```

The Nix configuration automatically handles all dependencies, including system libraries like PortAudio which PyAudio requires.

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