{
  description = "OCF Jukebox Django Application";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;
      supportedSystems = [ "x86_64-linux" ];
      forSystems = lib.genAttrs supportedSystems;

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };

      editableOverlay = workspace.mkEditablePyprojectOverlay {
        root = "$REPO_ROOT";
      };

      pythonSets = forSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.python312;
        in
        (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope
          (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.wheel
              overlay
              (final: prev: {
                py-ubjson = prev.py-ubjson.overrideAttrs (old: {
                  nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ final.setuptools ];
                });
              })
            ]
          )
      );

    in
    {
      devShells = forSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet = pythonSets.${system}.overrideScope editableOverlay;
          virtualenv = pythonSet.mkVirtualEnv "jukebox-django-dev-env" (workspace.deps.all // { editables = [ ]; });
        in
        {
          default = pkgs.mkShell {
            packages = [
              virtualenv
              pkgs.uv
              pkgs.ffmpeg
              pkgs.portaudio
            ];
            env = {
              UV_NO_SYNC = "1";
              UV_PYTHON = pythonSet.python.interpreter;
              UV_PYTHON_DOWNLOADS = "never";
              # Required for just-playback to find libportaudio at runtime
              LD_LIBRARY_PATH = "${pkgs.portaudio}/lib";
            };
            shellHook = ''
              unset PYTHONPATH
              export REPO_ROOT=$(git rev-parse --show-toplevel)
              echo "Run: python manage.py runserver"
            '';
          };
        }
      );

      packages = forSystems (system: {
        default =
          let
            pkgs = nixpkgs.legacyPackages.${system};
            venv = pythonSets.${system}.mkVirtualEnv "jukebox-django-env" workspace.deps.default;
            src = ./.;

            # Collect static files during build
            staticfiles = pkgs.stdenv.mkDerivation {
              name = "jukebox-staticfiles";
              inherit src;
              nativeBuildInputs = [ venv ];
              buildPhase = ''
                export PYTHONPATH=$src
                export DJANGO_STATIC_ROOT=$out
                python -m django collectstatic --no-input --settings=config.settings
              '';
              installPhase = "true";
            };
          in
          pkgs.symlinkJoin {
            name = "jukebox-django";
            paths = [ venv ];
            nativeBuildInputs = [ pkgs.makeWrapper ];
            postBuild = ''
              wrapProgram $out/bin/daphne \
                --set PYTHONPATH "${src}" \
                --set DJANGO_STATIC_ROOT "${staticfiles}" \
                --set LD_LIBRARY_PATH "${pkgs.portaudio}/lib" \
                --prefix PATH : "${lib.makeBinPath [ pkgs.ffmpeg ]}"

              makeWrapper ${venv}/bin/python $out/bin/jukebox-manage \
                --add-flags "${src}/manage.py" \
                --set PYTHONPATH "${src}" \
                --set DJANGO_STATIC_ROOT "${staticfiles}" \
                --set LD_LIBRARY_PATH "${pkgs.portaudio}/lib" \
                --prefix PATH : "${lib.makeBinPath [ pkgs.ffmpeg ]}"
            '';
          };
      });

      apps = forSystems (system: {
        default = {
          type = "app";
          program =
            let
              pkgs = nixpkgs.legacyPackages.${system};
            in
            lib.getExe (
              pkgs.writeShellScriptBin "jukebox-server" ''
                exec ${self.packages.${system}.default}/bin/daphne config.asgi:application
              ''
            );
        };
      });
    };
}
