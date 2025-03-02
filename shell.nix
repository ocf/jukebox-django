# shell.nix - For compatibility with older Nix installations
# Use this with: nix-shell

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    (python311.withPackages (ps: with ps; [
      django
      yt-dlp
      jsonpickle
      wheel
      pyaudio
      websockets
      aioconsole
      channels
      daphne
      pip
    ]))
    portaudio
  ];

  shellHook = ''
    # Set up environment variables if needed
    export PYTHONPATH=$PWD:$PYTHONPATH
    
    # Use the portaudio library
    export LD_LIBRARY_PATH=${pkgs.portaudio}/lib:$LD_LIBRARY_PATH
    
    # Note for users
    echo "Nix development environment for jukebox-django activated!"
    echo "To run the backend server: python jukebox/backend/runner.py"
    echo "To run the Django server: cd jukebox && python manage.py runserver"
  '';
} 