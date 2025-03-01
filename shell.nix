# shell.nix - For compatibility with older Nix installations
# Use this with: nix-shell

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.pip
    python311Packages.poetry-core
    portaudio
  ];

  shellHook = ''
    # Set up environment variables if needed
    export PYTHONPATH=$PWD:$PYTHONPATH
    
    # Use the portaudio library
    export LD_LIBRARY_PATH=${pkgs.portaudio}/lib:$LD_LIBRARY_PATH
    
    # Create a local virtual environment for pip packages
    if [ ! -d .venv ]; then
      echo "Creating virtual environment..."
      ${pkgs.python311}/bin/python -m venv .venv
      . .venv/bin/activate
      pip install django-icons==24.4
    else
      . .venv/bin/activate
    fi
    
    # Note for users
    echo "Nix development environment for jukebox-django activated!"
    echo "Virtual environment is active with all dependencies installed."
    echo "To run the backend server: cd jukebox/backend && python runner.py"
    echo "To run the Django server: cd jukebox && python manage.py runserver"
  '';
} 