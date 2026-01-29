#!/bin/bash
# Hand Mouse OS - Script d'Installation & Configuration Rapide
# =============================================================

set -e  # Arrêt en cas d'erreur

echo "=================================================="
echo "  🚀 Hand Mouse OS - Installation Automatique"
echo "=================================================="
echo ""

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
step() {
    echo -e "${BLUE}▶ $1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

# =============================================================================
# ÉTAPE 1: Vérification du système
# =============================================================================

step "Étape 1: Vérification du système"

# Vérifier si on est sur Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    error "Ce script est conçu pour Linux uniquement"
    exit 1
fi

success "Système Linux détecté"

# Vérifier Python 3.8+
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    success "Python $PYTHON_VERSION détecté"
else
    error "Python 3 non trouvé. Installation requise."
    exit 1
fi

# Vérifier les permissions sudo
if sudo -n true 2>/dev/null; then
    success "Permissions sudo disponibles"
else
    warning "Certaines opérations nécessiteront sudo"
fi

echo ""

# =============================================================================
# ÉTAPE 2: Installation des dépendances système
# =============================================================================

step "Étape 2: Installation des dépendances système"

echo "Installation de:"
echo "  - v4l-utils (contrôle caméra)"
echo "  - GStreamer (pipeline vidéo optimisé)"
echo "  - udev (permissions périphériques)"
echo ""

read -p "Continuer? [O/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]] && [[ ! -z $REPLY ]]; then
    warning "Installation des dépendances annulée"
else
    sudo apt update
    sudo apt install -y \
        v4l-utils \
        gstreamer1.0-tools \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        libgstreamer1.0-dev \
        python3-pip \
        python3-venv
    
    success "Dépendances système installées"
fi

echo ""

# =============================================================================
# ÉTAPE 3: Configuration udev pour /dev/uinput
# =============================================================================

step "Étape 3: Configuration des permissions uinput"

UDEV_RULE="/etc/udev/rules.d/99-uinput.rules"

if [ -f "$UDEV_RULE" ]; then
    success "Règle udev déjà existante"
else
    echo "Création de la règle udev..."
    echo 'KERNEL=="uinput", MODE="0660", GROUP="input", TAG+="uaccess"' | sudo tee $UDEV_RULE > /dev/null
    
    # Recharger udev
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    # Ajouter l'utilisateur au groupe input
    sudo usermod -aG input $USER
    
    success "Règle udev créée"
    warning "IMPORTANT: Vous devez vous déconnecter puis reconnecter pour appliquer les permissions"
fi

echo ""

# =============================================================================
# ÉTAPE 4: Configuration de la caméra
# =============================================================================

step "Étape 4: Configuration optimale de la caméra"

# Lister les caméras
echo "Caméras détectées:"
v4l2-ctl --list-devices

echo ""
read -p "Device de la caméra à utiliser [/dev/video0]: " CAMERA_DEVICE
CAMERA_DEVICE=${CAMERA_DEVICE:-/dev/video0}

if [ ! -e "$CAMERA_DEVICE" ]; then
    error "Device $CAMERA_DEVICE non trouvé"
else
    success "Utilisation de $CAMERA_DEVICE"
    
    echo ""
    echo "Configuration de l'exposition et du gain..."
    
    # Fixer exposition
    v4l2-ctl -d $CAMERA_DEVICE --set-ctrl=exposure_auto=1 2>/dev/null || true
    v4l2-ctl -d $CAMERA_DEVICE --set-ctrl=exposure_absolute=150 2>/dev/null || true
    
    # Fixer focus
    v4l2-ctl -d $CAMERA_DEVICE --set-ctrl=focus_auto=0 2>/dev/null || true
    v4l2-ctl -d $CAMERA_DEVICE --set-ctrl=focus_absolute=0 2>/dev/null || true
    
    # Fixer gain
    v4l2-ctl -d $CAMERA_DEVICE --set-ctrl=gain=100 2>/dev/null || true
    
    # White balance manuel
    v4l2-ctl -d $CAMERA_DEVICE --set-ctrl=white_balance_temperature_auto=0 2>/dev/null || true
    v4l2-ctl -d $CAMERA_DEVICE --set-ctrl=white_balance_temperature=4600 2>/dev/null || true
    
    success "Caméra configurée (certains contrôles peuvent ne pas être supportés)"
fi

echo ""

# =============================================================================
# ÉTAPE 5: Environnement virtuel Python
# =============================================================================

step "Étape 5: Création de l'environnement virtuel Python"

if [ -d "venv" ]; then
    success "Environnement virtuel déjà existant"
else
    python3 -m venv venv
    success "Environnement virtuel créé"
fi

# Activer l'environnement
source venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip

echo ""

# =============================================================================
# ÉTAPE 6: Installation des packages Python
# =============================================================================

step "Étape 6: Installation des packages Python"

echo "Installation de:"
echo "  - opencv-python (vision par ordinateur)"
echo "  - mediapipe (détection de main)"
echo "  - numpy (calculs numériques)"
echo "  - python-uinput (contrôle souris)"
echo "  - screeninfo (résolution écran)"
echo "  - filterpy (filtre de Kalman)"
echo ""

cat > requirements.txt << 'EOF'
# Core dependencies
opencv-python==4.8.1.78
mediapipe==0.10.7
numpy==1.24.3

# Mouse control
python-uinput==0.11.2

# Utilities
screeninfo==0.8.1
filterpy==1.4.5

# Optional (pour développement)
pytest==7.4.3
pytest-benchmark==4.0.0
EOF

pip install -r requirements.txt

success "Packages Python installés"

echo ""

# =============================================================================
# ÉTAPE 7: Tests de vérification
# =============================================================================

step "Étape 7: Tests de vérification"

echo "Test 1: Import OpenCV..."
python3 -c "import cv2; print(f'OpenCV {cv2.__version__} OK')" && success "OpenCV OK" || error "OpenCV FAIL"

echo "Test 2: Import MediaPipe..."
python3 -c "import mediapipe as mp; print(f'MediaPipe {mp.__version__} OK')" && success "MediaPipe OK" || error "MediaPipe FAIL"

echo "Test 3: Accès caméra..."
python3 << 'PYTHON_TEST'
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    cap.release()
    if ret:
        print("Caméra accessible et fonctionnelle")
        exit(0)
print("Impossible d'accéder à la caméra")
exit(1)
PYTHON_TEST

if [ $? -eq 0 ]; then
    success "Caméra OK"
else
    error "Caméra FAIL"
fi

echo "Test 4: Permissions uinput..."
if [ -w /dev/uinput ] || groups | grep -q input; then
    success "Permissions uinput OK"
else
    error "Permissions uinput FAIL - Déconnexion/reconnexion requise"
fi

echo ""

# =============================================================================
# ÉTAPE 8: Benchmark rapide
# =============================================================================

step "Étape 8: Benchmark de performance"

echo "Test de capture caméra (5 secondes)..."

python3 << 'PYTHON_BENCHMARK'
import cv2
import time
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir la caméra")
    exit(1)

frame_times = []
start_time = time.time()
frame_count = 0

while time.time() - start_time < 5.0:
    t0 = time.perf_counter()
    ret, frame = cap.read()
    t1 = time.perf_counter()
    
    if ret:
        frame_times.append((t1 - t0) * 1000)
        frame_count += 1

cap.release()

if frame_times:
    avg_time = np.mean(frame_times)
    fps = 1000 / avg_time if avg_time > 0 else 0
    
    print(f"\n📊 Résultats:")
    print(f"  Frames capturées: {frame_count}")
    print(f"  Temps moyen: {avg_time:.2f}ms")
    print(f"  FPS: {fps:.1f}")
    
    if fps >= 25:
        print("  ✓ Performance acceptable")
    else:
        print("  ⚠ Performance suboptimale")
PYTHON_BENCHMARK

echo ""

# =============================================================================
# RÉSUMÉ ET PROCHAINES ÉTAPES
# =============================================================================

echo "=================================================="
echo "  ✅ Installation terminée!"
echo "=================================================="
echo ""
echo "📝 Prochaines étapes:"
echo ""
echo "1. Activez l'environnement virtuel:"
echo "   $ source venv/bin/activate"
echo ""
echo "2. Lancez Hand Mouse OS:"
echo "   $ python src/main.py"
echo ""
echo "3. Si erreur de permissions uinput:"
echo "   - Déconnectez-vous de votre session"
echo "   - Reconnectez-vous"
echo "   - Relancez le programme"
echo ""
echo "4. Pour optimisation maximale, consultez:"
echo "   - HandMouseOS_Plan_Optimisation_Complet.docx"
echo "   - hand_mouse_optimized_implementations.py"
echo ""
echo "=================================================="
echo "  📚 Ressources utiles"
echo "=================================================="
echo ""
echo "Configuration caméra:"
echo "  $ v4l2-ctl -d /dev/video0 --list-ctrls"
echo ""
echo "Monitoring performance:"
echo "  $ python src/test_cam.py"
echo ""
echo "Logs détaillés:"
echo "  $ LOGLEVEL=DEBUG python src/main.py"
echo ""

# Sauvegarder les paramètres
cat > .hand_mouse_config << EOF
# Hand Mouse OS Configuration
# Generated on $(date)

CAMERA_DEVICE=$CAMERA_DEVICE
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=30

SCREEN_WIDTH=$(xdpyinfo 2>/dev/null | awk '/dimensions/{print $2}' | cut -d'x' -f1)
SCREEN_HEIGHT=$(xdpyinfo 2>/dev/null | awk '/dimensions/{print $2}' | cut -d'x' -f2)

# Filtrage
FILTER_MIN_CUTOFF=0.004
FILTER_BETA=0.7

# Dwell click
DWELL_TIME=0.4
DWELL_TOLERANCE=15

# Performance
ENABLE_GPU=false
ENABLE_PROFILING=true
EOF

success "Configuration sauvegardée dans .hand_mouse_config"

echo ""
echo "Bonne chance! 🚀"
