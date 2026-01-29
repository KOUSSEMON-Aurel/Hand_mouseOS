# -*- coding: utf-8 -*-
"""
Tests unitaires pour les modules core
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.state_manager import StateManager, AppMode, HandData
from src.core.event_bus import EventBus, EventType


class TestStateManager:
    """Tests pour StateManager"""
    
    def test_initial_state(self):
        """État initial correct"""
        sm = StateManager()
        assert sm.is_running == True
        assert sm.is_processing == False
        assert sm.current_mode == AppMode.CURSOR
    
    def test_processing_toggle(self):
        """Toggle processing fonctionne"""
        sm = StateManager()
        
        sm.is_processing = True
        assert sm.is_processing == True
        
        sm.is_processing = False
        assert sm.is_processing == False
    
    def test_mode_change(self):
        """Changement de mode fonctionne"""
        sm = StateManager()
        
        sm.current_mode = AppMode.MEDIA
        assert sm.current_mode == AppMode.MEDIA
        
        sm.current_mode = AppMode.ASL
        assert sm.current_mode == AppMode.ASL
    
    def test_asl_toggle(self):
        """Toggle ASL"""
        sm = StateManager()
        
        assert sm.asl_enabled == False
        sm.asl_enabled = True
        assert sm.asl_enabled == True


class TestEventBus:
    """Tests pour EventBus"""
    
    def test_singleton(self):
        """EventBus est un singleton"""
        bus1 = EventBus()
        bus2 = EventBus()
        assert bus1 is bus2
    
    def test_subscribe_publish(self):
        """Subscribe et publish fonctionnent"""
        bus = EventBus()
        received = []
        
        def handler(event_type, data):
            received.append((event_type, data))
        
        bus.subscribe(EventType.GESTURE_DETECTED, handler)
        bus.publish(EventType.GESTURE_DETECTED, "PINCH")
        
        assert len(received) == 1
        assert received[0][1] == "PINCH"
        
        # Cleanup
        bus.unsubscribe(EventType.GESTURE_DETECTED, handler)
    
    def test_unsubscribe(self):
        """Unsubscribe fonctionne"""
        bus = EventBus()
        received = []
        
        def handler(event_type, data):
            received.append(data)
        
        bus.subscribe(EventType.MODE_CHANGED, handler)
        bus.unsubscribe(EventType.MODE_CHANGED, handler)
        bus.publish(EventType.MODE_CHANGED, "TEST")
        
        assert len(received) == 0
    
    def test_multiple_subscribers(self):
        """Plusieurs subscribers reçoivent l'event"""
        bus = EventBus()
        results = []
        
        def handler1(event_type, data):
            results.append("handler1")
        
        def handler2(event_type, data):
            results.append("handler2")
        
        bus.subscribe(EventType.ENGINE_STARTED, handler1)
        bus.subscribe(EventType.ENGINE_STARTED, handler2)
        bus.publish(EventType.ENGINE_STARTED, None)
        
        assert "handler1" in results
        assert "handler2" in results
        
        # Cleanup
        bus.unsubscribe(EventType.ENGINE_STARTED, handler1)
        bus.unsubscribe(EventType.ENGINE_STARTED, handler2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
