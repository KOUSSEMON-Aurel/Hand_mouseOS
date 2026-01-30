import pytest
from unittest.mock import patch

@pytest.fixture
def mock_engine():
    # Mock des dépendances lourdes pour éviter l'init matérielle
    with patch('src.engine.MouseDriver'), \
         patch('src.engine.HybridMouseFilter'), \
         patch('src.engine.StaticGestureClassifier'), \
         patch('src.engine.ContextModeDetector'), \
         patch('src.engine.ActionDispatcher'), \
         patch('src.engine.FeedbackOverlay'), \
         patch('src.engine.VirtualKeyboard'), \
         patch('src.engine.ASLManager'), \
         patch('src.engine.PerformanceProfiler'), \
         patch('cv2.VideoCapture'):
        
        from src.engine import HandEngine
        engine = HandEngine(headless=True)
        # On empêche le thread de tourner réellement pour les tests unitaires simples
        engine.running = False 
        return engine

def test_engine_initialization(mock_engine):
    """Vérifie que l'engine s'initialise avec les bonnes valeurs par défaut."""
    assert mock_engine.headless is True
    assert mock_engine.is_processing is False
    assert mock_engine.camera_index == 0
    assert mock_engine.keyboard_enabled is False

def test_engine_start_stop(mock_engine):
    """Vérifie le basculement de l'état processing."""
    mock_engine.start()
    assert mock_engine.is_processing is True
    
    mock_engine.stop()
    assert mock_engine.is_processing is False

def test_engine_set_camera(mock_engine):
    """Vérifie que le changement de caméra réinitialise la capture."""
    mock_engine.cap = MagicMock() # Simule une capture ouverte
    
    mock_engine.set_camera(1)
    assert mock_engine.camera_index == 1
    assert mock_engine.cap is None # Doit être libéré pour ré-init
