```
   ██╗  ██╗ █████╗ ███╗   ██╗██████╗     ███╗   ███╗ ██████╗ ██╗   ██╗███████╗███████╗
   ██║  ██║██╔══██╗████╗  ██║██╔══██╗    ████╗ ████║██╔═══██╗██║   ██║██╔════╝██╔════╝
   ███████║███████║██╔██╗ ██║██║  ██║    ██╔████╔██║██║   ██║██║   ██║███████╗█████╗  
   ██╔══██║██╔══██║██║╚██╗██║██║  ██║    ██║╚██╔╝██║██║   ██║██║   ██║╚════██║██╔══╝  
   ██║  ██║██║  ██║██║ ╚████║██████╔╝    ██║ ╚═╝ ██║╚██████╔╝╚██████╔╝███████║███████╗
   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝     ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
                                                                                         
                         🖐️  Contrôlez votre PC avec vos mains  🤖
```

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Go](https://img.shields.io/badge/go-1.21+-00ADD8)
![Rust](https://img.shields.io/badge/rust-1.70+-orange)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey)

---

## 📖 À Propos

**Hand Mouse OS** transforme votre webcam en interface de contrôle gestuel ultra-précise. Utilisez vos mains pour déplacer le curseur, cliquer, scroller et exécuter des actions complexes grâce à l'intelligence artificielle et des performances optimisées par Rust.

### 🎯 Pourquoi Hand Mouse OS ?

```
┌─────────────────────────────────────────────────────────────┐
│  ✨ Précision                → Filtrage SIMD 11.4x plus rapide│
│  🚀 Performance              → Support GPU/CPU automatique    │
│  🖥️  Multi-Plateforme        → Linux (Wayland/X11) + Windows │
│  🎨 Double Interface         → GUI Flet + CLI Go moderne     │
│  🤖 IA Temps Réel            → MediaPipe Hands (Google)      │
│  ⚡ Distribution Portable    → Binaire autonome sans dépendances│
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Fonctionnalités

| 🎯 Fonctionnalité | 📝 Description |
|-------------------|----------------|
| **Contrôle Souris Haute Précision** | Filtrage hybride Rust (SIMD AVX2) + Python avec lissage adaptatif |
| **Détection Multi-Mains** | Suivi simultané de 2 mains avec 21 points par main |
| **Support Wayland Natif** | Driver `evdev` (uinput) pour contrôle au niveau noyau |
| **Interface Moderne** | GUI Flet avec flux vidéo temps réel + CLI Go professionnel |
| **Mode Portable** | Distribution autonome (Go CLI statique + PyInstaller) |
| **GPU/CPU Auto** | Bascule intelligente selon le matériel disponible |
| **Gestes ASL** | Reconnaissance American Sign Language (en développement) |

---

## 🚀 Installation & Lancement

### 📦 Option 1 : Distribution Portable (RECOMMANDÉ)

```bash
# 1. Télécharger la dernière release
wget https://github.com/KOUSSEMON-Aurel/Hand_mouseOS/releases/latest/download/handmouse-linux-portable.zip

# 2. Extraire
unzip handmouse-linux-portable.zip
cd handmouse-linux-portable

# 3. Lancer (configuration automatique incluse)
./handmouse start
```

> **Note Linux/Wayland** : Au premier lancement, l'application configure automatiquement les permissions `uinput` (sudo requis une seule fois). Après configuration, **déconnectez-vous et reconnectez-vous** pour que les changements de groupe prennent effet.

---

### 🛠️ Option 2 : Build Depuis les Sources

#### Prérequis

- **Python** 3.10+
- **Go** 1.21+
- **Rust** 1.70+ (dernière version stable)
- **Système** : Linux (Arch, Ubuntu, Fedora...) ou Windows 10+

#### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/KOUSSEMON-Aurel/Hand_mouseOS.git
cd Hand_mouseOS

# 2. Build complet (Go CLI + Rust Core + Python Engine)
./scripts/build_portable.sh

# 3. Lancer
./dist/linux/handmouse start
```

#### Build Manuel (Développeurs)

```bash
# Environnement virtuel Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Compiler Rust Core (filtres SIMD)
cd rust_core
cargo build --release
cd ..

# Compiler Go CLI
cd cli
go build -o handmouse main.go
cd ..

# Lancer en mode développement
python main.py
```

---

## 🎮 Guide d'Utilisation

### Commandes Principales

```bash
# Démarrer l'application (GUI + Engine)
./dist/linux/handmouse start

# Configuration automatique des permissions (Linux uniquement)
./dist/linux/handmouse setup permissions

# Installer DroidCam (utiliser smartphone comme webcam)
./dist/linux/handmouse setup webcam

# Aide complète
./dist/linux/handmouse --help
```

### Gestes Supportés

```
┌────────────────────────────────────────────────────────┐
│  👆 Index levé              → Déplacer le curseur      │
│  ✌️  Index + Majeur         → Clic gauche              │
│  🤘 Pouce + Index + Majeur → Clic droit                │
│  🖐️  Main fermée            → Arrêter le mouvement     │
│  👍 Pouce levé             → Actions spéciales (bientôt)│
└────────────────────────────────────────────────────────┘
```

### Interface Utilisateur

L'application offre **deux modes** d'utilisation :

#### 🎨 Mode GUI (Par défaut)

- Flux vidéo en temps réel avec overlay squelettique
- Paramètres ajustables : sensibilité, caméra, lissage
- Diagnostic système (mode souris, OS, performances)

#### 💻 Mode Headless (CLI)

```bash
./handmouse run --headless
```

Idéal pour serveurs ou environnements sans interface graphique.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      🎯 Hand Mouse OS                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   Go CLI     │   │ Python Engine│   │  Rust Core   │    │
│  │  (Statique)  │──▶│  (PyInstaller)│──▶│ (SIMD AVX2) │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
│         │                   │                   │            │
│         │                   │                   │            │
│    Orchestration      MediaPipe AI         Filtrage         │
│    + IPC              + OpenCV             Ultra-Rapide     │
│    + Setup Auto       + Flet GUI           (11.4x speedup)  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Composants Clés

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **CLI** | Go (Cobra) | Orchestration, setup automatique, gestion config |
| **Engine** | Python + MediaPipe | Détection mains, traitement vidéo, IA |
| **Filtres** | Rust (PyO3 + SIMD) | Lissage mouvement ultra-performant |
| **GUI** | Flet (Flutter) | Interface graphique cross-platform |
| **Mouse Driver** | evdev (uinput) | Contrôle souris niveau noyau (Wayland) |

---

## 🐧 Support Linux : Wayland vs X11

### Wayland (Recommandé)

Hand Mouse OS utilise **evdev + uinput** pour un contrôle souris natif au niveau du noyau Linux, offrant :

- ✅ Mouvement visible du curseur sous Wayland
- ✅ Performances maximales
- ✅ Compatibilité universelle (toutes distros)

**Configuration automatique :**

```bash
./handmouse start  # Configure automatiquement au premier lancement
```

### X11

Fonctionne également avec `PyAutoGUI` et `Pynput` si `uinput` n'est pas disponible.

---

## 📁 Structure du Projet

```
Hand_mouseOS/
├── 📁 cli/                      # CLI Go (Cobra)
│   ├── cmd/                     # Commandes (start, setup, config)
│   │   ├── root.go
│   │   ├── start.go             # Lancement + auto-setup uinput
│   │   └── setup_permissions.go # Config automatique Linux
│   └── main.go
├── 📁 rust_core/                # Filtrage SIMD haute performance
│   └── src/
│       ├── lib.rs
│       └── filters/
│           ├── mod.rs           # OneEuroFilter (1D/2D)
│           └── simd_filter.rs   # Batch AVX2 (21 landmarks)
├── 📁 src/                      # Engine Python
│   ├── engine.py                # Moteur IA principal
│   ├── gui.py                   # Interface Flet
│   ├── mouse_driver.py          # Contrôle souris (evdev/pynput)
│   ├── advanced_filter.py       # Filtrage hybride Rust/Python
│   └── optimized_utils.py       # Utilitaires performance
├── 📁 scripts/
│   └── build_portable.sh        # Build distribution autonome
├── 📁 assets/
│   └── hand_landmarker.task     # Modèle MediaPipe
├── main.py                      # Point d'entrée GUI
└── requirements.txt
```

---

## 🛠️ Technologies & Dépendances

### Stack Principal

- **Python** 3.10+ : Engine IA, GUI, logique métier
- **Rust** 1.70+ : Filtrage SIMD (11.4x speedup vs Python pur)
- **Go** 1.21+ : CLI, orchestration, IPC

### Bibliothèques Clés

- **MediaPipe** (Google) : Détection et tracking de mains temps réel
- **Flet** : Framework GUI Python (basé sur Flutter)
- **PyO3** : Bindings Rust ↔ Python
- **evdev** : Contrôle périphérique Linux (uinput)
- **OpenCV** : Traitement vidéo
- **Cobra** (Go) : Framework CLI moderne

---

## 🔧 Configuration

### Fichier de Configuration

```yaml
# ~/.config/handmouse/config.yaml (auto-généré)

camera:
  index: 0              # Index de la caméra
  resolution: [640, 480]

mouse:
  sensitivity: 1.3      # Gamma de sensibilité
  smoothing: 0.007      # Beta du filtre OneEuro

mediapipe:
  min_detection_confidence: 0.3
  min_tracking_confidence: 0.5
```

### Variables d'Environnement

```bash
# Désactiver les logs TensorFlow/MediaPipe
export TF_CPP_MIN_LOG_LEVEL=3
export ABSL_LOGGING_LEVEL=3

# Forcer le mode CPU (désactiver GPU)
export HANDMOUSE_FORCE_CPU=1
```

---

## 📊 Performances

### Benchmarks (Ryzen 5 3600, Webcam 720p)

| Métrique | Python Pur | Rust SIMD | Speedup |
|----------|-----------|-----------|---------|
| Filtrage 21 landmarks | 127.3 µs | **11.2 µs** | **11.4x** |
| FPS moyen | 24 | **30** | 1.25x |
| Latence mouvement | ~50ms | **~15ms** | 3.3x |

> **Note** : Les performances varient selon le CPU (AVX2 requis pour SIMD optimal).

---

## 🗺️ Roadmap

### ✅ Complété (Sprint 9)

- [x] CLI Go avec commandes professionnelles
- [x] Distribution portable autonome (PyInstaller + Go statique)
- [x] Support Wayland natif (evdev/uinput)
- [x] Configuration automatique des permissions
- [x] Filtrage SIMD Rust (11.4x speedup)
- [x] Build propre avec nettoyage cache

### 🚧 En Cours (Sprint 10)

- [ ] Profils utilisateur (YAML)
- [ ] UI de sélection de profil
- [ ] Paramètres par profil (sensibilité, gestes)

### 📅 Planifié

- [ ] Support macOS (DMG + Universal Binaries)
- [ ] API REST + Monitoring
- [ ] Gestes personnalisables (éditeur visuel)
- [ ] ML Local (entraînement gestes custom)
- [ ] Clavier virtuel gestuel
- [ ] Plugin system (extensions .py)

---

## 🐛 Dépannage

### Linux : "UInput failed (/dev/uinput missing)"

**Solution** : Redémarrez votre session après le premier lancement

```bash
# L'app configure automatiquement, mais les changements de groupe 
# nécessitent une reconnexion pour être actifs
./handmouse start    # Configure (demande sudo)
# → Logout/Login
./handmouse start    # Fonctionne désormais !
```

**Vérification manuelle** :

```bash
groups  # Vérifier que 'input' est présent
ls -l /dev/uinput  # Doit montrer 'crw-rw---- ... input'
```

### "Invisible cursor" sur Wayland

✅ **Résolu** : Hand Mouse OS utilise `evdev` qui fonctionne nativement sous Wayland. Si le curseur reste invisible, vérifiez que vous avez bien redémarré votre session après la configuration.

### GPU non détecté

L'application bascule automatiquement en mode CPU. Pour forcer le GPU :

```bash
# Vérifier les drivers
nvidia-smi  # NVIDIA
rocm-smi    # AMD
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 🎉

### Comment contribuer ?

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

### Guidelines

- Code en **français** (commentaires, logs, docs)
- Tests unitaires requis pour nouvelles features
- Respecter l'architecture existante (Go/Rust/Python séparés)

---

## 📄 Licence

**MIT License** - Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

Un grand merci aux projets open-source qui rendent Hand Mouse OS possible :

- **MediaPipe** (Google) : Detection et tracking de mains de classe mondiale
- **Flet** : Framework GUI Python moderne et élégant
- **PyO3** : Bindings Rust-Python ultra-performants
- **Cobra** (Spf13) : Framework CLI Go professionnel
- **evdev** : Accès bas-niveau aux périphériques Linux

---

## 📞 Support & Contact

- 🐛 **Issues** : [GitHub Issues](https://github.com/KOUSSEMON-Aurel/Hand_mouseOS/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/KOUSSEMON-Aurel/Hand_mouseOS/discussions)
- 📧 **Email** : <reyseilfullbryger@gmail.com>

---

<div align="center">

**Fait avec des projets open source : [Sign-Language-Interpreter-using-Deep-Learning](https://github.com/harshbg/Sign-Language-Interpreter-using-Deep-Learning.git) , [Mediapipe](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/models.md#hands) et 🖐️ par [KOUSSEMON Aurel](https://github.com/KOUSSEMON-Aurel)**

⭐ **Star ce projet si vous l'aimez !** ⭐

</div>
