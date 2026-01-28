import flet as ft
from engine import HandEngine
from gui import AppGUI
import sys

def main():
    # 1. Init Engine (starts in stopped state)
    print("Initializing Engine...")
    engine = HandEngine()
    
    # 2. Init GUI
    print("Initializing GUI...")
    app_gui = AppGUI(engine)
    
    # 3. Start Flet App
    print("Starting Flet App...")
    # ft.app(target=app_gui.main)
    # Use native running mode
    try:
        # ft.app is deprecated in 0.80 -> ft.run (for script) or flet.app (if flet run)
        # But for script execution "python main.py", ft.app(target=...) used to be the way.
        # Deprecation warning suggests ft.run might be for internal usage, usually it is ft.app(target=...) but let's check docs or use what warning said.
        # Warning said: "Use run() instead." so ft.app() -> ft.run() ? No, flet.app is the entry.
        # Let's try to maintain ft.app but maybe it moved? 
        # Actually for desktop app we should use:
        ft.app(target=app_gui.main) 
    except Exception as e:
        print(f"Error starting app: {e}")
        # Ensure engine is stopped
        engine.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
