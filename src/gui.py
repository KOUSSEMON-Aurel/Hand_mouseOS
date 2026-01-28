import flet as ft
from engine import HandEngine
import base64

class AppGUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Hand_mouseOS"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        # self.page.bgcolor = "#0b0f14" # Dark background from AppShell

        self.img_control = ft.Image(
            src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            width=640,
            height=480,
            fit="contain",
        )
        
        # Engine setup
        self.engine = HandEngine()
        
        self.setup_ui()

    def on_frame(self, b64_str):
        self.img_control.src = f"data:image/jpeg;base64,{b64_str}"
        self.img_control.update()

    def setup_ui(self):
        # --- Sidebar ---
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            # bgcolor="#151a21", # Sidebar color
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.VIDEOCAM_OUTLINED, 
                    selected_icon=ft.Icons.VIDEOCAM, 
                    label="Live View"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.GESTURE, 
                    selected_icon=ft.Icons.GESTURE, 
                    label="Gestures"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED, 
                    selected_icon=ft.Icons.SETTINGS, 
                    label="Settings"
                ),
            ],
            on_change=self.on_nav_change
        )

        # --- Content Area ---
        self.content_area = ft.Column(expand=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Initial Content (Live View)
        self.build_live_view()

        # --- Main Layout ---
        layout = ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
        )

        self.page.add(layout)
    
    def on_nav_change(self, e):
        self.content_area.controls.clear()
        if e.control.selected_index == 0:
            self.build_live_view()
        elif e.control.selected_index == 1:
            self.content_area.controls.append(ft.Text("Gestures Config (Coming Soon)", size=30))
        elif e.control.selected_index == 2:
            self.build_settings_view()
        
        self.content_area.update()

    def build_live_view(self):
        # Controls
        self.btn_start = ft.ElevatedButton(
            content=ft.Text("Start System"),
            icon=ft.Icons.PLAY_ARROW,
            on_click=lambda e: self.toggle_engine(e)
        )
        
        if self.engine.running:
             self.btn_start.content = ft.Text("Stop System")
             self.btn_start.icon = ft.Icons.STOP
             self.btn_start.bgcolor = ft.Colors.RED_400

        self.content_area.controls.extend([
            ft.Text("Hand Mouse Control", size=30, weight=ft.FontWeight.BOLD),
            ft.Text("Camera feed opens in a separate native window for zero-latency performance.", italic=True),
            ft.Container(height=20),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.VIDEOCAM_OUTLINED, size=50, color=ft.Colors.GREEN),
                            ft.Text("Video Engine Status", size=20, weight=ft.FontWeight.BOLD),
                            self.btn_start,
                            ft.Text("Press 'q' in the video window to stop", size=12, color=ft.Colors.GREY_500)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    padding=40,
                )
            )
        ])

    def build_settings_view(self):
        def on_smooth_change(e):
            val = int(e.control.value)
            self.engine.mouse.set_smoothing(val)
            lbl.value = f"Smoothing Factor: {val}"
            self.page.update()

        slider = ft.Slider(min=1, max=20, divisions=19, value=5, label="{value}", on_change=on_smooth_change)
        lbl = ft.Text("Smoothing Factor: 5")

        self.content_area.controls.extend([
            ft.Text("Settings", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            lbl,
            slider,
            ft.Container(height=20),
            ft.Text("One Euro Filter Active", color=ft.Colors.GREEN_400)
        ])

    def toggle_engine(self, e):
        if self.engine.running:
            self.engine.stop()
            self.btn_start.content = ft.Text("Start System")
            self.btn_start.icon = ft.Icons.PLAY_ARROW
            self.btn_start.bgcolor = None 
        else:
            self.engine.start()
            self.btn_start.content = ft.Text("Stop System")
            self.btn_start.icon = ft.Icons.STOP
            self.btn_start.bgcolor = ft.Colors.RED_400
        
        self.btn_start.update() 

def main(page: ft.Page):
    app = AppGUI(page)

if __name__ == "__main__":
    ft.app(target=main)
