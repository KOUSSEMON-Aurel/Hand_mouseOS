# -*- coding: utf-8 -*-
"""
HandTracker - Wrapper MediaPipe avec gestion GPU/CPU automatique
Responsabilité unique : Détection des mains via MediaPipe
"""
from typing import Optional, Callable
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np


class HandTracker:
    """Wrapper MediaPipe avec fallback GPU → CPU automatique"""
    
    def __init__(
        self,
        model_path: str = "assets/hand_landmarker.task",
        callback: Callable = None,
        max_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        self.model_path = model_path
        self.callback = callback
        self.max_hands = max_hands
        self.min_detection = min_detection_confidence
        self.min_presence = min_presence_confidence
        self.min_tracking = min_tracking_confidence
        
        self.landmarker: Optional[vision.HandLandmarker] = None
        self.using_gpu = False
        self._options = None
    
    def initialize(self) -> bool:
        """Initialise MediaPipe avec fallback CPU si GPU échoue"""
        # Tente GPU d'abord
        try:
            print("⚡ Attempting GPU initialization...")
            self._options = self._build_options(use_gpu=True)
            self.landmarker = vision.HandLandmarker.create_from_options(self._options)
            self.using_gpu = True
            print("✅ GPU initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️ GPU failed ({e}), falling back to CPU...")
            return self._fallback_cpu()
    
    def _build_options(self, use_gpu: bool) -> vision.HandLandmarkerOptions:
        """Construit les options MediaPipe"""
        delegate = (
            python.BaseOptions.Delegate.GPU if use_gpu 
            else python.BaseOptions.Delegate.CPU
        )
        base_options = python.BaseOptions(
            model_asset_path=self.model_path,
            delegate=delegate
        )
        return vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.min_detection,
            min_hand_presence_confidence=self.min_presence,
            min_tracking_confidence=self.min_tracking,
            result_callback=self.callback
        )
    
    def _fallback_cpu(self) -> bool:
        """Fallback vers CPU"""
        try:
            self._options = self._build_options(use_gpu=False)
            self.landmarker = vision.HandLandmarker.create_from_options(self._options)
            self.using_gpu = False
            print("✅ CPU fallback active")
            return True
        except Exception as e:
            print(f"❌ CPU init failed: {e}")
            return False
    
    def detect(self, frame: np.ndarray, timestamp_ms: int):
        """Détecte les mains de manière asynchrone"""
        if self.landmarker is None:
            return
        
        # Convertit BGR → RGB si nécessaire
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame_rgb = frame[:, :, ::-1]  # BGR to RGB (view, no copy)
        else:
            frame_rgb = frame
            
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=np.ascontiguousarray(frame_rgb)
        )
        self.landmarker.detect_async(mp_image, timestamp_ms)
    
    def close(self):
        """Ferme le landmarker"""
        if self.landmarker:
            self.landmarker.close()
            self.landmarker = None
            print("🖐️ HandTracker closed")
    
    def __enter__(self):
        self.initialize()
        return self
    
    def __exit__(self, *args):
        self.close()
