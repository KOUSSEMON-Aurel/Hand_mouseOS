# -*- coding: utf-8 -*-
"""
Configuration centralisée pour Hand Mouse OS
Charge les paramètres depuis config.yaml si disponible
"""
import os
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class CameraConfig:
    """Configuration de la caméra"""
    indices: List[int] = field(default_factory=lambda: [0, 1])
    backend: str = "v4l2"
    fps: int = 30
    resolution: Tuple[int, int] = (640, 480)


@dataclass
class MediaPipeConfig:
    """Configuration de MediaPipe"""
    model_path: str = "assets/hand_landmarker.task"
    max_hands: int = 2
    min_detection_confidence: float = 0.5
    min_presence_confidence: float = 0.5
    min_tracking_confidence: float = 0.5


@dataclass
class MouseConfig:
    """Configuration de la souris"""
    sensitivity: float = 1.0
    smoothing: str = "hybrid"  # one_euro, kalman, hybrid
    min_cutoff: float = 1.0
    beta: float = 0.007


@dataclass
class PerformanceConfig:
    """Configuration performance"""
    profiling_enabled: bool = False
    max_fps: int = 60
    use_rust_acceleration: bool = True


@dataclass
class AppConfig:
    """Configuration complète de l'application"""
    camera: CameraConfig = field(default_factory=CameraConfig)
    mediapipe: MediaPipeConfig = field(default_factory=MediaPipeConfig)
    mouse: MouseConfig = field(default_factory=MouseConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # UI
    overlay_position: str = "top_left"
    keyboard_layout: str = "azerty"
    
    @classmethod
    def load(cls, config_path: str = None) -> "AppConfig":
        """Charge la config depuis un fichier YAML si disponible"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config", "default.yaml"
            )
        
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path) as f:
                    data = yaml.safe_load(f)
                return cls._from_dict(data)
            except Exception as e:
                print(f"⚠️ Config load failed: {e}, using defaults")
        
        return cls()
    
    @classmethod
    def _from_dict(cls, data: dict) -> "AppConfig":
        """Construit la config depuis un dict"""
        config = cls()
        
        if "camera" in data:
            config.camera = CameraConfig(**data["camera"])
        if "mediapipe" in data:
            config.mediapipe = MediaPipeConfig(**data["mediapipe"])
        if "mouse" in data:
            config.mouse = MouseConfig(**data["mouse"])
        if "performance" in data:
            config.performance = PerformanceConfig(**data["performance"])
        
        return config


# Instance globale
config = AppConfig()
