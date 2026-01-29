import flet as ft
import threading
import time
import json
import os
import http.server
import socket
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
        self.wv_3d = None # WebView for 3D HUD
        
        # Start Local HUD Server
        self.port = self.find_free_port()
        threading.Thread(target=self.start_asset_server, daemon=True).start()
        
        # Navigation State
        self.current_view_index = 0
        
        self.init_components()
        self.build_layout()
        self.render_view(0)
        
    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def start_asset_server(self):
        # Serve from project root to access assets/
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        handler = http.server.SimpleHTTPRequestHandler
        with http.server.HTTPServer(("", self.port), handler) as httpd:
            print(f"HUD Asset Server running on port {self.port}")
            httpd.serve_forever()

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
            self.content_area.controls.append(GesturesView(self))
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

        # 3D HUD WebView
        self.wv_3d = ft.WebView(
            url=f"http://localhost:{self.port}/assets/3d/hand_scene.html",
            on_page_started=lambda _: print("3D HUD Started"),
            expand=True
        )

        # Dashboard Layout
        dashboard = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Hand Mouse OS", size=30, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    self.txt_latency
                ]),
                
                ft.Row([
                    # Left Side: Visualization
                    ft.Container(
                        content=self.wv_3d,
                        bgcolor="#000000",
                        border_radius=15,
                        width=600,
                        height=400,
                        border=ft.border.all(1, "#45a29e")
                    ),
                    
                    # Right Side: Status & Controls
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.MONITOR_HEART, size=40, color=ft.Colors.BLUE_400),
                                ft.Text("AI Engine", size=14, weight=ft.FontWeight.BOLD),
                                self.btn_start
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor="#2b2d31", padding=20, border_radius=15, width=200
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text("System Logs", size=12, color=ft.Colors.GREY_400),
                                self.logs_view
                            ]),
                            bgcolor="#111111", padding=15, border_radius=10, width=200, height=220
                        )
                    ])
                ], spacing=20, alignment=ft.MainAxisAlignment.START)
            ]),
            padding=30
        )
        self.content_area.controls.append(dashboard)

        # Start loops
        threading.Thread(target=self.update_metrics_loop, daemon=True).start()
        threading.Thread(target=self.update_3d_loop, daemon=True).start()

    def update_3d_loop(self):
        while True:
            if self.engine.is_processing and self.wv_3d:
                with self.engine.lock:
                    landmarks = self.engine.latest_landmarks
                
                if landmarks:
                    # Convert MediaPipe landmarks to simple list of dicts for JS
                    data = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in landmarks]
                    js_data = json.dumps(data)
                    try:
                        # Use window.postMessage for cleaner data transfer
                        self.wv_3d.run_javascript(f"window.postMessage({js_data}, '*')")
                    except Exception as e:
                        pass
            time.sleep(0.033) # ~30 FPS for 3D view

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
