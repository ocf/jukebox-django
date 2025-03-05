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

        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
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
        ]);

        # Create a custom derivation for the jukebox app
        jukebox-django = pkgs.stdenv.mkDerivation {
          pname = "jukebox-django";
          version = "0.1.0";
          src = ./.;

          buildInputs = [
            pythonEnv
            pkgs.portaudio
          ];

          # No build phase, just install the files
          dontBuild = true;

          installPhase = ''
            mkdir -p $out/share/jukebox-django
            cp -r . $out/share/jukebox-django

            # Create a wrapper script to run the Django server
            mkdir -p $out/bin
            cat > $out/bin/jukebox-django-server << EOF
            #!/bin/sh
            cd $out/share/jukebox-django/jukebox
            ${pythonEnv}/bin/python manage.py runserver "\$@"
            EOF

            # Create a wrapper script to run the backend
            cat > $out/bin/jukebox-django-backend << EOF
            #!/bin/sh
            cd $out/share/jukebox-django/jukebox/backend
            ${pythonEnv}/bin/python main.py "\$@"
            EOF

            # Create a setup script
            cat > $out/bin/jukebox-django-setup << EOF
            #!/bin/sh
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              ${pythonEnv}/bin/python -m venv .venv
              . .venv/bin/activate
              pip install django-icons==24.4
            else
              . .venv/bin/activate
            fi
            EOF

            chmod +x $out/bin/jukebox-django-server
            chmod +x $out/bin/jukebox-django-backend
            chmod +x $out/bin/jukebox-django-setup
          '';

          # Ensure Python can find portaudio
          fixupPhase = ''
            wrapProgram $out/bin/jukebox-django-server \
              --prefix LD_LIBRARY_PATH : ${pkgs.portaudio}/lib \
              --prefix PYTHONPATH : $PYTHONPATH

            wrapProgram $out/bin/jukebox-django-backend \
              --prefix LD_LIBRARY_PATH : ${pkgs.portaudio}/lib \
              --prefix PYTHONPATH : $PYTHONPATH
          '';

          nativeBuildInputs = [ 
            pkgs.makeWrapper
          ];
        };
      in
      {
        packages = {
          default = jukebox-django;
          jukebox-django = jukebox-django;
        };

        devShells.default = pkgs.mkShell {
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
            ffmpeg
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
            echo "To run the backend server: cd jukebox/backend && python main.py"
            echo "To run the Django server: cd jukebox && python manage.py runserver"
          '';
        };
      });
} 
