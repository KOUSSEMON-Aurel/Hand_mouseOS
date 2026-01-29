import flet as ft
from gui import main as gui_main
import os
import sys
import subprocess

def check_and_setup_uinput():
    """Auto-configure uinput if needed"""
    if os.system("test -w /dev/uinput") != 0:
        print("\n🔧 CONFIGURATION UINPUT NECESSAIRE...")
        print("🔒 Mot de passe sudo requis pour activer le contrôle fluide.")
        
        try:
            # Execute the setup script
            # Ensure script is executable
            subprocess.run(["chmod", "+x", "./setup_uinput.sh"], check=True)
            # Run it
            subprocess.run(["./setup_uinput.sh"], check=True)
            print("✅ Configuration UInput terminée. Démarrage...")
        except Exception as e:
            print(f"⚠️ Initialisation auto échouée: {e}")
            print("Le mode 'Secours' (PyAutoGUI) sera utilisé. (La souris ne bougera pas sur Wayland !)\n")

if __name__ == "__main__":
    check_and_setup_uinput()
    
    try:
        os.nice(-10) # High Priority
        print("🚀 Process Priority set to HIGH (-10)")
    except:
        pass
    
    # Flet 0.80+ recommends ft.app(target=...). 
    # The warning "Use run() instead" might refer to flet 1.0 changes or internal app() structure, 
    # but strictly speaking ft.app() is the main entry point for desktop.
    ft.app(target=gui_main)
