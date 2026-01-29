import flet as ft
from engine import HandEngine
from calibration_view import CalibrationView

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
                label="Tableau de bord"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OVERSCAN_OUTLINED,
                selected_icon=ft.Icons.SETTINGS_OVERSCAN,
                label="Calibration"
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
            self.content_area.controls.append(CalibrationView(self))
        elif idx == 2:
            self.content_area.controls.append(
                ft.Container(
                    content=ft.Text("Paramètres avancés (À venir dans v1.1)", size=20, color=ft.Colors.GREY_500),
                    alignment=ft.alignment.center,
                    padding=50
                )
            )
            
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
                    
                    # Info Card
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=40, color=ft.Colors.ORANGE_400),
                            ft.Text("GPU Status", size=14, weight=ft.FontWeight.BOLD),
                            ft.Text("CPU Fallback" if "CPU" in str(self.engine.options.base_options.delegate) else "Auto/GPU", size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#2b2d31", padding=20, border_radius=15, width=200
                    )
                ], spacing=20),
                
                ft.Container(height=30),
                ft.Text("Console Logs:", weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text("System initialized.\nReady to capture.", font_family="Consolas", color=ft.Colors.GREEN_400),
                    bgcolor="#111111", padding=10, border_radius=5, width=600, height=150
                )
            ]),
            padding=40
        )
        self.content_area.controls.append(dashboard)

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
