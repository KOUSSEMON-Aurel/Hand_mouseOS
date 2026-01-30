#!/bin/bash
# Hand Mouse OS - Independent Portable Build Script
# Génère des exécutables autonomes minimisant les dépendances système.

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Hand Mouse OS Independent Portable Build ===${NC}"

# Dossier de sortie
DIST_ROOT="dist"
rm -rf "$DIST_ROOT"
mkdir -p "$DIST_ROOT/linux"
mkdir -p "$DIST_ROOT/windows"

# 1. Compilation Go CLI (Statique pour Linux, Cross-build Windows)
echo -e "\n${BLUE}[1/3] Building Go CLI (Static)...${NC}"
cd cli
echo "  - Linux (amd64, static)..."
# CGO_ENABLED=0 force l'utilisation de l'implémentation Go pure (plus portable)
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o "../$DIST_ROOT/linux/handmouse" main.go

echo "  - Windows (amd64)..."
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o "../$DIST_ROOT/windows/handmouse.exe" main.go
cd ..

# 2. Compilation Rust Core (OS actuel)
echo -e "\n${BLUE}[2/3] Building Rust Core...${NC}"
cd rust_core
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
cargo build --release
cd ..

# 3. Bundle Python Engine (OS actuel) via PyInstaller --onefile
echo -e "\n${BLUE}[3/3] Bundling Python Engine (Independent One-File)...${NC}"
if [ ! -d "venv" ]; then
    echo "  - Création du venv..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

./venv/bin/pip install pyinstaller

# Découverte du chemin librust_core.so
RUST_LIB="rust_core/target/release/librust_core.so"
if [ ! -f "$RUST_LIB" ]; then
    echo -e "${RED}Erreur: $RUST_LIB introuvable.${NC}"
    exit 1
fi

echo "  - Running PyInstaller (--onefile)..."
# --onefile emballe tout dans un seul binaire auto-extractible
./venv/bin/python -m PyInstaller --noconfirm --onefile --console \
    --name "handmouse-engine" \
    --add-data "assets:assets" \
    --add-binary "$RUST_LIB:." \
    --hidden-import "cv2" \
    --hidden-import "mediapipe" \
    --hidden-import "pyautogui" \
    --hidden-import "pynput" \
    main.py

# Placement final
mv dist/handmouse-engine "$DIST_ROOT/linux/"

echo -e "\n${GREEN}=== Build terminé avec succès ! ===${NC}"
echo -e "Binaires disponibles dans : ${BLUE}$DIST_ROOT/${NC}"
echo -e "  - Linux:   $DIST_ROOT/linux/handmouse (CLI) & $DIST_ROOT/linux/handmouse-engine (GUI)"
echo -e "  - Windows: $DIST_ROOT/windows/handmouse.exe (CLI uniquement)"
echo -e "\n${NC}Note: Pour la GUI Windows portative, lancez ce script sur Windows nativement."
