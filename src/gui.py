import flet as ft
import threading
import time
from engine import HandEngine
from gestures_view import GesturesView
from settings_view import SettingsView

class AppGUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Hand Mouse OS - Master Control"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.bgcolor = "#1a1c21"
        
        self.engine = HandEngine()
        
        # Navigation State
        self.current_view_index = 0
        
        self.init_components()
        self.build_layout()
        self.render_view(0)
        
    def init_components(self):
        # Sidebar items
        self.menu_items = [
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Bord"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BACK_HAND_OUTLINED,
                selected_icon=ft.Icons.BACK_HAND,
                label="Gestes"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Paramètres"
            ),
        ]
        
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=self.menu_items,
            on_change=self.on_nav_change,
            bgcolor="#2b2d31",
        )
        
        # Main Content Area
        self.content_area = ft.Column(expand=True, scroll="auto")
        # Defer rendering until attached

    def on_nav_change(self, e):
        idx = e.control.selected_index
        self.render_view(idx)

    def render_view(self, idx):
        self.content_area.controls.clear()
        
        if idx == 0:
            self.build_live_view()
        elif idx == 1:
            self.content_area.controls.append(GesturesView())
        elif idx == 2:
            self.content_area.controls.append(SettingsView(self))
            
        if self.content_area.page:
            self.content_area.update()
        
    def go_home(self):
        self.rail.selected_index = 0
        self.rail.update()
        self.render_view(0)

    def build_live_view(self):
        # Controls
        icon = ft.Icons.PLAY_ARROW
        text = "Start System"
        color = ft.Colors.BLUE_400
        
        # Init metrics controls
        self.txt_latency = ft.Text("Waiting...", color=ft.Colors.CYAN_400, weight=ft.FontWeight.BOLD)
        self.logs_view = ft.Text("System initialized.\nReady.", font_family="Consolas", color=ft.Colors.GREEN_400)
        
        if self.engine.is_processing:
             icon = ft.Icons.STOP
             text = "Stop System"
             color = ft.Colors.RED_400

        self.btn_start = ft.ElevatedButton(
            content=ft.Text(text),
            icon=icon,
            bgcolor=color,
            on_click=lambda e: self.toggle_engine(e),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
            )
        )

        # Dashboard Layout
        dashboard = ft.Container(
            content=ft.Column([
                ft.Text("Hand Mouse OS", size=40, weight=ft.FontWeight.BOLD),
                ft.Text("V 1.0.0 - Optimized Core", size=16, color=ft.Colors.GREY_400),
                ft.Container(height=30),
                
                ft.Row([
                    # Status Card
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.MONITOR_HEART, size=40, color=ft.Colors.BLUE_400),
                            ft.Text("AI Engine", size=14, weight=ft.FontWeight.BOLD),
                            self.btn_start
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#2b2d31", padding=20, border_radius=15, width=200
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Container(height=30),
                ft.Container(height=30),
                ft.Row([
                    ft.Text("Performance Monitor:", weight=ft.FontWeight.BOLD),
                    ft.Container(width=10),
                    self.txt_latency  # Added control
                ]),
                ft.Container(
                    content=self.logs_view, # Reusing container as logs_view
                    bgcolor="#111111", padding=10, border_radius=5, width=600, height=150
                )
            ]),
            padding=40
        )
        self.content_area.controls.append(dashboard)

        # Start metrics update loop
        threading.Thread(target=self.update_metrics_loop, daemon=True).start()

    def update_metrics_loop(self):
        while True:
            if hasattr(self, 'txt_latency') and self.content_area.page:
                if self.engine.is_processing:
                    fps = self.engine.profiler.get_fps()
                    lat = self.engine.profiler.get_inference_time()
                    try:
                        self.txt_latency.value = f"FPS: {fps:.1f} | Latency: {lat:.1f} ms"
                        self.txt_latency.update()
                    except:
                        pass
            time.sleep(0.5)

    def toggle_engine(self, e):
        if not self.engine.is_processing:
            self.engine.start()
            self.btn_start.content = ft.Text("Stop System")
            self.btn_start.icon = ft.Icons.STOP
            self.btn_start.bgcolor = ft.Colors.RED_400
        else:
            self.engine.stop()
            self.btn_start.content = ft.Text("Start System")
            self.btn_start.icon = ft.Icons.PLAY_ARROW
            self.btn_start.bgcolor = ft.Colors.BLUE_400
        
        self.btn_start.update()

    def build_layout(self):
        self.page.add(
            ft.Row(
                [
                    self.rail,
                    ft.VerticalDivider(width=1, color=ft.Colors.GREY_800),
                    self.content_area,
                ],
                expand=True,
            )
        )

def main(page: ft.Page):
    app = AppGUI(page)

if __name__ == "__main__":
    ft.app(target=main)
