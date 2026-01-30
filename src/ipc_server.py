"""
IPC Server - Serveur de communication inter-processus pour Hand Mouse OS
Permet au CLI Go de contrôler l'engine Python via socket UNIX
"""
import socket
import json
import threading
import os
from pathlib import Path


class IPCServer:
    SOCKET_PATH = "/tmp/handmouse.sock"
    
    def __init__(self, engine):
        self.engine = engine
        self.socket = None
        self.running = False
        self.thread = None
    
    def start(self):
        """Démarre le serveur IPC"""
        # Supprimer le socket s'il existe déjà
        if os.path.exists(self.SOCKET_PATH):
            os.unlink(self.SOCKET_PATH)
        
        # Créer le socket UNIX
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.SOCKET_PATH)
        self.socket.listen(1)
        
        self.running = True
        self.thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Arrête le serveur IPC"""
        self.running = False
        if self.socket:
            self.socket.close()
        if os.path.exists(self.SOCKET_PATH):
            os.unlink(self.SOCKET_PATH)
    
    def _accept_loop(self):
        """Boucle d'acceptation des connexions"""
        while self.running:
            try:
                conn, _ = self.socket.accept()
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except:
                break
    
    def _handle_client(self, conn):
        """Gère une connexion client"""
        try:
            data = conn.recv(4096).decode('utf-8')
            if not data:
                return
            
            # Parser la commande JSON
            command = json.loads(data)
            response = self._execute_command(command)
            
            # Envoyer la réponse
            conn.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            error_response = {"status": "error", "message": str(e)}
            conn.sendall(json.dumps(error_response).encode('utf-8'))
        finally:
            conn.close()
    
    def _execute_command(self, command):
        """Exécute une commande et retourne la réponse"""
        cmd_type = command.get("command")
        
        if cmd_type == "get_status":
            return {
                "status": "ok",
                "data": {
                    "is_processing": self.engine.is_processing,
                    "asl_enabled": self.engine.asl_enabled,
                    "fps": getattr(self.engine, 'fps', 0)
                }
            }
        
        elif cmd_type == "toggle_asl":
            self.engine.asl_enabled = not self.engine.asl_enabled
            return {"status": "ok", "asl_enabled": self.engine.asl_enabled}
        
        elif cmd_type == "set_asl":
            value = command.get("value", False)
            self.engine.asl_enabled = value
            return {"status": "ok", "asl_enabled": self.engine.asl_enabled}
        
        elif cmd_type == "start":
            self.engine.start()
            return {"status": "ok", "message": "Engine started"}
        
        elif cmd_type == "stop":
            self.engine.stop()
            return {"status": "ok", "message": "Engine stopped"}
        
        else:
            return {"status": "error", "message": f"Unknown command: {cmd_type}"}
