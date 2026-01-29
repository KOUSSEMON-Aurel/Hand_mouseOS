"""
Module de dispatch des actions.

Traduit les combinaisons (Geste + Mode + Timing) en actions système.
"""

from enum import Enum
from typing import Callable, Optional, Dict, Tuple
import time


class ActionType(Enum):
    """Types d'actions système."""
    # Souris
    MOVE_CURSOR = "move_cursor"
    CLICK_LEFT = "click_left"
    CLICK_RIGHT = "click_right"
    DRAG_START = "drag_start"
    DRAG_END = "drag_end"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    
    # Fenêtres
    SNAP_LEFT = "snap_left"
    SNAP_RIGHT = "snap_right"
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    MOVE_WINDOW = "move_window"
    SWITCH_WINDOW = "switch_window"
    
    # Multimédia
    PLAY_PAUSE = "play_pause"
    NEXT_TRACK = "next_track"
    PREV_TRACK = "prev_track"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    MUTE = "mute"
    
    # Raccourcis clavier
    COPY = "copy"
    PASTE = "paste"
    CUT = "cut"
    UNDO = "undo"
    
    # Système
    NONE = "none"


class GestureTiming(Enum):
    """Timing du geste pour différencier les actions."""
    QUICK = "quick"       # < 300ms
    HOLD = "hold"         # 300ms - 1s
    LONG = "long"         # > 1s


