# -*- coding: utf-8 -*-
"""
EventBus - Système de communication inter-modules
Responsabilité unique : Pub/Sub asynchrone pour événements
"""
from typing import Callable, Dict, List, Any
from enum import Enum, auto
import threading
from queue import Queue, Empty


class EventType(Enum):
    """Types d'événements du système"""
    # Vision
    HAND_DETECTED = auto()
    HAND_LOST = auto()
    GESTURE_DETECTED = auto()
    
    # Mode
    MODE_CHANGED = auto()
    
    # Actions
    ACTION_TRIGGERED = auto()
    MOUSE_MOVED = auto()
    CLICK_PERFORMED = auto()
    
    # Système
    ENGINE_STARTED = auto()
    ENGINE_STOPPED = auto()
    ERROR_OCCURRED = auto()
    
    # ASL
    ASL_SIGN_DETECTED = auto()
    ASL_ENABLED = auto()
    ASL_DISABLED = auto()
    
    # Keyboard
    KEY_PRESSED = auto()
    KEYBOARD_ENABLED = auto()
    KEYBOARD_DISABLED = auto()


class EventBus:
    """Bus d'événements thread-safe avec support async"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._async_queue: Queue = Queue()
        self._lock = threading.RLock()
        self._initialized = True
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """S'abonne à un type d'événement"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Se désabonne d'un type d'événement"""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                except ValueError:
                    pass
    
    def publish(self, event_type: EventType, data: Any = None):
        """Publie un événement de manière synchrone"""
        with self._lock:
            subscribers = self._subscribers.get(event_type, []).copy()
        
        for callback in subscribers:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"EventBus error in {callback.__name__}: {e}")
    
    def publish_async(self, event_type: EventType, data: Any = None):
        """Publie un événement dans la queue async"""
        self._async_queue.put((event_type, data))
    
    def process_async_events(self, max_events: int = 10):
        """Traite les événements en attente"""
        processed = 0
        while processed < max_events:
            try:
                event_type, data = self._async_queue.get_nowait()
                self.publish(event_type, data)
                processed += 1
            except Empty:
                break
    
    def clear_all(self):
        """Supprime tous les abonnements"""
        with self._lock:
            self._subscribers.clear()
    
    def subscriber_count(self, event_type: EventType) -> int:
        """Compte les abonnés pour un type d'événement"""
        with self._lock:
            return len(self._subscribers.get(event_type, []))


# Instance globale (Singleton)
event_bus = EventBus()
