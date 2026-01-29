import time
import threading
import numpy as np
import cv2
from collections import deque
from typing import Optional, Tuple, List
import subprocess

# ============================================================================
# 1. PROFILING
# ============================================================================

class PerformanceProfiler:
    """Profiler pour mesurer précisément les temps de chaque étape"""
    
    def __init__(self, window_size=100):
        self.metrics = {
            'capture': deque(maxlen=window_size),
            'inference': deque(maxlen=window_size),
            'total': deque(maxlen=window_size),
        }
        self.timestamps = {}
    
    def mark(self, event_name: str):
        self.timestamps[event_name] = time.perf_counter()
    
    def measure(self, stage: str, start: str, end: str):
        if start in self.timestamps and end in self.timestamps:
            duration_ms = (self.timestamps[end] - self.timestamps[start]) * 1000
            if stage in self.metrics:
                self.metrics[stage].append(duration_ms)
            else:
                 self.metrics[stage] = deque([duration_ms], maxlen=100)
    
    def get_fps(self):
        if self.metrics['total']:
            avg_frame_time = np.mean(list(self.metrics['total']))
            return 1000 / avg_frame_time if avg_frame_time > 0 else 0
        return 0

    def get_inference_time(self):
        if self.metrics['inference']:
            return np.mean(list(self.metrics['inference']))
        return 0

# ============================================================================
# 2. ADAPTIVE FILTERING
# ============================================================================

