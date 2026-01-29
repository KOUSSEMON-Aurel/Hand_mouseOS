# -*- coding: utf-8 -*-
"""
StatusPanel - Widget Flet pour afficher l'état du moteur
"""
import flet as ft


class StatusPanel(ft.UserControl):
    """Panneau d'état avec indicateurs LED et métriques"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
        # Indicateurs
        self.fps_text = ft.Text("0 FPS", size=14, color=ft.colors.WHITE)
        self.latency_text = ft.Text("0ms", size=14, color=ft.colors.WHITE)
        self.mode_text = ft.Text("CURSOR", size=14, color=ft.colors.CYAN)
        self.gesture_text = ft.Text("--", size=14, color=ft.colors.WHITE)
        
        # LED Status
        self.status_led = ft.Container(
            width=12,
            height=12,
            border_radius=6,
            bgcolor=ft.colors.RED_400
        )
    
    def build(self):
        return ft.Container(
            content=ft.Row(
                [
                    # LED + Status
                    ft.Row([
                        self.status_led,
                        ft.Text("Engine", size=12, color=ft.colors.WHITE54)
                    ], spacing=8),
                    
                    # Métriques
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.SPEED, size=16, color=ft.colors.GREEN),
                            self.fps_text,
                        ], spacing=4),
                        padding=ft.padding.symmetric(horizontal=8)
                    ),
                    
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.TIMER, size=16, color=ft.colors.ORANGE),
                            self.latency_text,
                        ], spacing=4),
                        padding=ft.padding.symmetric(horizontal=8)
                    ),
                    
                    # Mode & Geste
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.PAN_TOOL, size=16, color=ft.colors.CYAN),
                            self.mode_text,
                        ], spacing=4),
                        padding=ft.padding.symmetric(horizontal=8)
                    ),
                    
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.GESTURE, size=16, color=ft.colors.PURPLE),
                            self.gesture_text,
                        ], spacing=4),
                        padding=ft.padding.symmetric(horizontal=8)
                    ),
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            bgcolor="#2a2d35",
            padding=10,
            border_radius=8,
        )
    
    def update_status(self, is_running: bool, fps: float, latency: float, mode: str, gesture: str):
        """Met à jour tous les indicateurs"""
        self.status_led.bgcolor = ft.colors.GREEN_400 if is_running else ft.colors.RED_400
        self.fps_text.value = f"{int(fps)} FPS"
        self.latency_text.value = f"{int(latency)}ms"
        self.mode_text.value = mode.upper()
        self.gesture_text.value = gesture
        self.update()
