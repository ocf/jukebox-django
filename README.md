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

The build process produces the following executables:

- `result/bin/jukebox-django-server` - Run the Django web server
- `result/bin/jukebox-django-backend` - Run the backend server
- `result/bin/jukebox-django-setup` - Setup a virtual environment with missing packages

#### Without flakes:

```bash
# Development shell
nix-shell
```

The Nix configuration automatically creates a Python virtual environment (.venv) and installs all required packages, including those not available in nixpkgs.

## Running the project

#### Starting the Server

Enter the `backend` directory, then run `main.py`:

```
cd backend/
python3 main.py
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
          
          # Optional: Create a systemd service for the backend server
          systemd.services.jukebox-backend = {
            description = "Jukebox Backend Service";
            wantedBy = [ "multi-user.target" ];
            after = [ "network.target" ];
            serviceConfig = {
              ExecStart = "${jukebox-django.packages.${pkgs.system}.default}/bin/jukebox-django-backend";
              Restart = "always";
              User = "jukebox";
              Group = "jukebox";
            };
          };
          
          # Optional: Create a systemd service for the Django server
          systemd.services.jukebox-server = {
            description = "Jukebox Django Web Service";
            wantedBy = [ "multi-user.target" ];
            after = [ "network.target" ];
            serviceConfig = {
              ExecStart = "${jukebox-django.packages.${pkgs.system}.default}/bin/jukebox-django-server 0.0.0.0:8000";
              Restart = "always";
              User = "jukebox";
              Group = "jukebox";
            };
          };
        })
      ];
    };
  };
}
```