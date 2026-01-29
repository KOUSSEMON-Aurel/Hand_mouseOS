"""
Module de détection des modes contextuels.

Le système devine automatiquement ce que l'utilisateur veut faire
selon la position de sa main et le contexte.
"""

from enum import Enum
from typing import Tuple, Optional
import time


class ContextMode(Enum):
    """Les 4 modes contextuels du système simplifié."""
    CURSOR = "cursor"      # Défaut - contrôle souris
    WINDOW = "window"      # Près des bords - gestion fenêtres
    MEDIA = "media"        # Zone haute - multimédia
    SHORTCUT = "shortcut"  # Main gauche fixe - raccourcis clavier


class ContextModeDetector:
    """Détecteur de mode contextuel basé sur la position de la main."""
    
    # Configuration des zones (en pourcentage de l'écran)
    MEDIA_ZONE_TOP = 0.20      # Tiers supérieur = zone média
    WINDOW_EDGE_MARGIN = 0.10  # 10% des bords = zone fenêtre
    
    # Seuils pour le mode SHORTCUT
    SHORTCUT_HOLD_TIME = 0.8   # Secondes de maintien main gauche fixe
    SHORTCUT_MOVE_THRESHOLD = 0.03  # Mouvement max pour considérer "fixe"
    
    def __init__(self):
        self._left_hand_history = []  # Historique positions main gauche
        self._left_hand_gesture_time = 0  # Timestamp début geste main gauche
        self._current_mode = ContextMode.CURSOR
        
    def detect_mode(
        self, 
        hand_pos: Tuple[float, float],  # Position normalisée (0-1)
        left_hand_gesture: Optional[str] = None,
        left_hand_pos: Optional[Tuple[float, float]] = None
    ) -> ContextMode:
        """
        Détecte le mode contextuel basé sur la position de la main.
        
        Args:
            hand_pos: Position (x, y) normalisée de la main dominante (0-1)
            left_hand_gesture: Geste détecté sur la main secondaire (gauche)
            left_hand_pos: Position de la main secondaire
            
        Returns:
            ContextMode: Le mode contextuel approprié
        """
        x, y = hand_pos
        
        # 1. SHORTCUT: Main gauche en FIST maintenu
        if self._check_shortcut_mode(left_hand_gesture, left_hand_pos):
            self._current_mode = ContextMode.SHORTCUT
            return ContextMode.SHORTCUT
        
        # Reset shortcut timer si conditions non remplies
        if left_hand_gesture != "FIST":
            self._left_hand_gesture_time = 0
        
        # 2. MEDIA: Main dans la zone supérieure
        if y < self.MEDIA_ZONE_TOP:
            self._current_mode = ContextMode.MEDIA
            return ContextMode.MEDIA
        
        # 3. WINDOW: Main près des bords de l'écran
        near_left = x < self.WINDOW_EDGE_MARGIN
        near_right = x > (1 - self.WINDOW_EDGE_MARGIN)
        near_bottom = y > (1 - self.WINDOW_EDGE_MARGIN)
        
        if near_left or near_right or near_bottom:
            self._current_mode = ContextMode.WINDOW
            return ContextMode.WINDOW
        
        # 4. CURSOR: Mode par défaut
        self._current_mode = ContextMode.CURSOR
        return ContextMode.CURSOR
    
    def _check_shortcut_mode(
        self, 
        left_hand_gesture: Optional[str],
        left_hand_pos: Optional[Tuple[float, float]]
    ) -> bool:
        """Vérifie si les conditions du mode SHORTCUT sont remplies."""
        
        if left_hand_gesture != "FIST" or left_hand_pos is None:
            return False
        
        now = time.time()
        
        # Première détection du geste
        if self._left_hand_gesture_time == 0:
            self._left_hand_gesture_time = now
            self._left_hand_history = [left_hand_pos]
            return False
        
        # Vérifier la stabilité de la position
        self._left_hand_history.append(left_hand_pos)
        if len(self._left_hand_history) > 10:
            self._left_hand_history.pop(0)
        
        # Calculer le mouvement moyen
        if len(self._left_hand_history) >= 2:
            total_movement = 0
            for i in range(1, len(self._left_hand_history)):
                prev = self._left_hand_history[i-1]
                curr = self._left_hand_history[i]
                dx = abs(curr[0] - prev[0])
                dy = abs(curr[1] - prev[1])
                total_movement += (dx + dy)
            avg_movement = total_movement / (len(self._left_hand_history) - 1)
            
            # Main pas assez stable
            if avg_movement > self.SHORTCUT_MOVE_THRESHOLD:
                self._left_hand_gesture_time = now
                return False
        
        # Vérifier le temps de maintien
        hold_duration = now - self._left_hand_gesture_time
        return hold_duration >= self.SHORTCUT_HOLD_TIME
    
    def get_mode_info(self) -> dict:
        """Retourne les informations sur le mode actuel."""
        mode_info = {
            ContextMode.CURSOR: {
                "name": "Curseur",
                "emoji": "🖱️",
                "description": "Contrôle de la souris",
                "color": "#00FFFF"  # Cyan
            },
            ContextMode.WINDOW: {
                "name": "Fenêtres",
                "emoji": "🪟",
                "description": "Gestion des fenêtres",
                "color": "#FF00FF"  # Magenta
            },
            ContextMode.MEDIA: {
                "name": "Multimédia",
                "emoji": "🎵",
                "description": "Contrôle lecture audio/vidéo",
                "color": "#00FF00"  # Vert
            },
            ContextMode.SHORTCUT: {
                "name": "Raccourcis",
                "emoji": "⌨️",
                "description": "Raccourcis clavier (Ctrl+...)",
                "color": "#FFFF00"  # Jaune
            }
        }
        return mode_info.get(self._current_mode, mode_info[ContextMode.CURSOR])
    
    @property
    def current_mode(self) -> ContextMode:
        return self._current_mode
