{
  description = "OCF Jukebox Django Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonPackages = pkgs.python311Packages;

        jukebox-django = pythonPackages.buildPythonApplication {
          pname = "jukebox-django";
          version = "0.1.0";
          format = "pyproject";

          src = ./.;

          nativeBuildInputs = [
            pythonPackages.poetry-core
          ];

          propagatedBuildInputs = with pythonPackages; [
            django
            yt-dlp
            jsonpickle
            wheel
            pyaudio
            websockets
            aioconsole
            django-icons
            channels
            daphne
            portaudio  # System dependency for pyaudio
          ];

          # Make sure Python can find portaudio
          makeWrapperArgs = [
            "--prefix LD_LIBRARY_PATH : ${pkgs.portaudio}/lib"
          ];

          # Skip tests during build
          doCheck = false;
        };
      in
      {
        packages = {
          default = jukebox-django;
          jukebox-django = jukebox-django;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            python311Packages.poetry
            portaudio
          ];

          shellHook = ''
            # Set up environment variables if needed
            export PYTHONPATH=$PWD:$PYTHONPATH
            
            # Note for users
            echo "Nix development environment for jukebox-django"
            echo "To run the backend server: cd jukebox/backend && python runner.py"
            echo "To run the Django server: cd jukebox && python manage.py runserver"
          '';
        };
      });
} 