# 🗺️ Plan d'Amélioration & Optimisation

Ce document détaille les pistes d'amélioration pour **Hand Mouse OS**, basées sur les modules déjà prototypés dans `hand_mouse_optimized_implementations.py`.

## 1. 🚀 Optimisations Immédiates (Quick Wins)

Ces modifications peuvent être intégrées rapidement dans `src/engine.py` et donneront des gains immédiats.

### A. Filtrage Adaptatif (Anti-Tremblement Intelligent)

* **Problème Actuel :** Le `OneEuroFilter` a des paramètres fixes (`beta`, `min_cutoff`). Si on bouge vite, ça peut laguer. Si on est lent, ça tremble.
* **Solution :** Intégrer `AdaptiveOneEuroFilter`.
* **Principe :** Ajuste dynamiquement le filtrage selon la vitesse de la main.
  * *Mouvement Rapide* -> Filtrage faible (Max réactivité).
  * *Mouvement Lent/Arrêt* -> Filtrage fort (Max précision, curseur immobile).
* **Code prêt :** Classe `AdaptiveOneEuroFilter` (lignes 126-233).

### B. Configuration Caméra (V4L2)

* **Problème Actuel :** La webcam est en mode "Auto". En basse lumière, le temps d'exposition augmente -> Flou de mouvement (Motion Blur) -> MediaPipe perd la main.
* **Solution :** Forcer les réglages via `v4l2-ctl` au démarrage.
* **Action :**
  * Désactiver Auto-Focus (fixe à l'infini).
  * Réduire l'Exposition (image plus sombre mais plus nette en mouvement).
  * Augmenter le Gain (compense la baisse d'exposition).
* **Code prêt :** Classe `CameraConfigurator` (lignes 238-340).

---

## 2. ✨ Nouvelles Fonctionnalités (Ux)

### A. Calibration 4-Points

* **Problème :** La zone de la caméra (16:9) ne correspond pas toujours à mon envie de mouvement. Je dois tendre le bras trop loin pour atteindre les coins.
* **Solution :** Système de calibration.
* **Fonctionnement :** L'utilisateur clique sur les 4 coins de **sa** zone de confort dans l'air. Le système mappe cette zone restreinte à tout l'écran.
* **Code prêt :** Classe `CalibrationSystem` (lignes 527-594).

### B. "Dwell Click" (Clic par Maintien)

* **Problème :** Le geste de "Pince" (Pinch) peut être fatiguant ou faire bouger le curseur au moment du clic.
* **Solution :** Clic automatique quand on reste immobile sur une cible pendant X millisecondes.
* **Code prêt :** Classe `DwellClickDetector` (lignes 394-448).

---

## 3. 🏎️ Performance & Hardware (Long Terme)

### A. GPU Acceleration (Delegate)

* **Constat :** MediaPipe tourne sur CPU (~30 FPS max).
* **Piste :** Recompiler/Configurer MediaPipe pour utiliser le **GPU Delegate** (OpenCL ou Vulkan).
* **Gain espéré :** 60 FPS constants avec < 10% CPU.

### B. Pipeline GStreamer

* **Constat :** `cv2.VideoCapture(0)` utilise le backend par défaut (souvent V4L2 lent).
* **Piste :** Utiliser un pipeline GStreamer natif pour récupérer le flux MJPEG brut de la caméra sans conversion CPU coûteuse.
* **Code prêt :** `create_optimized_capture` (lignes 309-326).

---

## 4. 📅 Planning d'Intégration Proposé

1. **Phase 1 (Stabilisation)** : Remplacer `mouse_driver.py` par sa version `OptimizedMouseDriver` avec `AdaptiveOneEuroFilter`.
2. **Phase 2 (Vision)** : Intégrer `CameraConfigurator` au démarrage de `HandEngine`.
3. **Phase 3 (Fonctionnel)** : Ajouter un bouton "Calibrer" dans l'interface Flet qui déclenche la routine de calibration.

---
*Ce plan est basé sur l'analyse du code existant dans le dossier `amelioration/`.*
