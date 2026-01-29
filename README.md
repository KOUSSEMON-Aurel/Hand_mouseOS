# 🖐️ Hand Mouse OS

**Contrôlez votre ordinateur avec vos mains grâce à l'IA.**

Hand Mouse OS est un système de contrôle gestuel avancé qui transforme votre webcam en interface de contrôle. Déplacez le curseur, cliquez, et exécutez des actions complexes simplement avec vos mains.

![Version](https://img.shields.io/badge/version-2.1-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ✨ Fonctionnalités

- 🎯 **Contrôle de souris haute précision** avec filtrage Rust ultra-rapide (0.0006ms)
- 🖐️ **Détection multi-mains** (2 mains simultanées)
- 🎨 **Interface futuriste** avec dashboard Flet
- 🧠 **Reconnaissance de gestes** (Paume ouverte, Poing, Pointage, Peace)
- ⚡ **GPU/CPU automatique** avec fallback intelligent
- 📹 **Flux vidéo AR temps réel** avec overlay squelettique

---

## 📋 Prérequis

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3.10 python3-pip python3-venv
sudo apt install -y libgtk-3-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt install -y v4l-utils  # Pour la webcam
```

### Windows

1. **Python 3.10+** : [Télécharger ici](https://www.python.org/downloads/)
2. **Microsoft Visual C++ Redistributable** : [Télécharger ici](https://aka.ms/vs/17/release/vc_redist.x64.exe)
3. **Webcam compatible** (intégrée ou USB)

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/Hand_mouseOS.git
cd Hand_mouseOS
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
```

### 3. Activer l'environnement

**Linux/macOS :**

```bash
source venv/bin/activate
```

**Windows (PowerShell) :**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD) :**

```cmd
venv\Scripts\activate.bat
```

### 4. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Compiler la bibliothèque Rust (Optionnel mais recommandé)

```bash
cd hand_mouse_core
cargo build --release
maturin develop --release
cd ..
```

---

## 🎮 Lancement

### Linux

```bash
chmod +x master_run.sh
./master_run.sh
```

> **Note** : Le script configure automatiquement les permissions `uinput` pour un contrôle souris au niveau kernel.

### Windows

```powershell
python main.py
```

---

## 🎯 Utilisation

1. **Lancez l'application** (voir section ci-dessus)
2. **Interface Dashboard** : Une fenêtre Flet s'ouvre
3. **Cliquez sur "Start System"** : La détection démarre
4. **Contrôlez avec vos mains** :
   - **Index levé** : Déplace le curseur
   - **Index + Pouce rapprochés** : Clic gauche
   - **Paume ouverte** : Mode Pilotage (curseur suit l'index)
   - **Poing** : Clic maintenu ou scroll

5. **Paramètres** : Ajustez la sensibilité dans l'onglet "Paramètres"

---

## 🛠️ Configuration Avancée

### Permissions Linux (Manuel)

Si `master_run.sh` ne fonctionne pas automatiquement :

```bash
sudo modprobe uinput
sudo chmod 666 /dev/uinput
```

Pour rendre permanent :

```bash
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf
echo 'KERNEL=="uinput", MODE="0666"' | sudo tee /etc/udev/rules.d/99-uinput.rules
```

### Changer de caméra

Si votre webcam n'est pas détectée automatiquement, éditez `src/engine.py` ligne 174 :

```python
for cam_idx in range(5):  # Augmentez si vous avez plus de caméras
```

---

## 📁 Structure du Projet

```
Hand_mouseOS/
├── assets/                  # Modèles IA (MediaPipe)
├── gui/                     # Ancienne tentative Svelte (non utilisée)
├── hand_mouse_core/         # Filtrage Rust haute performance
├── src/                     # Code source Python
│   ├── engine.py           # Moteur IA principal
│   ├── gui.py              # Interface Flet
│   ├── mouse_driver.py     # Contrôle souris (uinput/PyAutoGUI)
│   ├── advanced_filter.py  # Filtres de lissage
│   └── gesture_classifier.py  # Reconnaissance de gestes
├── main.py                  # Point d'entrée
├── master_run.sh            # Lanceur Linux
└── requirements.txt         # Dépendances Python
```

---

## 🐛 Dépannage

### Linux : "No working camera found"

```bash
ls /dev/video*  # Vérifiez que votre webcam est détectée
v4l2-ctl --list-devices  # Listez les périphériques vidéo
```

### Windows : Erreur DLL MediaPipe

Installez Visual C++ Redistributable (voir Prérequis).

### Interface Flet ne s'ouvre pas

```bash
pip install --upgrade flet
```

### Latence élevée

Activez le mode GPU dans les paramètres (si compatible).

---

## 📝 Roadmap

- [ ] Reconnaissance de signes (alphabet)
- [ ] Clavier virtuel gestuel
- [ ] Support macOS natif
- [ ] Gestes personnalisables
- [ ] Mode multi-écrans

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
- **PyAutoGUI** et **python-uinput** pour le contrôle souris