class OneEuroFilter:
    def __init__(self, min_cutoff=0.004, beta=0.7, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None
    
    def __call__(self, x: float, timestamp: float) -> float:
        if self.x_prev is None:
            self.x_prev = x
            self.t_prev = timestamp
            return x
        
        dt = timestamp - self.t_prev
        if dt <= 0: return self.x_prev
        
        freq = 1.0 / dt
        dx = (x - self.x_prev) * freq
        edx = self._smoothing_factor(freq, self.d_cutoff)
        dx_filtered = self._exponential_smoothing(edx, dx, self.dx_prev)
        
        cutoff = self.min_cutoff + self.beta * abs(dx_filtered)
        ex = self._smoothing_factor(freq, cutoff)
        x_filtered = self._exponential_smoothing(ex, x, self.x_prev)
        
        self.x_prev = x_filtered
        self.dx_prev = dx_filtered
        self.t_prev = timestamp
        return x_filtered
    
    @staticmethod
    def _smoothing_factor(freq, cutoff):
        r = 2 * np.pi * cutoff / freq
        return r / (r + 1)
    
    @staticmethod
    def _exponential_smoothing(alpha, x, x_prev):
        return alpha * x + (1 - alpha) * x_prev

class AdaptiveOneEuroFilter:
    """Version adaptative qui ajuste min_cutoff selon la vitesse"""
    def __init__(self):
        self.filter_x = OneEuroFilter(min_cutoff=0.004, beta=0.7)
        self.filter_y = OneEuroFilter(min_cutoff=0.004, beta=0.7)
        self.prev_pos = None
        self.prev_time = None
        
        # Seuils de vitesse (pixels/seconde) - A ajuster selon résolution
        self.FAST_THRESHOLD = 800
        self.MEDIUM_THRESHOLD = 300
        
        # Paramètres
        self.FAST_CUTOFF = 0.001      # Très réactif
        self.MEDIUM_CUTOFF = 0.004    # Équilibré
        self.SLOW_CUTOFF = 0.015      # Très stable (augmenté pour "fixer" le curseur à l'arrêt)
    
    def __call__(self, x: float, y: float, timestamp: float) -> Tuple[float, float]:
        if self.prev_pos is not None and self.prev_time is not None:
            dt = timestamp - self.prev_time
            if dt > 0:
                dx = x - self.prev_pos[0]
                dy = y - self.prev_pos[1]
                speed = np.sqrt(dx**2 + dy**2) / dt
                
                if speed > self.FAST_THRESHOLD:
                    cutoff = self.FAST_CUTOFF
                elif speed > self.MEDIUM_THRESHOLD:
                    cutoff = self.MEDIUM_CUTOFF
                else:
                    cutoff = self.SLOW_CUTOFF
                
                # Mise à jour douce
                self.filter_x.min_cutoff = 0.7 * self.filter_x.min_cutoff + 0.3 * cutoff
                self.filter_y.min_cutoff = 0.7 * self.filter_y.min_cutoff + 0.3 * cutoff
        
        x_filtered = self.filter_x(x, timestamp)
        y_filtered = self.filter_y(y, timestamp)
        
        self.prev_pos = (x, y)
        self.prev_time = timestamp
        return x_filtered, y_filtered

# ============================================================================
# 3. CAMERA CONFIGURATION
# ============================================================================

class CameraConfigurator:
    @staticmethod
    def configure_camera(device='/dev/video0', exposure_auto=1, exposure_absolute=150, focus_auto=0, focus_absolute=0, gain=100):
        commands = [
            f'v4l2-ctl -d {device} --set-ctrl=exposure_auto={exposure_auto}',
            f'v4l2-ctl -d {device} --set-ctrl=exposure_absolute={exposure_absolute}',
            f'v4l2-ctl -d {device} --set-ctrl=focus_auto={focus_auto}',
            f'v4l2-ctl -d {device} --set-ctrl=focus_absolute={focus_absolute}',
            f'v4l2-ctl -d {device} --set-ctrl=gain={gain}',
            f'v4l2-ctl -d {device} --set-ctrl=white_balance_temperature_auto=0',
            f'v4l2-ctl -d {device} --set-ctrl=white_balance_temperature=4600',
        ]
        for cmd in commands:
            try:
                subprocess.run(cmd.split(), check=False, capture_output=True)
            except:
                pass

# ============================================================================
# 4. MAPPING & CALIBRATION
# ============================================================================

class AdaptiveSensitivityMapper:
    """Mapping non-linéaire avec sensibilité adaptative et courbe exponentielle"""
    def __init__(self, screen_width: int, screen_height: int, gamma=1.3):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gamma = gamma
        self.deadzone = 0.02  # 2% au centre
    
    def map(self, x_normalized: float, y_normalized: float) -> Tuple[int, int]:
        # Normaliser [-1, 1] centré (Input est 0-1)
        x_centered = (x_normalized - 0.5) * 2
        y_centered = (y_normalized - 0.5) * 2
        
        # Deadzone
        if abs(x_centered) < self.deadzone: x_mapped = 0
        else: x_mapped = np.sign(x_centered) * (abs(x_centered) ** self.gamma)
        
        if abs(y_centered) < self.deadzone: y_mapped = 0
        else: y_mapped = np.sign(y_centered) * (abs(y_centered) ** self.gamma)
        
        # Reconvertir 0-1
        x_final = (x_mapped / 2 + 0.5)
        y_final = (y_mapped / 2 + 0.5)
        
        # Scale to screen
        return int(x_final * self.screen_width), int(y_final * self.screen_height)

class CalibrationSystem:
    """Système de calibration 4-points pour mapping caméra→écran"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.transform_matrix = None
        self.is_calibrated = False
    
    def calibrate(self, camera_points: List[Tuple[float, float]]) -> bool:
        """
        Effectuer la calibration
        Args:
            camera_points: 4 points détectés par la caméra [top-left, top-right, bottom-right, bottom-left]
        """
        if len(camera_points) != 4:
            return False
        
        # Points cibles à l'écran (coins)
        screen_points = [
            (0, 0),
            (self.screen_width, 0),
            (self.screen_width, self.screen_height),
            (0, self.screen_height)
        ]
        
        # Convertir en numpy
        src_pts = np.float32(camera_points)
        dst_pts = np.float32(screen_points)
        
        # Calculer transformation perspective
        self.transform_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        self.is_calibrated = True
        
        return True
    
    def apply(self, x: float, y: float) -> Tuple[float, float]:
        """Appliquer la transformation calibrée"""
        if not self.is_calibrated:
            # Pas calibré → mapping simple
            return x * self.screen_width, y * self.screen_height
        
        # Appliquer transformation perspective
        point = np.array([[[x, y]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(point, self.transform_matrix)
        
        return float(transformed[0][0][0]), float(transformed[0][0][1])
    
    def save(self, filepath: str):
        if self.is_calibrated:
            np.save(filepath, self.transform_matrix)
    
    def load(self, filepath: str) -> bool:
        try:
            self.transform_matrix = np.load(filepath)
            self.is_calibrated = True
            return True
        except:
            return False

# ============================================================================
# 5. VISUAL FEEDBACK & EXTRAS
# ============================================================================

class VisualFeedback:
    @staticmethod
    def draw_skeleton(frame: np.ndarray, landmarks: List[Tuple[int, int]]):
        CONNECTIONS = frozenset([
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ])
        
        # Dessiner les liens
        for start_idx, end_idx in CONNECTIONS:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                pt1 = landmarks[start_idx]
                pt2 = landmarks[end_idx]
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
        
        # Dessiner les points
        for point in landmarks:
            cv2.circle(frame, point, 4, (255, 0, 0), -1)
    
    @staticmethod
    def draw_fps(frame: np.ndarray, fps: float):
        text = f"FPS: {fps:.1f}"
        cv2.putText(frame, text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

class DwellClickDetector:
    def __init__(self, dwell_time=0.4, tolerance_px=15):
        self.dwell_time = dwell_time
        self.tolerance = tolerance_px
        self.dwell_start = None
        self.dwell_pos = None
        
    def update(self, x: float, y: float, timestamp: float) -> Tuple[bool, float]:
        if self.dwell_pos is None:
            self.dwell_pos = (x, y)
            self.dwell_start = timestamp
            return False, 0.0
            
        distance = np.sqrt((x - self.dwell_pos[0])**2 + (y - self.dwell_pos[1])**2)
        
        if distance > self.tolerance:
            self.dwell_pos = (x, y)
            self.dwell_start = timestamp
            return False, 0.0
            
        elapsed = timestamp - self.dwell_start
        progress = min(elapsed / self.dwell_time, 1.0)
        
        if elapsed >= self.dwell_time:
            self.dwell_pos = None
            return True, 1.0
            
        return False, progress
