# 🖐️ Hand Mouse OS

**Contrôlez votre ordinateur avec vos mains grâce à l'IA.**

Hand Mouse OS est un système de contrôle gestuel avancé qui transforme votre webcam en interface de contrôle. Déplacez le curseur, cliquez, et exécutez des actions complexes simplement avec vos mains.

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Go](https://img.shields.io/badge/go-1.21+-00ADD8)
![Rust](https://img.shields.io/badge/rust-1.70+-orange)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ✨ Fonctionnalités

- 🎯 **Contrôle de souris haute précision** avec filtrage SIMD Rust (11.4x plus rapide)
- 🖐️ **Détection multi-mains** (2 mains simultanées)
- 🎨 **Double interface** : GUI Flet + CLI Go professionnel
- 🧠 **Reconnaissance ASL** (American Sign Language)
- ⚡ **GPU/CPU automatique** avec fallback intelligent
- 📹 **Flux vidéo AR temps réel** avec overlay squelettique
- 🖥️ **Mode headless** pour serveurs et environnements sans GUI

---

## 🚀 Installation Rapide

```bash
git clone https://github.com/KOUSSEMON-Aurel/Hand_mouseOS.git
cd Hand_mouseOS

# Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Rust (optionnel mais recommandé)
cd rust_core && maturin develop --release && cd ..

# CLI Go
cd cli && go build -o handmouse && cd ..
```

---

## 🎮 Utilisation

### Mode GUI (Interface Graphique)

```bash
./cli/handmouse start --gui
```

### Mode CLI (Headless)

```bash
# Lancer l'engine seul
./cli/handmouse run

# Lancer sans vidéo (serveur)
./cli/handmouse run --headless

# Monitorer en temps réel
./cli/handmouse dash

# Configurer
./cli/handmouse config set asl true
```

### Commandes Disponibles

| Commande | Description |
|----------|-------------|
| `start` | Lance l'interface GUI Flet |
| `run` | Lance l'engine headless (avec/sans vidéo) |
| `stop` | Arrête tous les processus |
| `status` | Affiche l'état du système |
| `dash` | Dashboard interactif (TUI) |
| `config` | Gère la configuration en temps réel |

Pour plus de détails : `./cli/handmouse --help`

---

## 📁 Structure du Projet

```
Hand_mouseOS/
├── cli/                     # CLI Go (Cobra + Bubble Tea)
│   ├── cmd/                # Commandes (start, run, config, etc.)
│   ├── tui/                # Dashboard interactif
│   └── ipc/                # Communication Go ↔ Python
├── rust_core/              # Filtrage SIMD haute performance
│   └── src/filters/        # OneEuro filter avec AVX2
├── src/                    # Code source Python
│   ├── engine.py          # Moteur IA principal
│   ├── gui.py             # Interface Flet
│   ├── headless_runner.py # Mode CLI standalone
│   ├── ipc_server.py      # Serveur IPC
│   └── mouse_driver.py    # Contrôle souris (uinput)
└── main.py                # Point d'entrée GUI
```

---

## 🛠️ Technologies

- **Python** : Engine IA et interface
- **Rust** : Filtrage SIMD (AVX2) pour performance maximale
- **Go** : CLI professionnel et TUI
- **MediaPipe** : Détection de mains
- **Flet** : Interface graphique
- **Bubble Tea** : Dashboard terminal

---

## 📝 Roadmap

- [x] CLI Go avec Cobra
- [x] Mode headless
- [x] Dashboard TUI temps réel
- [x] Filtrage SIMD Rust (11.4x speedup)
- [ ] Cross-compilation binaire (Windows/Mac)
- [ ] Clavier virtuel gestuel
- [ ] Gestes personnalisables

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

---

## 📄 Licence

MIT License - Voir le fichier `LICENSE` pour plus de détails.

---

## 🙏 Remerciements

- **MediaPipe** (Google) pour la détection de mains
- **Flet** pour le framework GUI Python
- **Charm** (Bubble Tea) pour la TUI Go
- **PyO3** pour l'intégration Rust-Python
