#!/bin/bash
# Hand Mouse OS - Portable Build Script
# Génère les binaires portables pour Linux et Windows (CLI) 
# et le bundle Python pour la plateforme actuelle.

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Hand Mouse OS Portable Build ===${NC}"

# Dossier de sortie
DIST_ROOT="dist"
DIST_LINUX="$DIST_ROOT/linux"
DIST_WINDOWS="$DIST_ROOT/windows"

mkdir -p "$DIST_LINUX" "$DIST_LINUX/assets"
mkdir -p "$DIST_WINDOWS" "$DIST_WINDOWS/assets"

# 1. Compilation Go CLI (Multi-OS)
echo -e "\n${BLUE}[1/3] Building Go CLI...${NC}"
cd cli
echo "  - Linux (amd64)..."
GOOS=linux GOARCH=amd64 go build -o "../$DIST_LINUX/handmouse" main.go
echo "  - Windows (amd64)..."
GOOS=windows GOARCH=amd64 go build -o "../$DIST_WINDOWS/handmouse.exe" main.go
cd ..

# 2. Compilation Rust Core (OS actuel)
echo -e "\n${BLUE}[2/3] Building Rust Core...${NC}"
cd rust_core
# Force la compatibilité avec Python 3.14+ via stable ABI
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
cargo build --release
cd ..
# Note: Pour Windows, cela nécessite de tourner sur Windows ou d'utiliser cross-rs.
# Ici on copie pour Linux si on est sur Linux.
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cp rust_core/target/release/librust_core.so "$DIST_LINUX/"
fi

# 3. Bundle Python (OS actuel) via PyInstaller
echo -e "\n${BLUE}[3/3] Bundling Python Engine...${NC}"
if [ ! -d "venv" ]; then
    echo "  - Création du venv..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

./venv/bin/pip install pyinstaller

# Assets
cp -r assets/* "$DIST_LINUX/assets/"
cp -r assets/* "$DIST_WINDOWS/assets/"

echo "  - Running PyInstaller..."
# On utilise --onedir pour une version portable en dossier
./venv/bin/python -m PyInstaller --noconfirm --onedir --console \
    --name "handmouse-engine" \
    --add-data "assets:assets" \
    --add-binary "rust_core/target/release/librust_core.so:." \
    --hidden-import "cv2" \
    --hidden-import "mediapipe" \
    main.py

mv dist/handmouse-engine "$DIST_LINUX/"

echo -e "\n${GREEN}=== Build terminé avec succès ! ===${NC}"
echo -e "Retrouvez les fichiers portables dans : ${BLUE}$DIST_ROOT/${NC}"
echo -e "${NC}Note: Pour générer le bundle Python Windows, lancez ce script sur Windows avec WSL ou Git Bash."
