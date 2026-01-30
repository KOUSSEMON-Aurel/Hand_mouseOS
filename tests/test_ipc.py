import pytest
import json
import socket
import os
import threading
import time
from unittest.mock import MagicMock
from src.ipc_server import IPCServer

@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.is_processing = True
    engine.asl_enabled = False
    return engine

def test_ipc_command_execution(mock_engine):
    """Teste la logique de traitement des commandes sans socket réel."""
    server = IPCServer(mock_engine)
    
    # Test get_status
    resp = server._execute_command({"command": "get_status"})
    assert resp["status"] == "ok"
    assert resp["data"]["is_processing"] is True
    
    # Test toggle_asl
    resp = server._execute_command({"command": "set_asl", "value": True})
    assert resp["status"] == "ok"
    mock_engine.asl_enabled = True # Setter mocké
    
    # Test start/stop
    server._execute_command({"command": "start"})
    mock_engine.start.assert_called_once()
    
    server._execute_command({"command": "stop"})
    mock_engine.stop.assert_called_once()

def test_ipc_invalid_command(mock_engine):
    """Vérifie la réponse d'erreur pour une commande inconnue."""
    server = IPCServer(mock_engine)
    resp = server._execute_command({"command": "invalid_cmd"})
    assert resp["status"] == "error"
    assert "Unknown command" in resp["message"]
