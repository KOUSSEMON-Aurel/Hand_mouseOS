import flet as ft
import threading
import subprocess
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
        
        # Initialize Engine (Native Window Enabled as requested)
        self.engine = HandEngine(headless=False)
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
        import cv2
        import numpy as np
        import base64
        
        # Create 600x400 black image (Matches Main Container)
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Draw grid lines for 4 quadrants (300x200 each)
        cv2.line(img, (300, 0), (300, 400), (50, 50, 50), 2)
        cv2.line(img, (0, 200), (600, 200), (50, 50, 50), 2)
        
        # Labels
        cv2.putText(img, 'Main View', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        cv2.putText(img, 'Top View', (310, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        cv2.putText(img, 'Left View', (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        cv2.putText(img, 'Right View', (310, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        
        cv2.putText(img, "WAITING...", (240, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        _, buffer = cv2.imencode('.png', img)
        return base64.b64encode(buffer).decode()

    def _draw_hand_skeleton(self, landmarks, world_landmarks=None, gesture="UNKNOWN", hand_idx=0):
        """Draws a 4-view 3D skeleton using OpenCV."""
        import cv2
        import numpy as np
        import base64
        
        # Canvas 600x400
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Draw Quadrant Lines
        cv2.line(img, (300, 0), (300, 400), (100, 100, 100), 1)
        cv2.line(img, (0, 200), (600, 200), (100, 100, 100), 1)
        
        # Labels
        cv2.putText(img, 'Main', (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.putText(img, 'Top', (305, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.putText(img, 'Left', (5, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.putText(img, 'Right', (305, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        # Color
        color = (0, 255, 255) if hand_idx == 0 else (255, 0, 255) # BGR
        
        def draw_lines(image, pts, offset_x=0, offset_y=0, scale=1.0):
            # MediaPipe Joints: 0-4 (Thumb), 5-8 (Index), etc.
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),
                (0, 5), (5, 6), (6, 7), (7, 8),
                (5, 9), (9, 10), (10, 11), (11, 12),
                (9, 13), (13, 14), (14, 15), (15, 16),
                (13, 17), (17, 18), (18, 19), (19, 20),
                (0, 17)
            ]
            
            # Draw Bones
            for start, end in connections:
                if start < len(pts) and end < len(pts):
                    pt1 = (int(pts[start][0] * scale + offset_x), int(pts[start][1] * scale + offset_y))
                    pt2 = (int(pts[end][0] * scale + offset_x), int(pts[end][1] * scale + offset_y))
                    cv2.line(image, pt1, pt2, (200, 200, 200), 2)
            
            # Draw Joints
            for p in pts:
                px = int(p[0] * scale + offset_x)
                py = int(p[1] * scale + offset_y)
                cv2.circle(image, (px, py), 3, color, -1)

        # 1. Main View (Top-Left) - Use Screen Landmarks
        # Scale 0-1 to 300x200
        screen_pts = np.array([(lm.x, lm.y) for lm in landmarks])
        screen_pts[:, 0] = screen_pts[:, 0] * 300 # Width
        screen_pts[:, 1] = screen_pts[:, 1] * 200 # Height
        draw_lines(img, screen_pts, offset_x=0, offset_y=0)
        
        # 2. 3D Views - Require World Landmarks
        if world_landmarks:
            # Extract world x,y,z
            w_pts = np.array([(lm.x, lm.y, lm.z) for lm in world_landmarks])
            
            # Normalize scale (heuristic)
            scale_3d = 1000 
            
            # Top View (XZ plane) -> Top-Right (Start x=300)
            # x -> x, z -> y
            top_pts = w_pts[:, [0, 2]] 
            top_pts[:, 1] = -top_pts[:, 1]
            # Center roughly in 300x200 box (center is 150, 100 relative)
            draw_lines(img, top_pts, offset_x=450, offset_y=100, scale=scale_3d) 
            
            # Left View (YZ plane) -> Bottom-Left (Start y=200)
            # y -> y, z -> x
            left_pts = w_pts[:, [2, 1]]
            left_pts[:, 0] = -left_pts[:, 0]
            draw_lines(img, left_pts, offset_x=150, offset_y=300, scale=scale_3d)

            # Right View (ZY plane) -> Bottom-Right (Start x=300, y=200)
            right_pts = w_pts[:, [2, 1]]
            draw_lines(img, right_pts, offset_x=450, offset_y=300, scale=scale_3d)
            
        else:
            cv2.putText(img, "No 3D Data", (420, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Encode
        _, buffer = cv2.imencode('.png', img)
        return base64.b64encode(buffer).decode()
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
        
        # PHASE 8: Toggle Switches
        self.switch_keyboard = ft.Switch(
            label="🔤 Clavier Virtuel",
            value=False,
            on_change=lambda e: self.toggle_keyboard(e)
        )
        
        # PHASE 8: Keyboard Mode Selector
        self.keyboard_mode_dropdown = ft.Dropdown(
            label="Mode Clavier",
            value="dwell",
            options=[
                ft.dropdown.Option("dwell", "SURVOL (Attendre 1s)"),
                ft.dropdown.Option("pinch", "PINCER (Pouce+Index)")
            ],
            width=200
        )
        self.keyboard_mode_dropdown.on_change = lambda e: self.change_keyboard_mode(e)
        
        # PHASE 8: Mouse Freeze Toggle
        self.switch_mouse_freeze = ft.Switch(
            label="❄️ Geler la Souris",
            value=False,
            on_change=lambda e: self.toggle_mouse_freeze(e)
        )
        
        self.switch_asl = ft.Switch(
            label="🤟 Langue des Signes (ASL)",
            value=False,
            on_change=lambda e: self.toggle_asl(e)
        )


        # Dashboard Layout (Simplified - Skeleton is now in separate native window)
        dashboard = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Hand Mouse OS", size=30, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    self.txt_latency
                ]),
                
                ft.Row([
                    # Left Side: Info Panel (Skeleton is in separate window)
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.FRONT_HAND, size=80, color=ft.Colors.CYAN_400),
                            ft.Text("Visualisation Active", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                "Les fenêtres de visualisation OpenCV\ns'ouvriront automatiquement.",
                                text_align=ft.TextAlign.CENTER,
                                color=ft.Colors.GREY_400
                            ),
                            ft.Divider(height=20, color=ft.Colors.GREY_800),
                            ft.Text("Fenêtre 1: Hand Mouse AI (Webcam)", size=12, color=ft.Colors.GREEN_400),
                            ft.Text("Fenêtre 2: Skeleton 4-View (3D)", size=12, color=ft.Colors.YELLOW_400),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        bgcolor="#1e1e2e",
                        border_radius=15,
                        width=400,
                        height=300,
                        padding=30,
                        border=ft.border.all(1, "#45a29e")
                    ),
                    
                    # Right Side: Status & Controls
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.MONITOR_HEART, size=40, color=ft.Colors.BLUE_400),
                                ft.Text("AI Engine", size=14, weight=ft.FontWeight.BOLD),
                                self.btn_start,
                                ft.Divider(height=10, color=ft.Colors.GREY_800),
                                ft.Text("Fonctionnalités", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                                self.switch_keyboard,
                                self.keyboard_mode_dropdown,
                                self.switch_mouse_freeze,
                                self.switch_asl
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor="#2b2d31", padding=20, border_radius=15, width=280
                        ),
                    ])
                ], spacing=20, alignment=ft.MainAxisAlignment.START)
            ]),
            padding=30
        )
        self.content_area.controls.append(dashboard)

        # Start loops
        threading.Thread(target=self.update_metrics_loop, daemon=True).start()
        # NOTE: Skeleton update loop removed - now handled by engine in native window

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
    
    def toggle_keyboard(self, e):
        """Active/Désactive le clavier virtuel."""
        # Safety: Only allow if engine is running
        if not self.engine.is_processing and e.control.value:
            print("⚠️ Démarrez le système avant d'activer le clavier!")
            e.control.value = False
            self.switch_keyboard.update()
            return
        
        self.engine.keyboard_enabled = e.control.value
        print(f"🔤 Clavier Virtuel: {'ACTIVÉ' if e.control.value else 'DÉSACTIVÉ'}")
    
    def change_keyboard_mode(self, e):
        """Change le mode du clavier (DWELL ou PINCH)."""
        new_mode = e.control.value
        self.engine.virtual_keyboard.mode = new_mode
        mode_name = "SURVOL (1s)" if new_mode == "dwell" else "PINCER"
        print(f"⌨️ Mode Clavier changé: {mode_name}")
    
    def toggle_mouse_freeze(self, e):
        """Gel/Dégel la souris pour faciliter la frappe."""
        self.engine.mouse_frozen = e.control.value
        status = "GELÉE ❄️" if e.control.value else "DÉGELÉE ✅"
        print(f"🕹️ Souris: {status}")
    
    def toggle_asl(self, e):
        """Active/Désactive la reconnaissance ASL."""
        self.engine.asl_enabled = e.control.value
        print(f"🤟 ASL: {'ACTIVÉ' if e.control.value else 'DÉSACTIVÉ'}")

    def run_setup_webcam(self):
        """Lance l'installation de DroidCam via le CLI Go."""
        def run():
            # Afficher un message de début
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("🚀 Préparation de l'installation de DroidCam..."),
                bgcolor=ft.Colors.BLUE_900
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            try:
                # Trouver le binaire Go
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                cli_path = os.path.join(project_root, "cli", "handmouse")
                
                # S'assurer que le binaire existe
                if not os.path.exists(cli_path):
                    # Essayer de le compiler si absent
                    os.system(f"cd {os.path.join(project_root, 'cli')} && go build -o handmouse")
                
                # Lancer la commande dans un terminal séparé pour que l'utilisateur voit le sudo
                if os.name == 'posix': # Linux
                    # On utilise x-terminal-emulator ou termite/gnome-terminal selon ce qui est dispo
                    cmd = f"x-terminal-emulator -e {cli_path} setup webcam || gnome-terminal -- {cli_path} setup webcam || xterm -e {cli_path} setup webcam"
                    subprocess.run(cmd, shell=True)
                else: # Windows
                    subprocess.run([cli_path, "setup", "webcam"], shell=True)
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Installation de DroidCam terminée !"),
                    bgcolor=ft.Colors.GREEN_900
                )
                self.page.snack_bar.open = True
            except Exception as e:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Erreur: {str(e)}"),
                    bgcolor=ft.Colors.RED_900
                )
                self.page.snack_bar.open = True
            
            self.page.update()

        threading.Thread(target=run, daemon=True).start()

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
