{
  description = "OCF Jukebox Django Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    uv2nix.url = "github:pyproject-nix/uv2nix";
  };

  outputs = { self, nixpkgs, pyproject-nix, uv2nix, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};

      workspace = uv2nix.lib.${system}.loadWorkspace {
        src = ./.;
      };

      pythonEnv = pyproject-nix.lib.${system}.mkPythonApplication {
        inherit (workspace) name version src;
        pyproject = workspace.pyproject;
        lockFile = workspace.lockFile;
        python = pkgs.python312;
      };

    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pythonEnv
          pkgs.uv
          pkgs.ffmpeg
          pkgs.portaudio
        ];

        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.portaudio}/lib:$LD_LIBRARY_PATH"
          echo "Run: python manage.py runserver"
        '';
      };
    };
}
