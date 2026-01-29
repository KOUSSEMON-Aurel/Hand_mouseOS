"""
Module d'overlay de feedback temps réel.

Affiche un overlay discret sur la fenêtre native OpenCV avec :
- Mode actuel
- Geste détecté
- Action en cours
- Indicateur de confiance
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class FeedbackOverlay:
    """Affiche un overlay de feedback sur les frames OpenCV."""
    
    # Couleurs par mode (BGR)
    MODE_COLORS = {
        "cursor": (255, 255, 0),    # Cyan
        "window": (255, 0, 255),    # Magenta
        "media": (0, 255, 0),       # Vert
        "shortcut": (0, 255, 255),  # Jaune
    }
    
    # Emojis textuels (car OpenCV ne supporte pas les vrais emojis)
    GESTURE_ICONS = {
        "POINTING": "[^]",
        "PINCH": "(O)",
        "PALM": "[=]",
        "FIST": "[#]",
        "TWO_FINGERS": "[V]",
        "UNKNOWN": "[?]",
    }
    
    MODE_NAMES = {
        "cursor": "CURSEUR",
        "window": "FENETRES",
        "media": "MULTIMEDIA",
        "shortcut": "RACCOURCIS",
    }
    
    def __init__(self, position: str = "top_left"):
        """
        Args:
            position: Position de l'overlay ('top_left', 'top_right', 'bottom_left', 'bottom_right')
        """
        self.position = position
        self._confidence = 0.0
        self._last_action = "Aucune"
        
    def draw(
        self,
        frame: np.ndarray,
        mode: str,
        gesture: str,
        action: str = "",
        confidence: float = 1.0
    ) -> np.ndarray:
        """
        Dessine l'overlay sur la frame.
        
        Args:
            frame: Image OpenCV (BGR)
            mode: Mode contextuel actif
            gesture: Geste détecté
            action: Action en cours (optionnel)
            confidence: Score de confiance 0-1
            
        Returns:
            Frame avec overlay dessiné
        """
        h, w = frame.shape[:2]
        
        # Dimensions de l'overlay
        overlay_w = 220
        overlay_h = 100
        margin = 10
        
        # Position selon configuration
        if self.position == "top_left":
            x, y = margin, margin
        elif self.position == "top_right":
            x, y = w - overlay_w - margin, margin
        elif self.position == "bottom_left":
            x, y = margin, h - overlay_h - margin
        else:  # bottom_right
            x, y = w - overlay_w - margin, h - overlay_h - margin
        
        # Couleur du mode
        mode_color = self.MODE_COLORS.get(mode.lower(), (200, 200, 200))
        
        # Fond semi-transparent
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + overlay_w, y + overlay_h), (30, 30, 35), -1)
        cv2.rectangle(overlay, (x, y), (x + overlay_w, y + overlay_h), mode_color, 2)
        
        # Blend avec la frame originale
        alpha = 0.85
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Texte : Mode
        mode_name = self.MODE_NAMES.get(mode.lower(), mode.upper())
        cv2.putText(frame, f"Mode: {mode_name}", (x + 10, y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, mode_color, 1, cv2.LINE_AA)
        
        # Texte : Geste
        gesture_icon = self.GESTURE_ICONS.get(gesture.upper(), "[?]")
        cv2.putText(frame, f"Geste: {gesture_icon} {gesture} ({getattr(self, 'debug_raw_gesture', '')})", (x + 10, y + 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
        # Texte : Action (si fournie)
        if action:
            cv2.putText(frame, f"Action: {action}", (x + 10, y + 75), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
        
        # Barre de confiance
        conf_bar_y = y + overlay_h - 15
        conf_bar_w = int((overlay_w - 20) * confidence)
        cv2.rectangle(frame, (x + 10, conf_bar_y), (x + 10 + overlay_w - 20, conf_bar_y + 8), (50, 50, 50), -1)
        cv2.rectangle(frame, (x + 10, conf_bar_y), (x + 10 + conf_bar_w, conf_bar_y + 8), mode_color, -1)
        
        return frame
    
    def draw_zone_indicators(
        self,
        frame: np.ndarray,
        current_mode: str
    ) -> np.ndarray:
        """
        Dessine les indicateurs de zones d'écran.
        
        Args:
            frame: Image OpenCV
            current_mode: Mode actif pour le highlighting
            
        Returns:
            Frame avec indicateurs
        """
        h, w = frame.shape[:2]
        
        # Zones (semi-transparentes)
        overlay = frame.copy()
        
        # Zone Media (top 20%)
        media_h = int(h * 0.20)
        if current_mode.lower() == "media":
            cv2.rectangle(overlay, (0, 0), (w, media_h), (0, 255, 0), -1)
            cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)
            cv2.putText(frame, "MEDIA ZONE", (w//2 - 50, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Zones fenêtres (bords 10%)
        edge_w = int(w * 0.10)
        if current_mode.lower() == "window":
            # Bord gauche
            cv2.rectangle(overlay, (0, media_h), (edge_w, h), (255, 0, 255), -1)
            # Bord droit
            cv2.rectangle(overlay, (w - edge_w, media_h), (w, h), (255, 0, 255), -1)
            cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)
        
        return frame
    
    def draw_hand_halo(
        self,
        frame: np.ndarray,
        hand_pos: Tuple[int, int],
        mode: str,
        radius: int = 40
    ) -> np.ndarray:
        """
        Dessine un halo coloré autour de la main.
        
        Args:
            frame: Image OpenCV
            hand_pos: Position (x, y) en pixels
            mode: Mode actif pour la couleur
            radius: Rayon du halo
            
        Returns:
            Frame avec halo
        """
        color = self.MODE_COLORS.get(mode.lower(), (200, 200, 200))
        
        # Halo extérieur (semi-transparent)
        overlay = frame.copy()
        cv2.circle(overlay, hand_pos, radius, color, 3)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Point central
        cv2.circle(frame, hand_pos, 5, color, -1)
        
        return frame
