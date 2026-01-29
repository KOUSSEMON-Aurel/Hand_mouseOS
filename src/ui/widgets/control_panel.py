# -*- coding: utf-8 -*-
"""
ControlPanel - Widget Flet pour les contrôles du moteur
"""
import flet as ft
from typing import Callable


class ControlPanel(ft.UserControl):
    """Panneau de contrôle avec boutons Start/Stop et toggles"""
    
    def __init__(
        self,
        on_toggle_engine: Callable,
        on_toggle_keyboard: Callable,
        on_toggle_asl: Callable,
        on_toggle_freeze: Callable = None
    ):
        super().__init__()
        self.on_toggle_engine = on_toggle_engine
        self.on_toggle_keyboard = on_toggle_keyboard
        self.on_toggle_asl = on_toggle_asl
        self.on_toggle_freeze = on_toggle_freeze
        
        # État
        self.is_running = False
        self.keyboard_enabled = False
        self.asl_enabled = False
        self.mouse_frozen = False
        
        # Boutons
        self.start_btn = ft.ElevatedButton(
            text="▶️ START",
            bgcolor=ft.colors.GREEN_700,
            color=ft.colors.WHITE,
            on_click=self._handle_engine_toggle,
            width=120,
            height=45
        )
        
        self.keyboard_btn = ft.IconButton(
            icon=ft.icons.KEYBOARD_OUTLINED,
            icon_color=ft.colors.WHITE54,
            tooltip="Clavier Virtuel",
            on_click=self._handle_keyboard_toggle,
        )
        
        self.asl_btn = ft.IconButton(
            icon=ft.icons.SIGN_LANGUAGE_OUTLINED,
            icon_color=ft.colors.WHITE54,
            tooltip="Reconnaissance ASL",
            on_click=self._handle_asl_toggle,
        )
        
        self.freeze_btn = ft.IconButton(
            icon=ft.icons.MOUSE_OUTLINED,
            icon_color=ft.colors.WHITE54,
            tooltip="Geler Souris",
            on_click=self._handle_freeze_toggle,
        )
    
    def build(self):
        return ft.Container(
            content=ft.Row(
                [
                    # Bouton principal
                    self.start_btn,
                    
                    ft.VerticalDivider(width=1, color=ft.colors.WHITE12),
                    
                    # Toggles
                    ft.Row([
                        self.keyboard_btn,
                        self.asl_btn,
                        self.freeze_btn,
                    ], spacing=4),
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            bgcolor="#2a2d35",
            padding=12,
            border_radius=8,
        )
    
    def _handle_engine_toggle(self, e):
        self.is_running = not self.is_running
        self._update_engine_button()
        if self.on_toggle_engine:
            self.on_toggle_engine(e)
    
    def _handle_keyboard_toggle(self, e):
        self.keyboard_enabled = not self.keyboard_enabled
        self.keyboard_btn.icon_color = (
            ft.colors.BLUE_400 if self.keyboard_enabled 
            else ft.colors.WHITE54
        )
        self.update()
        if self.on_toggle_keyboard:
            self.on_toggle_keyboard(e)
    
    def _handle_asl_toggle(self, e):
        self.asl_enabled = not self.asl_enabled
        self.asl_btn.icon_color = (
            ft.colors.ORANGE_400 if self.asl_enabled 
            else ft.colors.WHITE54
        )
        self.update()
        if self.on_toggle_asl:
            self.on_toggle_asl(e)
    
    def _handle_freeze_toggle(self, e):
        self.mouse_frozen = not self.mouse_frozen
        self.freeze_btn.icon_color = (
            ft.colors.RED_400 if self.mouse_frozen 
            else ft.colors.WHITE54
        )
        self.update()
        if self.on_toggle_freeze:
            self.on_toggle_freeze(e)
    
    def _update_engine_button(self):
        if self.is_running:
            self.start_btn.text = "⏹️ STOP"
            self.start_btn.bgcolor = ft.colors.RED_700
        else:
            self.start_btn.text = "▶️ START"
            self.start_btn.bgcolor = ft.colors.GREEN_700
        self.update()
    
    def set_running(self, is_running: bool):
        """Synchronise l'état externe"""
        self.is_running = is_running
        self._update_engine_button()
