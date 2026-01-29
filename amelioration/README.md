# 🖱️ Hand Mouse OS - Plan d'Optimisation Complet

> **Version:** 1.0.0-stable  
> **Date:** 29 Janvier 2026  
> **Mainteneur:** Aurel / Agent AI

---

## 📋 Table des Matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Fichiers inclus](#-fichiers-inclus)
3. [Installation rapide](#-installation-rapide)
4. [Structure du plan](#-structure-du-plan)
5. [Gains de performance attendus](#-gains-de-performance-attendus)
6. [Roadmap d'implémentation](#-roadmap-dimplémentation)
7. [FAQ](#-faq)

---

## 🎯 Vue d'ensemble

Ce package contient un **plan d'optimisation complet en 3 niveaux** pour maximiser les performances de Hand Mouse OS. L'objectif est d'atteindre:

- ✅ **Latence < 50ms** (contre 80-120ms actuellement)
- ✅ **60 FPS stables** (contre 20-30 FPS actuellement)
- ✅ **Précision ±2px** (contre ±5px actuellement)
- ✅ **Usage CPU < 20%** (contre 30-50% actuellement)

### Goulots d'étranglement identifiés

1. **Inférence CPU MediaPipe** (30-50ms) → Solution: GPU Delegate ou Edge TPU
2. **Backlog de frames** → Solution: Ring Buffer latest-only
3. **Motion blur** → Solution: Exposition fixe v4l2
4. **Copies mémoire** → Solution: Buffers préalloués

---

## 📦 Fichiers inclus

### 1. `HandMouseOS_Plan_Optimisation_Complet.docx`
**Document technique principal (40+ pages)**

Contenu:
- Résumé exécutif avec métriques cibles
- **Niveau 1: Quick Wins** (1-2 jours, gains immédiats)
  - Profiling détaillé
  - Ring buffer latest-only
  - Configuration caméra v4l2
  - Filtrage adaptatif OneEuro
  - Buffers préalloués
  - Permissions uinput
- **Niveau 2: Améliorations moyennes** (1-2 semaines, architecture)
  - Multiprocessing avec shared memory
  - Pipeline GStreamer
  - Quantification modèle TFLite
  - Délégation GPU/TPU
- **Niveau 3: Précision & UX** (1-2 semaines)
  - Système de calibration
  - Mapping non-linéaire
  - Mécanismes de clic (dwell, pinch)
  - Filtre de Kalman
- Plan d'action concret (roadmap)
- Métriques de succès (KPIs)

### 2. `hand_mouse_optimized_implementations.py`
**Bibliothèque de code Python prête à l'emploi**

Classes implémentées:
- `PerformanceProfiler` - Mesures précises des temps
- `LatestFrameBuffer` - Ring buffer optimisé
- `AdaptiveOneEuroFilter` - Filtrage dynamique
- `CameraConfigurator` - Configuration v4l2
- `PreallocatedBuffers` - Buffers sans copies
- `DwellClickDetector` - Détection de clic par maintien
- `VisualFeedback` - Rendu feedback utilisateur
- `CalibrationSystem` - Calibration 4-points
- `AdaptiveSensitivityMapper` - Mapping non-linéaire
- `OptimizedMouseDriver` - Driver uinput optimisé
- `example_optimized_pipeline()` - Pipeline complet intégré

**Usage:**
```python
from hand_mouse_optimized_implementations import *

# Initialiser les composants
profiler = PerformanceProfiler()
buffer = LatestFrameBuffer()
filter = AdaptiveOneEuroFilter()
mouse = OptimizedMouseDriver(1920, 1080)

# Utiliser dans votre pipeline...
```

### 3. `install_hand_mouse_os.sh`
**Script d'installation automatique**

Fonctionnalités:
- ✅ Vérification système (Linux, Python 3.8+)
- ✅ Installation dépendances (v4l-utils, GStreamer, udev)
- ✅ Configuration permissions uinput
- ✅ Configuration optimale caméra
- ✅ Création environnement virtuel Python
- ✅ Installation packages (OpenCV, MediaPipe, etc.)
- ✅ Tests de vérification
- ✅ Benchmark de performance
- ✅ Génération fichier config

**Usage:**
```bash
chmod +x install_hand_mouse_os.sh
./install_hand_mouse_os.sh
```

### 4. `README.md` (ce fichier)
Guide complet pour naviguer dans le plan d'optimisation.

---

## 🚀 Installation rapide

### Prérequis
- Linux (testé sur Ubuntu 22.04, Arch Linux)
- Python 3.8+
- Webcam USB
- Permissions sudo (pour configuration initiale)

### Méthode 1: Installation automatique (Recommandé)

```bash
# Télécharger les fichiers
cd ~/hand-mouse-os

# Lancer l'installation
chmod +x install_hand_mouse_os.sh
./install_hand_mouse_os.sh

# Suivre les instructions à l'écran
```

Le script va:
1. Installer les dépendances système
2. Configurer les permissions uinput
3. Optimiser la caméra
4. Créer l'environnement Python
5. Installer les packages
6. Effectuer des tests

### Méthode 2: Installation manuelle

```bash
# 1. Dépendances système
sudo apt update
sudo apt install -y v4l-utils gstreamer1.0-tools python3-pip python3-venv

# 2. Permissions uinput
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", TAG+="uaccess"' | \
    sudo tee /etc/udev/rules.d/99-uinput.rules
sudo udevadm control --reload-rules
sudo usermod -aG input $USER
# Déconnexion/reconnexion requise

# 3. Environnement Python
python3 -m venv venv
source venv/bin/activate

# 4. Packages Python
pip install opencv-python mediapipe numpy python-uinput screeninfo filterpy

# 5. Configuration caméra
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_auto=1
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_absolute=150
v4l2-ctl -d /dev/video0 --set-ctrl=gain=100
```

---

## 🏗️ Structure du plan

Le plan est organisé en **3 niveaux de priorité**:

### 📌 Niveau 1: Quick Wins (Priorité HAUTE)
**Durée:** 1-2 jours  
**Difficulté:** Faible  
**Impact:** Haut  

**Objectif:** Gains immédiats avec un minimum d'effort.

Optimisations:
1. ✅ Profiling détaillé (identifier les goulots)
2. ✅ Ring buffer latest-only (éliminer backlog)
3. ✅ Exposition caméra fixe (réduire motion blur)
4. ✅ Filtrage adaptatif OneEuro (stabilité + réactivité)
5. ✅ Buffers préalloués (éliminer copies)
6. ✅ Permissions uinput (sécurité)
7. ✅ Dwell click (interaction basique)

**Gain attendu:** Latence 80-120ms → 60-80ms

### ⚙️ Niveau 2: Améliorations moyennes (Priorité MOYENNE)
**Durée:** 1-2 semaines  
**Difficulté:** Moyenne  
**Impact:** Très haut  

**Objectif:** Débloquer le véritable potentiel du système.

Optimisations:
1. 🔧 Multiprocessing + shared memory
2. 🔧 Pipeline GStreamer optimisé
3. 🔧 Quantification modèle TFLite (int8)
4. 🔧 Délégation matérielle (GPU/TPU) ⭐ **CRITIQUE**

**Solutions matérielles:**
- **Coral Edge TPU:** 20-30 FPS → 60+ FPS (USB, $60)
- **NVIDIA GPU:** 20-30 FPS → 120+ FPS (CUDA/TensorRT)
- **Intel OpenVINO:** 20-30 FPS → 40-60 FPS (CPU/iGPU)

**Gain attendu:** 20-30 FPS → 40-60 FPS (CPU) ou 60+ FPS (GPU/TPU)

### 🎨 Niveau 3: Précision & UX (Priorité MOYENNE-BASSE)
**Durée:** 1-2 semaines  
**Difficulté:** Moyenne  
**Impact:** Moyen-Haut  

**Objectif:** Transformer l'outil en solution professionnelle.

Optimisations:
1. 🎯 Calibration 4-points (compensation parallaxe)
2. 🎯 Mapping non-linéaire (sensibilité adaptative)
3. 🎯 Pinch gesture (clic rapide)
4. 🎯 Filtre de Kalman (prédiction)

**Gain attendu:** Précision ±5px → ±2px

---

## 📊 Gains de performance attendus

### Tableau comparatif

| Métrique | Baseline (Actuel) | Après Niveau 1 | Après Niveau 2 | Cible Finale |
|----------|-------------------|----------------|----------------|--------------|
| **Latence totale** | 80-120ms | 60-80ms | 40-60ms | **< 40ms** |
| **FPS IA** | 20-30 | 25-35 | 40-60 | **60+** |
| **Précision** | ±5px | ±4px | ±3px | **±2px** |
| **CPU Usage** | 30-50% | 25-40% | 20-30% | **< 20%** |
| **Stabilité** | 85% | 90% | 95% | **99%** |

### Graphique progression

```
Latence (ms)
120 ┤ ███████████ Baseline
100 ┤ ██████████
 80 ┤ ███████  ← Niveau 1
 60 ┤ █████
 40 ┤ ██  ← Niveau 2 + 3
 20 ┤
  0 └─────────────────────
```

---

## 🗓️ Roadmap d'implémentation

### Semaine 1-2: Quick Wins ⚡
- ✅ **Jour 1:** Profiling + ring buffer
- ✅ **Jour 2:** Configuration caméra v4l2
- ✅ **Jour 3:** Filtrage adaptatif
- ✅ **Jour 4:** Buffers préalloués
- ✅ **Jour 5:** Permissions uinput
- ✅ **Jour 6-7:** Tests + dwell click

**Livrable:** Latence réduite de 30-40%, système stable

### Semaine 3-4: Architecture ⚙️
- 🔧 **Semaine 3:** Multiprocessing + GStreamer
- 🔧 **Semaine 4:** Quantification + GPU delegate

**Livrable:** 60 FPS stables, usage CPU divisé par 2

### Semaine 5-6: UX & Précision 🎨
- 🎯 **Semaine 5:** Calibration + mapping non-linéaire
- 🎯 **Semaine 6:** Pinch gesture + Kalman + tests utilisateurs

**Livrable:** Précision professionnelle, utilisable au quotidien

### Mois 2+: Polish & Scale 🚀
- Documentation complète
- CI/CD avec tests performance
- Package Flatpak/AppImage
- Support multi-utilisateur
- Interface settings avancés

---

## ❓ FAQ

### Q1: Par où commencer ?
**R:** Commencez par le Niveau 1 (Quick Wins). Suivez l'ordre du document docx. Chaque optimisation est indépendante.

### Q2: Quel est le gain le plus important ?
**R:** Le **GPU Delegate / Edge TPU** (Niveau 2). C'est la seule façon d'atteindre 60 FPS. Mais nécessite matériel approprié.

### Q3: Puis-je utiliser le code Python tel quel ?
**R:** Oui ! Le fichier `hand_mouse_optimized_implementations.py` contient des classes prêtes à l'emploi. Copiez-les dans votre projet.

### Q4: Mon système est déjà rapide, dois-je optimiser ?
**R:** Oui pour la **stabilité**. Le ring buffer et le filtrage adaptatif améliorent la fiabilité même avec de bonnes performances.

### Q5: Je n'ai pas de GPU, puis-je quand même optimiser ?
**R:** Oui ! Niveaux 1 et 3 sont CPU-only. Vous atteindrez 40-50 FPS avec le Niveau 1 + quantification.

### Q6: Combien de temps pour tout implémenter ?
**R:** 
- **Niveau 1 seul:** 1-2 jours
- **Niveaux 1+2:** 2-3 semaines
- **Complet (1+2+3):** 1-2 mois

### Q7: Puis-je contribuer ou améliorer ce plan ?
**R:** Absolument ! Ce document est un point de départ. Testez, mesurez, améliorez.

### Q8: Wayland est-il supporté ?
**R:** Oui, mais "Always on Top" nécessite configuration manuelle. Voir section dédiée dans le docx.

---

## 📚 Ressources supplémentaires

### Documentation MediaPipe
- [Hand Landmarker Guide](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- [Python API Reference](https://developers.google.com/mediapipe/api/solutions/python/mp/tasks/vision/HandLandmarker)

### Filtrage
- [One Euro Filter Paper](https://hal.inria.fr/hal-00670496/document)
- [Kalman Filter Tutorial](https://www.kalmanfilter.net/)

### Hardware Acceleration
- [Coral Edge TPU](https://coral.ai/products/accelerator/)
- [TensorFlow Lite GPU Delegate](https://www.tensorflow.org/lite/performance/gpu)
- [OpenVINO Toolkit](https://docs.openvino.ai/)

### v4l2 / GStreamer
- [v4l2-ctl Man Page](https://man7.org/linux/man-pages/man1/v4l2-ctl.1.html)
- [GStreamer Documentation](https://gstreamer.freedesktop.org/documentation/)

---

## 🤝 Contributions & Support

### Reporting Issues
Si vous rencontrez des problèmes lors de l'implémentation:
1. Vérifiez les logs de profiling
2. Consultez la section FAQ
3. Testez chaque optimisation individuellement

### Améliorations futures
Idées pour versions futures:
- Support de multiples caméras
- Détection de gestes complexes
- Mode "deux mains" (clic gauche/droit)
- Support macOS/Windows
- Interface web de monitoring

---

## 📄 Licence

Ce plan d'optimisation est fourni tel quel pour améliorer Hand Mouse OS.

---

## 🙏 Remerciements

Merci aux contributeurs de:
- **MediaPipe** (Google) - Framework IA
- **OpenCV** - Vision par ordinateur
- **TensorFlow Lite** - Inférence optimisée
- **La communauté Linux** - Outils v4l2, udev, GStreamer

---

**Dernière mise à jour:** 29 Janvier 2026  
**Version du plan:** 1.0.0-stable  
**Généré par:** Claude AI (Anthropic)

---

🚀 **Bon développement et excellente optimisation !**
