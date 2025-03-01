# shell.nix - For compatibility with older Nix installations
# Use this with: nix-shell

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.poetry
    portaudio
  ];

  shellHook = ''
    # Set up environment variables if needed
    export PYTHONPATH=$PWD:$PYTHONPATH
    
    # Use the portaudio library
    export LD_LIBRARY_PATH=${pkgs.portaudio}/lib:$LD_LIBRARY_PATH
    
    # Note for users
    echo "Nix development environment for jukebox-django"
    echo "To run the backend server: cd jukebox/backend && python runner.py"
    echo "To run the Django server: cd jukebox && python manage.py runserver"
  '';
} 