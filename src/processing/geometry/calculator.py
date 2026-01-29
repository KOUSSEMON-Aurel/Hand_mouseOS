# -*- coding: utf-8 -*-
"""
Geometry Calculator - Wrapper Python pour calculs géométriques Rust
Fallback Python si Rust non disponible
"""
import math
from typing import List, Tuple

# Essaie d'importer le module Rust
try:
    from rust_core import (
        distance_2d as rust_distance_2d,
        distance_3d as rust_distance_3d,
        angle_between_points as rust_angle,
        fingers_extended as rust_fingers,
        palm_center as rust_palm_center,
        pinch_distance as rust_pinch
    )
    RUST_AVAILABLE = True
    print("🦀 Using RUST geometry (optimized)")
except ImportError:
    RUST_AVAILABLE = False
    print("🐍 Using Python geometry (fallback)")


class GeometryCalculator:
    """Calculs géométriques optimisés (Rust + fallback Python)"""
    
    @staticmethod
    def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
        """Distance euclidienne 2D"""
        if RUST_AVAILABLE:
            return rust_distance_2d(x1, y1, x2, y2)
        return math.hypot(x2 - x1, y2 - y1)
    
    @staticmethod
    def distance_3d(x1: float, y1: float, z1: float, 
                    x2: float, y2: float, z2: float) -> float:
        """Distance euclidienne 3D"""
        if RUST_AVAILABLE:
            return rust_distance_3d(x1, y1, z1, x2, y2, z2)
        return math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    
    @staticmethod
    def angle_between_points(
        x1: float, y1: float,
        x2: float, y2: float,
        x3: float, y3: float
    ) -> float:
        """Angle entre 3 points (degrés), angle au point central"""
        if RUST_AVAILABLE:
            return rust_angle(x1, y1, x2, y2, x3, y3)
        
        # Fallback Python
        v1x, v1y = x1 - x2, y1 - y2
        v2x, v2y = x3 - x2, y3 - y2
        dot = v1x * v2x + v1y * v2y
        mag1 = math.hypot(v1x, v1y)
        mag2 = math.hypot(v2x, v2y)
        if mag1 < 1e-6 or mag2 < 1e-6:
            return 0.0
        cos_angle = max(-1.0, min(1.0, dot / (mag1 * mag2)))
        return math.degrees(math.acos(cos_angle))
    
    @staticmethod
    def fingers_extended(landmarks) -> List[int]:
        """Détecte quels doigts sont étendus [thumb, index, middle, ring, pinky]"""
        if len(landmarks) < 21:
            return [0, 0, 0, 0, 0]
        
        # Convertit en tuples si nécessaire
        if hasattr(landmarks[0], 'x'):
            coords = [(lm.x, lm.y, lm.z) for lm in landmarks]
        else:
            coords = landmarks
        
        if RUST_AVAILABLE:
            return list(rust_fingers(coords))
        
        # Fallback Python
        TIPS = [4, 8, 12, 16, 20]
        PIPS = [3, 6, 10, 14, 18]
        
        result = []
        # Pouce
        result.append(1 if coords[TIPS[0]][0] < coords[PIPS[0]][0] else 0)
        # Autres doigts
        for i in range(1, 5):
            result.append(1 if coords[TIPS[i]][1] < coords[PIPS[i]][1] else 0)
        return result
    
    @staticmethod
    def palm_center(landmarks) -> Tuple[float, float, float]:
        """Centre de la paume"""
        if len(landmarks) < 21:
            return (0.0, 0.0, 0.0)
        
        if hasattr(landmarks[0], 'x'):
            coords = [(lm.x, lm.y, lm.z) for lm in landmarks]
        else:
            coords = landmarks
        
        if RUST_AVAILABLE:
            return rust_palm_center(coords)
        
        # Fallback Python
        PALM_INDICES = [0, 5, 9, 13, 17]
        x = sum(coords[i][0] for i in PALM_INDICES) / 5
        y = sum(coords[i][1] for i in PALM_INDICES) / 5
        z = sum(coords[i][2] for i in PALM_INDICES) / 5
        return (x, y, z)
    
    @staticmethod
    def pinch_distance(landmarks) -> float:
        """Distance pouce-index pour détection PINCH"""
        if len(landmarks) < 21:
            return 1.0
        
        if hasattr(landmarks[0], 'x'):
            coords = [(lm.x, lm.y, lm.z) for lm in landmarks]
        else:
            coords = landmarks
        
        if RUST_AVAILABLE:
            return rust_pinch(coords)
        
        # Fallback Python
        thumb = coords[4]
        index = coords[8]
        return GeometryCalculator.distance_3d(
            thumb[0], thumb[1], thumb[2],
            index[0], index[1], index[2]
        )
