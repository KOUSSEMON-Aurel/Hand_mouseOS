# -*- coding: utf-8 -*-
"""
Data Models - Classes de données partagées
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class GestureType(Enum):
    """Types de gestes reconnus"""
    UNKNOWN = "UNKNOWN"
    POINTING = "POINTING"
    PINCH = "PINCH"
    PALM = "PALM"
    FIST = "FIST"
    TWO = "TWO"
    PEACE = "PEACE"
    THUMBS_UP = "THUMBS_UP"


class ActionType(Enum):
    """Types d'actions système"""
    NONE = "none"
    MOVE_CURSOR = "move_cursor"
    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    DOUBLE_CLICK = "double_click"
    DRAG_START = "drag_start"
    DRAG_END = "drag_end"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    PLAY_PAUSE = "play_pause"
    COPY = "copy"
    PASTE = "paste"


@dataclass
class Point2D:
    """Point 2D"""
    x: float
    y: float


@dataclass
class Point3D:
    """Point 3D"""
    x: float
    y: float
    z: float


@dataclass
class Landmark:
    """Un landmark MediaPipe"""
    x: float
    y: float
    z: float
    visibility: float = 1.0
    presence: float = 1.0


@dataclass
class GestureResult:
    """Résultat de classification de geste"""
    gesture: GestureType
    confidence: float
    fingers_extended: List[int] = field(default_factory=list)  # [thumb, index, middle, ring, pinky]


@dataclass
class ActionResult:
    """Résultat d'une action à exécuter"""
    action: ActionType
    position: Optional[Tuple[int, int]] = None
    value: float = 0.0  # Pour scroll, volume, etc.
