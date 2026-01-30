#!/usr/bin/env python3
"""
Headless Runner - Lance l'engine Hand Mouse OS sans interface Flet
"""
import sys
import signal
import time
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent))

from engine import HandEngine
from ipc_server import IPCServer


class HeadlessRunner:
    def __init__(self, show_video=True):
        self.show_video = show_video
        self.engine = None
        self.ipc_server = None
        self.running = True
        
        # Gérer les signaux pour arrêt propre
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Arrêt propre sur SIGINT/SIGTERM"""
        print("\n⏹️  Arrêt en cours...")
        self.running = False
        if self.engine:
            self.engine.stop()
        if self.ipc_server:
            self.ipc_server.stop()
        sys.exit(0)
    
    def run(self):
        """Lance l'engine en mode headless"""
        print("🚀 Hand Mouse OS - Mode Headless")
        print(f"📹 Vidéo: {'Activée' if self.show_video else 'Désactivée'}")
        
        # Créer l'engine
        self.engine = HandEngine()
        
        # Démarrer le serveur IPC
        self.ipc_server = IPCServer(self.engine)
        self.ipc_server.start()
        print("🔌 Serveur IPC démarré sur /tmp/handmouse.sock")
        
        # Démarrer l'engine
        self.engine.start()
        print("✅ Engine démarré")
        
        # Boucle principale
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._signal_handler(None, None)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hand Mouse OS - Mode Headless")
    parser.add_argument("--no-video", action="store_true", help="Désactive l'affichage vidéo")
    args = parser.parse_args()
    
    runner = HeadlessRunner(show_video=not args.no_video)
    runner.run()
