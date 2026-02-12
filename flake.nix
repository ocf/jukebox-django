{
  description = "OCF Jukebox Django Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python312
          pkgs.poetry
          pkgs.ffmpeg
          pkgs.portaudio
        ];

        shellHook = ''
          poetry env use python3.12

          if [ ! -d ".venv" ]; then
            echo "Initializing virtual environment..."
            poetry install
          fi

          # Required for just-playback to find libportaudio
          export LD_LIBRARY_PATH="${pkgs.portaudio}/lib:$LD_LIBRARY_PATH"
          
          echo "System: ${system}"
          echo "Python: $(python --version)"
          echo "Run: poetry run python manage.py runserver"
        '';
      };
    };
}
