import flet as ft
from gui import main as gui_main

if __name__ == "__main__":
    # Flet 0.80+ recommends ft.app(target=...). 
    # The warning "Use run() instead" might refer to flet 1.0 changes or internal app() structure, 
    # but strictly speaking ft.app() is the main entry point for desktop.
    ft.app(target=gui_main)
