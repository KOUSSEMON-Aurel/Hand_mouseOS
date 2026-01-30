# -*- coding: utf-8 -*-
"""
CameraManager - Gestion du cycle de vie de la caméra
Responsabilité unique : Ouverture, lecture, configuration et fermeture de la caméra
"""
from typing import Optional, List
import cv2
import numpy as np


class CameraManager:
    """Gère le cycle de vie de la caméra avec auto-détection"""
    
    def __init__(
        self, 
        indices: List[int] = None,
        backend: int = cv2.CAP_V4L2,
        target_fps: int = 30,
        resolution: tuple = (640, 480)
    ):
        self.indices = indices or [0, 1]
        self.backend = backend
        self.target_fps = target_fps
        self.resolution = resolution
        self.cap: Optional[cv2.VideoCapture] = None
        self._is_opened = False
        self._current_index = -1
    
    def open(self) -> bool:
        """Trouve et ouvre la première caméra disponible"""
        for idx in self.indices:
            print(f"📷 Testing camera index {idx} with {self._backend_name()}...")
            cap = cv2.VideoCapture(idx, self.backend)
            if self._test_camera(cap):
                self.cap = cap
                self._configure()
                self._is_opened = True
                self._current_index = idx
                print(f"✅ Camera {idx} opened successfully")
                return True
            cap.release()
        print("❌ No working camera found")
        return False
    
    def _backend_name(self) -> str:
        """Retourne le nom du backend pour les logs"""
        backends = {cv2.CAP_V4L2: "V4L2", cv2.CAP_GSTREAMER: "GStreamer"}
        return backends.get(self.backend, "Default")
    
    def _test_camera(self, cap: cv2.VideoCapture) -> bool:
        """Vérifie si une caméra est fonctionnelle"""
        if not cap.isOpened():
            return False
        ret, _ = cap.read()
        return ret
    
    def _configure(self):
        """Configure les paramètres optimaux de la caméra"""
        if self.cap is None:
            return
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Réduit la latence
    
    def read(self, flip: bool = True) -> Optional[np.ndarray]:
        """Lit une frame, optionnellement flippée horizontalement"""
        if not self._is_opened or self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return cv2.flip(frame, 1) if flip else frame
    
    def release(self):
        """Libère les ressources de la caméra"""
        if self.cap:
            self.cap.release()
            self._is_opened = False
            self._current_index = -1
            print("📷 Camera released")
    
    @property
    def is_opened(self) -> bool:
        return self._is_opened
    
    @property
    def current_index(self) -> int:
        return self._current_index
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args):
        self.release()