class ActionDispatcher:
    """Dispatch les actions basées sur Geste + Mode + Timing."""
    
    # Timing thresholds (en secondes)
    QUICK_THRESHOLD = 0.3
    HOLD_THRESHOLD = 1.0
    
    def __init__(self):
        self._gesture_start_time: Dict[str, float] = {}
        self._last_gesture: Optional[str] = None
        self._is_dragging = False
        
        # Table de mapping: (Mode, Geste, Timing) -> Action
        self._action_table = self._build_action_table()
        
    def _build_action_table(self) -> Dict[Tuple, ActionType]:
        """Construit la table de mapping Geste+Mode+Timing → Action."""
        return {
            # ==================== MODE CURSOR ====================
            ("cursor", "POINTING", "quick"): ActionType.MOVE_CURSOR,
            ("cursor", "POINTING", "hold"): ActionType.MOVE_CURSOR,
            ("cursor", "POINTING", "long"): ActionType.MOVE_CURSOR,
            
            ("cursor", "PINCH", "quick"): ActionType.CLICK_LEFT,
            ("cursor", "PINCH", "hold"): ActionType.DRAG_START,
            ("cursor", "PINCH", "long"): ActionType.DRAG_START,
            
            ("cursor", "TWO_FINGERS", "quick"): ActionType.SCROLL_UP,  # Direction via mouvement
            ("cursor", "TWO_FINGERS", "hold"): ActionType.SCROLL_UP,
            
            ("cursor", "FIST", "quick"): ActionType.CLICK_RIGHT,
            ("cursor", "PALM", "quick"): ActionType.MOVE_CURSOR,  # Allow PALM to move cursor too (Usability)
            ("cursor", "PALM", "hold"): ActionType.MOVE_CURSOR,
            ("cursor", "PALM", "long"): ActionType.MOVE_CURSOR,
            
            # ==================== MODE WINDOW ====================
            ("window", "POINTING", "quick"): ActionType.SNAP_LEFT,  # Dépend du bord
            ("window", "POINTING", "hold"): ActionType.SNAP_RIGHT,
            
            ("window", "PALM", "quick"): ActionType.MAXIMIZE,
            ("window", "PALM", "hold"): ActionType.MINIMIZE,
            
            ("window", "FIST", "quick"): ActionType.MOVE_WINDOW,
            ("window", "FIST", "hold"): ActionType.MOVE_WINDOW,
            
            ("window", "TWO_FINGERS", "quick"): ActionType.SWITCH_WINDOW,
            
            # ==================== MODE MEDIA ====================
            ("media", "PALM", "quick"): ActionType.PLAY_PAUSE,
            ("media", "PALM", "hold"): ActionType.MUTE,
            
            ("media", "POINTING", "quick"): ActionType.NEXT_TRACK,  # Dépend direction
            
            ("media", "TWO_FINGERS", "quick"): ActionType.VOLUME_UP,  # Dépend direction
            ("media", "TWO_FINGERS", "hold"): ActionType.VOLUME_DOWN,
            
            ("media", "FIST", "quick"): ActionType.MUTE,
            
            # ==================== MODE SHORTCUT ====================
            ("shortcut", "PINCH", "quick"): ActionType.COPY,
            ("shortcut", "PALM", "quick"): ActionType.PASTE,
            ("shortcut", "TWO_FINGERS", "quick"): ActionType.CUT,
            ("shortcut", "POINTING", "quick"): ActionType.UNDO,
        }
    
    def get_action(
        self, 
        mode: str, 
        gesture: str, 
        gesture_start_time: Optional[float] = None
    ) -> ActionType:
        """
        Détermine l'action à effectuer.
        
        Args:
            mode: Mode contextuel actif ('cursor', 'window', 'media', 'shortcut')
            gesture: Geste détecté ('POINTING', 'PINCH', 'PALM', 'FIST', 'TWO_FINGERS')
            gesture_start_time: Timestamp du début du geste (optionnel)
            
        Returns:
            ActionType: L'action à exécuter
        """
        # Déterminer le timing
        timing = self._get_timing(gesture, gesture_start_time)
        
        # Lookup dans la table
        key = (mode.lower(), gesture.upper(), timing.value)
        action = self._action_table.get(key, ActionType.NONE)
        
        return action
    
    def _get_timing(
        self, 
        gesture: str, 
        gesture_start_time: Optional[float]
    ) -> GestureTiming:
        """Calcule le timing du geste."""
        now = time.time()
        
        # Nouveau geste ou pas de timestamp
        if gesture != self._last_gesture:
            self._gesture_start_time[gesture] = now
            self._last_gesture = gesture
            return GestureTiming.QUICK
        
        # Utiliser le timestamp fourni ou celui stocké
        start = gesture_start_time or self._gesture_start_time.get(gesture, now)
        duration = now - start
        
        if duration < self.QUICK_THRESHOLD:
            return GestureTiming.QUICK
        elif duration < self.HOLD_THRESHOLD:
            return GestureTiming.HOLD
        else:
            return GestureTiming.LONG
    
    def execute_action(self, action: ActionType, **kwargs) -> bool:
        """
        Exécute l'action système.
        
        Args:
            action: L'action à exécuter
            **kwargs: Paramètres additionnels (position, direction, etc.)
            
        Returns:
            bool: True si l'action a été exécutée avec succès
        """
        # Pour l'instant, on log simplement l'action
        # L'implémentation réelle sera connectée au MouseDriver et aux API système
        
        if action == ActionType.NONE:
            return True
        
        # TODO: Implémenter les actions réelles
        # Cette méthode sera appelée par le moteur principal
        
        return True
    
    def get_action_info(self, action: ActionType) -> dict:
        """Retourne les informations sur une action."""
        action_info = {
            ActionType.MOVE_CURSOR: {"name": "Déplacer curseur", "emoji": "🖱️"},
            ActionType.CLICK_LEFT: {"name": "Clic gauche", "emoji": "👆"},
            ActionType.CLICK_RIGHT: {"name": "Clic droit", "emoji": "👉"},
            ActionType.DRAG_START: {"name": "Glisser", "emoji": "✊"},
            ActionType.SCROLL_UP: {"name": "Défiler", "emoji": "📜"},
            ActionType.SNAP_LEFT: {"name": "Snap gauche", "emoji": "⬅️"},
            ActionType.SNAP_RIGHT: {"name": "Snap droite", "emoji": "➡️"},
            ActionType.MAXIMIZE: {"name": "Maximiser", "emoji": "🔲"},
            ActionType.MINIMIZE: {"name": "Minimiser", "emoji": "➖"},
            ActionType.PLAY_PAUSE: {"name": "Play/Pause", "emoji": "⏯️"},
            ActionType.NEXT_TRACK: {"name": "Piste suivante", "emoji": "⏭️"},
            ActionType.VOLUME_UP: {"name": "Volume +", "emoji": "🔊"},
            ActionType.COPY: {"name": "Copier", "emoji": "📋"},
            ActionType.PASTE: {"name": "Coller", "emoji": "📥"},
            ActionType.NONE: {"name": "Aucune", "emoji": "⏸️"},
        }
        return action_info.get(action, {"name": str(action), "emoji": "❓"})
