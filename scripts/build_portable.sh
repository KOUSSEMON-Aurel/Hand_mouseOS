#!/bin/bash
# Hand Mouse OS - Independent Portable Build Script v3
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

# 3. Bundle Python Engine (OS actuel) via PyInstaller
echo -e "\n${BLUE}[3/3] Bundling Python Engine (Independent Bundle)...${NC}"
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

echo "  - Running PyInstaller..."
# On utilise --onedir pour Flet car --onefile est problématique avec ses assets internes sur Linux
# On zip ensuite pour la portabilité
./venv/bin/python -m PyInstaller --noconfirm --onedir --console \
    --name "handmouse-engine" \
    --add-data "assets:assets" \
    --add-data "src:src" \
    --collect-all "flet" \
    --collect-all "flet_desktop" \
    --add-binary "$RUST_LIB:." \
    --hidden-import "cv2" \
    --hidden-import "mediapipe" \
    --hidden-import "pyautogui" \
    --hidden-import "pynput" \
    --hidden-import "src" \
    --hidden-import "src.engine" \
    --hidden-import "src.ipc_server" \
    --hidden-import "src.mouse_driver" \
    --hidden-import "src.advanced_filter" \
    --hidden-import "src.gesture_classifier" \
    --hidden-import "src.context_mode" \
    --hidden-import "src.action_dispatcher" \
    --hidden-import "src.feedback_overlay" \
    --hidden-import "src.virtual_keyboard" \
    --hidden-import "src.asl_manager" \
    main.py

# Placement final
mv dist/handmouse-engine "$DIST_ROOT/linux/"

# Zip le dossier linux pour une distribution facile
if command -v zip >/dev/null 2>&1; then
    echo -e "\n${BLUE}Compressing Linux bundle...${NC}"
    cd "$DIST_ROOT/linux"
    zip -r "../../handmouse-linux-portable.zip" .
    cd ../..
else
    echo -e "\n${RED}Note: 'zip' non trouvé, archive .zip non créée.${NC}"
fi

echo -e "\n${GREEN}=== Build terminé avec succès ! ===${NC}"
echo -e "Archives disponibles dans : ${BLUE}$DIST_ROOT/${NC}"
echo -e "  - Linux:   handmouse-linux-portable.zip"
echo -e "  - Windows: $DIST_ROOT/windows/handmouse.exe (CLI uniquement)"
