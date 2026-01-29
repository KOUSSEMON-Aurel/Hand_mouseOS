# -*- coding: utf-8 -*-
"""
CameraPreview - Widget Flet pour affichage vidéo
"""
import flet as ft
import base64
import cv2
import numpy as np
from typing import Optional


class CameraPreview(ft.UserControl):
    """Widget de prévisualisation caméra avec squelette"""
    
    def __init__(self, width: int = 640, height: int = 480):
        super().__init__()
        self.width = width
        self.height = height
        
        # Image affichée
        self.image = ft.Image(
            src_base64=self._create_blank_image(),
            width=width,
            height=height,
            fit=ft.ImageFit.CONTAIN,
            border_radius=8,
        )
    
    def build(self):
        return ft.Container(
            content=self.image,
            bgcolor="#1a1c21",
            border_radius=8,
            padding=4,
            border=ft.border.all(2, ft.colors.WHITE12),
        )
    
    def update_frame(self, frame: np.ndarray):
        """Met à jour l'image affichée"""
        try:
            # Encode en JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            self.image.src_base64 = img_base64
            self.update()
        except Exception as e:
            print(f"CameraPreview update error: {e}")
    
    def _create_blank_image(self) -> str:
        """Crée une image noire de base"""
        blank = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cv2.putText(
            blank, "WAITING...", 
            (self.width // 2 - 80, self.height // 2),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2
        )
        _, buffer = cv2.imencode('.jpg', blank)
        return base64.b64encode(buffer).decode('utf-8')
    
    def set_offline(self):
        """Affiche l'état hors-ligne"""
        self.image.src_base64 = self._create_blank_image()
        self.update()
