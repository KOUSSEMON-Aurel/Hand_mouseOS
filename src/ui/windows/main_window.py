# -*- coding: utf-8 -*-
"""
MainWindow - Fenêtre principale refactorisée utilisant les widgets modulaires
"""
import flet as ft
import threading
import time

from src.engine import HandEngine
from src.gestures_view import GesturesView
from src.settings_view import SettingsView


class MainWindow:
    """Fenêtre principale de l'application Hand Mouse OS"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._configure_page()
        
        # Moteur
        self.engine = HandEngine(headless=False)
        
        # Composants UI
        self._init_navigation()
        self._init_live_view()
        
        # Thread métriques
        self._metrics_thread = threading.Thread(
            target=self._update_metrics_loop, 
            daemon=True
        )
        self._metrics_running = True
        self._metrics_thread.start()
        
        # Build layout
        self._build_layout()
    
    def _configure_page(self):
        """Configure la page Flet"""
        self.page.title = "Hand Mouse OS - Master Control"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.bgcolor = "#1a1c21"
    
    def _init_navigation(self):
        """Initialise la barre de navigation"""
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
            destinations=self.menu_items,
            on_change=self._on_nav_change,
            bgcolor="#2b2d31",
        )
        
        self.content_area = ft.Column(expand=True, scroll="auto")
    
    def _init_live_view(self):
        """Initialise les composants de la vue principale"""
        # Bouton Start/Stop
        self.start_btn = ft.ElevatedButton(
            text="▶️ START",
            bgcolor=ft.colors.GREEN_700,
            color=ft.colors.WHITE,
            on_click=self._toggle_engine,
            width=120,
            height=45
        )
        
        # Status LED
        self.status_led = ft.Container(
            width=12, height=12, 
            border_radius=6,
            bgcolor=ft.colors.RED_400
        )
        
        # Métriques
        self.fps_text = ft.Text("0 FPS", size=14)
        self.mode_text = ft.Text("IDLE", size=14, color=ft.colors.CYAN)
        
        # Toggles
        self.keyboard_btn = ft.IconButton(
            icon=ft.icons.KEYBOARD_OUTLINED,
            icon_color=ft.colors.WHITE54,
            tooltip="Clavier Virtuel",
            on_click=self._toggle_keyboard,
        )
        self.asl_btn = ft.IconButton(
            icon=ft.icons.SIGN_LANGUAGE_OUTLINED,
            icon_color=ft.colors.WHITE54,
            tooltip="ASL",
            on_click=self._toggle_asl,
        )
    
    def _on_nav_change(self, e):
        """Gère le changement de navigation"""
        idx = e.control.selected_index
        self.content_area.controls.clear()
        
        if idx == 0:
            self._build_dashboard()
        elif idx == 1:
            self.content_area.controls.append(GesturesView(self.page))
        elif idx == 2:
            self.content_area.controls.append(SettingsView(self.page, self.engine))
        
        self.page.update()
    
    def _build_dashboard(self):
        """Construit le tableau de bord principal"""
        self.content_area.controls.append(
            ft.Container(
                content=ft.Column([
                    # Header
                    ft.Row([
                        ft.Text("🖐️ Hand Mouse OS", size=24, weight=ft.FontWeight.BOLD),
                        ft.Row([self.status_led, self.fps_text], spacing=8),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(height=20, color=ft.colors.WHITE12),
                    
                    # Contrôles
                    ft.Row([
                        self.start_btn,
                        ft.VerticalDivider(width=1),
                        self.keyboard_btn,
                        self.asl_btn,
                    ], spacing=16),
                    
                    ft.Divider(height=20, color=ft.colors.WHITE12),
                    
                    # Mode actuel
                    ft.Row([
                        ft.Text("Mode:", size=14),
                        self.mode_text,
                    ], spacing=8),
                    
                ], spacing=16),
                padding=20,
            )
        )
    
    def _toggle_engine(self, e):
        """Toggle Start/Stop"""
        if self.engine.is_processing:
            self.engine.stop()
            self.start_btn.text = "▶️ START"
            self.start_btn.bgcolor = ft.colors.GREEN_700
            self.status_led.bgcolor = ft.colors.RED_400
        else:
            self.engine.start()
            self.start_btn.text = "⏹️ STOP"
            self.start_btn.bgcolor = ft.colors.RED_700
            self.status_led.bgcolor = ft.colors.GREEN_400
        self.page.update()
    
    def _toggle_keyboard(self, e):
        """Toggle clavier virtuel"""
        self.engine.keyboard_enabled = not self.engine.keyboard_enabled
        self.keyboard_btn.icon_color = (
            ft.colors.BLUE_400 if self.engine.keyboard_enabled 
            else ft.colors.WHITE54
        )
        self.page.update()
    
    def _toggle_asl(self, e):
        """Toggle ASL"""
        self.engine.asl_enabled = not self.engine.asl_enabled
        self.asl_btn.icon_color = (
            ft.colors.ORANGE_400 if self.engine.asl_enabled 
            else ft.colors.WHITE54
        )
        print(f"🤟 ASL: {'ACTIVÉ' if self.engine.asl_enabled else 'DÉSACTIVÉ'}")
        self.page.update()
    
    def _update_metrics_loop(self):
        """Thread de mise à jour des métriques"""
        while self._metrics_running:
            try:
                fps = self.engine.profiler.get_fps()
                self.fps_text.value = f"{int(fps)} FPS"
                
                mode = getattr(self.engine, 'current_mode', None)
                if mode:
                    self.mode_text.value = mode.value.upper()
                
                self.page.update()
            except Exception:
                pass
            time.sleep(0.5)
    
    def _build_layout(self):
        """Construit le layout principal"""
        self._build_dashboard()
        
        self.page.add(
            ft.Row(
                [
                    self.rail,
                    ft.VerticalDivider(width=1),
                    ft.Column([self.content_area], expand=True),
                ],
                expand=True,
            )
        )


def main(page: ft.Page):
    """Point d'entrée Flet"""
    MainWindow(page)
