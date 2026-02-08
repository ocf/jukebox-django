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
          just-playback
          channels
          daphne
          pip
        ]);

        jukebox-django = pkgs.stdenv.mkDerivation {
          pname = "jukebox-django";
          version = "0.1.0";
          src = ./.;

          buildInputs = [
            pythonEnv
            pkgs.portaudio
          ];

          dontBuild = true;

          installPhase = ''
            mkdir -p $out/share/jukebox-django
            cp -r . $out/share/jukebox-django

            mkdir -p $out/bin

            # Single server script using Daphne (ASGI)
            cat > $out/bin/jukebox-django << EOF
            #!/bin/sh
            cd $out/share/jukebox-django
            ${pythonEnv}/bin/daphne -b 0.0.0.0 -p "\''${1:-8000}" config.asgi:application
            EOF

            chmod +x $out/bin/jukebox-django
          '';

          fixupPhase = ''
            wrapProgram $out/bin/jukebox-django \
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
              just-playback
              channels
              daphne
              pip
            ]))
            portaudio
            ffmpeg
          ];

          shellHook = ''
            export PYTHONPATH=$PWD:$PYTHONPATH
            export LD_LIBRARY_PATH=${pkgs.portaudio}/lib:$LD_LIBRARY_PATH
            
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              python -m venv .venv
              . .venv/bin/activate
              pip install django-icons==24.4
            else
              . .venv/bin/activate
            fi
            
            echo "Jukebox development environment ready!"
            echo "Run: python manage.py runserver"
          '';
        };
      });
} 
