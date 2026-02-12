{
  description = "OCF Jukebox Django Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    uv2nix.url = "github:pyproject-nix/uv2nix";
    uv2nix.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";
    pyproject-build-systems.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-build-systems.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, pyproject-nix, uv2nix, pyproject-build-systems, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python312;

      workspace = uv2nix.lib.workspace.loadWorkspace {
        src = ./.;
      };

      overlay = workspace.mkPyprojectOverlay {
        inherit pkgs;
      };

      pythonSet = (pkgs.callPackage pyproject-nix.buildHelpers.packages {
        inherit python;
      }).overrideScope (
        pkgs.lib.composeManyExtensions [
          pyproject-nix.pythonPackagesMatchers.default
          overlay
          pyproject-build-systems.overlays.default
          (final: prev: {
            # Add overrides here if needed
            just-playback = prev.just-playback.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ pkgs.portaudio ];
            });
          })
        ]
      );

      env = pythonSet.withPackages (ps: [
        ps.jukebox-django
      ]);
    in
    {
      packages.${system}.default = env;

      devShells.${system}.default = pkgs.mkShell {
        packages = [
          env
          pkgs.uv
          pkgs.ffmpeg
          pkgs.portaudio
        ];

        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.portaudio}/lib:$LD_LIBRARY_PATH"
          echo "Jukebox Django Dev Shell (x86_64-linux)"
          echo "Python: $(python --version)"
        '';
      };
    };
}
