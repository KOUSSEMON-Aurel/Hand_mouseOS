# -*- coding: utf-8 -*-
"""
SkeletonRenderer - Rendu visuel des squelettes de mains
Responsabilité unique : Génération d'images de visualisation
"""
import numpy as np
import cv2
from typing import Optional, Tuple, List


# Connexions MediaPipe
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Pouce
    (0, 5), (5, 6), (6, 7), (7, 8),       # Index
    (5, 9), (9, 10), (10, 11), (11, 12),  # Majeur
    (9, 13), (13, 14), (14, 15), (15, 16),# Annulaire
    (13, 17), (17, 18), (18, 19), (19, 20),# Auriculaire
    (0, 17)                                # Paume
]


class SkeletonRenderer:
    """Génère les visualisations de squelettes de mains"""
    
    def __init__(
        self,
        canvas_size: Tuple[int, int] = (600, 400),
        colors: dict = None
    ):
        self.width, self.height = canvas_size
        self.colors = colors or {
            'right': (0, 255, 0),   # Vert
            'left': (255, 0, 255),  # Magenta
            'bone': (150, 150, 150),
            'joint': (255, 255, 255),
            'grid': (50, 50, 50)
        }
    
    def render_4view(
        self,
        landmarks,
        world_landmarks = None
    ) -> np.ndarray:
        """Génère une vue 4 quadrants (2D + 3 vues 3D)"""
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Lignes de quadrant
        mid_x, mid_y = self.width // 2, self.height // 2
        cv2.line(canvas, (mid_x, 0), (mid_x, self.height), self.colors['grid'], 2)
        cv2.line(canvas, (0, mid_y), (self.width, mid_y), self.colors['grid'], 2)
        
        if landmarks is None:
            cv2.putText(canvas, "WAITING...", (mid_x - 60, mid_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            return canvas
        
        # Quadrant 1: Vue 2D (haut-gauche)
        self._draw_2d_view(canvas, landmarks, 
                          offset=(mid_x // 2, mid_y // 2),
                          scale=150)
        
        if world_landmarks:
            # Quadrant 2: Vue de dessus XZ (haut-droite)
            self._draw_3d_view(canvas, world_landmarks, "top",
                              offset=(mid_x + mid_x // 2, mid_y // 2))
            
            # Quadrant 3: Vue côté gauche ZY (bas-gauche)
            self._draw_3d_view(canvas, world_landmarks, "left",
                              offset=(mid_x // 2, mid_y + mid_y // 2))
            
            # Quadrant 4: Vue côté droit (bas-droite)
            self._draw_3d_view(canvas, world_landmarks, "right",
                              offset=(mid_x + mid_x // 2, mid_y + mid_y // 2))
        
        return canvas
    
    def _draw_2d_view(
        self,
        canvas: np.ndarray,
        landmarks,
        offset: Tuple[int, int],
        scale: float = 150
    ):
        """Dessine la vue 2D screen-space"""
        ox, oy = offset
        points = []
        
        for lm in landmarks:
            x = int(ox + (lm.x - 0.5) * scale)
            y = int(oy + (lm.y - 0.5) * scale)
            points.append((x, y))
        
        self._draw_skeleton(canvas, points, self.colors['right'])
    
    def _draw_3d_view(
        self,
        canvas: np.ndarray,
        world_landmarks,
        view_type: str,
        offset: Tuple[int, int],
        scale: float = 500
    ):
        """Dessine une projection 3D"""
        ox, oy = offset
        points = []
        
        for lm in world_landmarks:
            if view_type == "top":      # XZ plane
                x = int(ox + lm.x * scale)
                y = int(oy - lm.z * scale)
            elif view_type == "left":   # ZY plane
                x = int(ox - lm.z * scale)
                y = int(oy + lm.y * scale)
            else:                       # ZY inverted
                x = int(ox + lm.z * scale)
                y = int(oy + lm.y * scale)
            points.append((x, y))
        
        self._draw_skeleton(canvas, points, self.colors['right'])
    
    def _draw_skeleton(
        self,
        canvas: np.ndarray,
        points: List[Tuple[int, int]],
        color: Tuple[int, int, int]
    ):
        """Dessine le squelette (os + articulations)"""
        # Connexions
        for start_idx, end_idx in HAND_CONNECTIONS:
            if start_idx < len(points) and end_idx < len(points):
                cv2.line(canvas, points[start_idx], points[end_idx], color, 2)
        
        # Articulations
        for pt in points:
            cv2.circle(canvas, pt, 3, self.colors['joint'], -1)
