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
            channels
            daphne
            pip  # Include pip for installing missing packages
          ] ++ [ pkgs.portaudio ];  # Add system dependency for pyaudio

          # Make sure Python can find portaudio and install missing packages
          makeWrapperArgs = [
            "--prefix LD_LIBRARY_PATH : ${pkgs.portaudio}/lib"
          ];

          # Skip tests during build
          doCheck = false;

          postInstall = ''
            # Create a wrapper script that installs missing packages in a local venv
            mkdir -p $out/bin
            cat > $out/bin/setup-jukebox << EOF
            #!/bin/sh
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              python -m venv .venv
              . .venv/bin/activate
              pip install django-icons==24.4
            else
              . .venv/bin/activate
            fi
            EOF
            chmod +x $out/bin/setup-jukebox
          '';
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
            (python311.withPackages (ps: with ps; [
              poetry-core
              pip
              venv
            ]))
            portaudio
          ];

          shellHook = ''
            # Set up environment variables if needed
            export PYTHONPATH=$PWD:$PYTHONPATH
            export LD_LIBRARY_PATH=${pkgs.portaudio}/lib:$LD_LIBRARY_PATH
            
            # Create a local virtual environment for pip packages
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              python -m venv .venv
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
        };
      });
} 