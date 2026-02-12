{
  description = "OCF Jukebox Django Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
    };
  };

  outputs = { self, nixpkgs, pyproject-nix, uv2nix, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};

      workspace = uv2nix.lib.workspace.loadWorkspace {
        workspaceRoot = ./.;
      };

      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };

      pythonSet = (pkgs.callPackage pyproject-nix.buildPackages.pyproject-set {
        python = pkgs.python312;
      }).overrideScope overlay;

      virtualenv = pythonSet.mkVirtualEnv "jukebox-django-dev" workspace.deps.default;

    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          virtualenv
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
