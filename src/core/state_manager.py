# -*- coding: utf-8 -*-
"""
StateManager - Gestion centralisée de l'état de l'application
Responsabilité unique : Stockage thread-safe de l'état global
"""
import threading
from typing import Optional, List, Any
from dataclasses import dataclass, field
from enum import Enum


class AppMode(Enum):
    """Modes de fonctionnement de l'application"""
    IDLE = "idle"
    CURSOR = "cursor"
    MEDIA = "media"
    WINDOWS = "windows"
    SHORTCUTS = "shortcuts"
    ASL = "asl"
    KEYBOARD = "keyboard"


@dataclass
class HandData:
    """Données d'une main détectée"""
    landmarks: Any = None
    world_landmarks: Any = None
    handedness: str = "Right"
    gesture: str = "UNKNOWN"
    confidence: float = 0.0


@dataclass
class AppState:
    """État complet de l'application"""
    # Flags de contrôle
    is_running: bool = True
    is_processing: bool = False
    
    # Mode actuel
    current_mode: AppMode = AppMode.CURSOR
    
    # Données mains
    primary_hand: Optional[HandData] = None
    secondary_hand: Optional[HandData] = None
    
    # Features activées
    asl_enabled: bool = False
    keyboard_enabled: bool = False
    mouse_frozen: bool = False
    
    # Position curseur
    cursor_position: tuple = (0, 0)
    
    # Performance
    current_fps: float = 0.0


class StateManager:
    """Gestionnaire d'état thread-safe"""
    
    def __init__(self):
        self._state = AppState()
        self._lock = threading.RLock()
        self._listeners = []
    
    @property
    def state(self) -> AppState:
        """Accès lecture seule à l'état"""
        with self._lock:
            return self._state
    
    # --- Contrôle ---
    
    @property
    def is_processing(self) -> bool:
        with self._lock:
            return self._state.is_processing
    
    @is_processing.setter
    def is_processing(self, value: bool):
        with self._lock:
            self._state.is_processing = value
    
    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._state.is_running
    
    @is_running.setter
    def is_running(self, value: bool):
        with self._lock:
            self._state.is_running = value
    
    # --- Mode ---
    
    @property
    def current_mode(self) -> AppMode:
        with self._lock:
            return self._state.current_mode
    
    @current_mode.setter
    def current_mode(self, mode: AppMode):
        with self._lock:
            old_mode = self._state.current_mode
            self._state.current_mode = mode
            if old_mode != mode:
                self._notify("mode_changed", mode)
    
    # --- Mains ---
    
    def update_hands(self, hand_landmarks, world_landmarks, handedness_list):
        """Met à jour les données des mains détectées"""
        with self._lock:
            if not hand_landmarks:
                self._state.primary_hand = None
                self._state.secondary_hand = None
                return
            
            # Première main = primaire
            self._state.primary_hand = HandData(
                landmarks=hand_landmarks[0] if hand_landmarks else None,
                world_landmarks=world_landmarks[0] if world_landmarks else None,
                handedness=handedness_list[0].classification[0].label if handedness_list else "Right"
            )
            
            # Deuxième main = secondaire
            if len(hand_landmarks) > 1:
                self._state.secondary_hand = HandData(
                    landmarks=hand_landmarks[1],
                    world_landmarks=world_landmarks[1] if len(world_landmarks) > 1 else None,
                    handedness=handedness_list[1].classification[0].label if len(handedness_list) > 1 else "Left"
                )
            else:
                self._state.secondary_hand = None
    
    def update_gesture(self, gesture: str, confidence: float = 1.0):
        """Met à jour le geste détecté pour la main primaire"""
        with self._lock:
            if self._state.primary_hand:
                self._state.primary_hand.gesture = gesture
                self._state.primary_hand.confidence = confidence
                self._notify("gesture_detected", gesture)
    
    # --- Features ---
    
    @property
    def asl_enabled(self) -> bool:
        with self._lock:
            return self._state.asl_enabled
    
    @asl_enabled.setter
    def asl_enabled(self, value: bool):
        with self._lock:
            self._state.asl_enabled = value
    
    @property
    def keyboard_enabled(self) -> bool:
        with self._lock:
            return self._state.keyboard_enabled
    
    @keyboard_enabled.setter
    def keyboard_enabled(self, value: bool):
        with self._lock:
            self._state.keyboard_enabled = value
    
    # --- Listeners ---
    
    def add_listener(self, callback):
        """Ajoute un listener pour les changements d'état"""
        self._listeners.append(callback)
    
    def _notify(self, event: str, data):
        """Notifie les listeners d'un changement"""
        for listener in self._listeners:
            try:
                listener(event, data)
            except Exception as e:
                print(f"Listener error: {e}")
