import flet as ft
import threading
import time
import json
import os
import http.server
import socket
from src.engine import HandEngine
from src.gestures_view import GesturesView
from src.settings_view import SettingsView

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

    # --- Skeleton Visualization Helpers ---
    def _create_blank_skeleton(self):
        """Generates a blank black image for idle state."""
        from PIL import Image as PILImage, ImageDraw
        import io, base64
        img = PILImage.new('RGB', (300, 300), color='#111111')
        draw = ImageDraw.Draw(img)
        draw.text((100, 140), "Waiting...", fill='#555555')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

    def _draw_hand_skeleton(self, landmarks, gesture="UNKNOWN", hand_idx=0):
        """Draws a 2D skeleton from landmarks."""
        from PIL import Image as PILImage, ImageDraw
        import io, base64
        
        img = PILImage.new('RGB', (300, 300), color='#111111')
        draw = ImageDraw.Draw(img)
        
        # Colors: Cyan for Primary, Purple for Secondary
        color = (0, 255, 255) if hand_idx == 0 else (255, 0, 255)
        
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4), 
            (0, 5), (5, 6), (6, 7), (7, 8), 
            (5, 9), (9, 10), (10, 11), (11, 12), 
            (9, 13), (13, 14), (14, 15), (15, 16), 
            (13, 17), (17, 18), (18, 19), (19, 20), 
            (0, 17)
        ]
        
        # Normalize and scale
        width, height = 300, 300
        points = []
        for lm in landmarks:
            # Mirror X for self-view feeling
            px = int((1 - lm.x) * width)
            py = int(lm.y * height)
            points.append((px, py))
        
        # Draw Lines
        for start, end in connections:
            if start < len(points) and end < len(points):
                draw.line([points[start], points[end]], fill=color, width=2)
        
        # Draw Joints
        for px, py in points:
            draw.ellipse([px-2, py-2, px+2, py+2], fill=color)
            
        # Gesture Label
        label = f"{'Main' if hand_idx == 0 else 'Sub'}: {gesture}"
        draw.text((10, 10), label, fill=color)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    # --------------------------------------

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

        # Live Skeletal HUD (Canvas 2D)
        from PIL import Image as PILImage, ImageDraw
        import io
        
        # Create initial blank canvas
        self.skeleton_canvas = ft.Image(
            src_base64=self._create_blank_skeleton(),
            fit="contain",
            expand=True
        )

        # Live Skeletal HUD (Canvas 2D)
        self.skeleton_canvas = ft.Image(
            src_base64=self._create_blank_skeleton(),
            fit="contain",
            expand=True,
            gapless_playback=True 
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
                        
                        # SKELETON VIEW CONTAINER (Replacing Logs)
                        ft.Container(
                            content=self.skeleton_canvas,
                            bgcolor="#111111", 
                            border_radius=10, 
                            width=200, 
                            height=220,
                            border=ft.border.all(1, "#333333")
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
        # Callback for engine to push frames
        def on_frame(b64_frame):
            if self.content_area.page:
                # 1. Update Main Video
                if self.wv_3d:
                    self.wv_3d.src_base64 = b64_frame
                    self.wv_3d.update()
                
                # 2. Update Skeleton View
                if self.skeleton_canvas and self.engine.latest_landmarks:
                    # Get gestures for label
                    gestures = getattr(self.engine, 'current_gestures', ["UNKNOWN"])
                    g_label = gestures[0] if gestures else "TRACKING"
                    
                    skel_b64 = self._draw_hand_skeleton(
                        self.engine.latest_landmarks, 
                        gesture=g_label
                    )
                    self.skeleton_canvas.src_base64 = skel_b64
                    self.skeleton_canvas.update()
                elif self.skeleton_canvas:
                    # Show blank if lost tracking
                    self.skeleton_canvas.src_base64 = self._create_blank_skeleton()
                    self.skeleton_canvas.update()

        # Attach callback
        if self.engine:
            self.engine.frame_callback = on_frame
            
        # Keep thread alive monitoring engine state
        while True:
            # Watchdog...
            time.sleep(1)

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
