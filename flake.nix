/**
 * ============================================================================
 * HANDMOUSE OS - NIX FLAKE ENVIRONMENT
 * ============================================================================
 * 
 * Ce fichier définit l'environnement de développement reproductible
 * via le gestionnaire de paquets Nix.
 * 
 * Pourquoi Nix ?
 * Le projet HandMouseOS dépend de nombreuses bibliothèques système 
 * (OpenCV, uinput, GLSL, Rust, Python, Go). Installer tout manuellement
 * sur chaque distribution Linux est complexe. Avec ce Flake, une simple commande 
 * 'nix develop' fournit instantanément tous les compilateurs et librairies.
 * 
 * OUTILS INCLUS :
 * - Compilateurs: GCC, Rust (Cargo), Go.
 * - IA Context: Python 3.10+, Mediapipe, OpenCV.
 * - Web Dev: TypeScript compiler.
 * - Automation: Just.
 * 
 * ----------------------------------------------------------------------------
 */

{
  description = "HandMouseOS - Système de contrôle gestuel par IA";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Environnement de compilation Rust
            cargo
            rustc
            rust-analyzer
            pkg-config
            
            # Moteur Python et IA
            python3
            python3Packages.pip
            python3Packages.opencv4
            python3Packages.numpy
            
            # Outils Système Go
            go
            
            # Développement Natif (C)
            gcc
            gnumake
            
            # Développement Web
            typescript
            
            # Outils de build modernes
            just
          ];

          shellHook = ''
            echo "--- Bienvenue dans l'environnement HandMouseOS ---"
            echo "Tous les langages sont chargés: Rust, Go, Python, C, TS"
          '';
        };
      });
}
