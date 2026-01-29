#!/usr/bin/env python3
"""
Hand Mouse OS - Code d'Optimisation Complet
===========================================
Implémentations prêtes à l'emploi pour toutes les optimisations
"""

import time
import threading
import numpy as np
import cv2
from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple, List
import uinput


# ============================================================================
# 1. PROFILING & METRICS
# ============================================================================

class PerformanceProfiler:
    """Profiler pour mesurer précisément les temps de chaque étape"""
    
    def __init__(self, window_size=100):
        self.metrics = {
            'capture': deque(maxlen=window_size),
            'preprocess': deque(maxlen=window_size),
            'inference': deque(maxlen=window_size),
            'postprocess': deque(maxlen=window_size),
            'total': deque(maxlen=window_size),
        }
        self.timestamps = {}
    
    def mark(self, event_name: str):
        """Marquer un timestamp"""
        self.timestamps[event_name] = time.perf_counter()
    
    def measure(self, stage: str, start: str, end: str):
        """Calculer et enregistrer la durée d'une étape"""
        if start in self.timestamps and end in self.timestamps:
            duration_ms = (self.timestamps[end] - self.timestamps[start]) * 1000
            self.metrics[stage].append(duration_ms)
    
    def get_stats(self, stage: str) -> dict:
        """Obtenir les statistiques d'une étape"""
        if not self.metrics[stage]:
            return {'avg': 0, 'min': 0, 'max': 0, 'p95': 0}
        
        data = list(self.metrics[stage])
        return {
            'avg': np.mean(data),
            'min': np.min(data),
            'max': np.max(data),
            'p95': np.percentile(data, 95),
        }
    
    def print_report(self):
        """Afficher un rapport de performance"""
        print("\n" + "="*60)
        print("📊 RAPPORT DE PERFORMANCE")
        print("="*60)
        
        for stage in ['capture', 'preprocess', 'inference', 'postprocess', 'total']:
            stats = self.get_stats(stage)
            print(f"\n{stage.upper():>15}: "
                  f"Avg={stats['avg']:6.2f}ms  "
                  f"Min={stats['min']:6.2f}ms  "
                  f"Max={stats['max']:6.2f}ms  "
                  f"P95={stats['p95']:6.2f}ms")
        
        # Calcul FPS
        if self.metrics['total']:
            avg_frame_time = np.mean(list(self.metrics['total']))
            fps = 1000 / avg_frame_time if avg_frame_time > 0 else 0
            print(f"\n{'FPS':>15}: {fps:.1f}")
        
        print("="*60 + "\n")


# ============================================================================
# 2. RING BUFFER LATEST-ONLY
# ============================================================================

class LatestFrameBuffer:
    """Buffer qui garde uniquement la frame la plus récente"""
    
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()
        self.new_frame_available = threading.Event()
        self.frame_count = 0
        self.dropped_count = 0
    
    def put(self, frame: np.ndarray):
        """Déposer une frame (écrase l'ancienne si non consommée)"""
        with self.lock:
            if self.frame is not None and not self.new_frame_available.is_set():
                # Frame précédente pas encore consommée = drop
                self.dropped_count += 1
            
            self.frame = frame.copy()
            self.frame_count += 1
            self.new_frame_available.set()
    
    def get(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """Récupérer la dernière frame disponible"""
        if self.new_frame_available.wait(timeout):
            with self.lock:
                frame = self.frame
                self.new_frame_available.clear()
                return frame
        return None
    
    def get_stats(self) -> dict:
        """Statistiques du buffer"""
        return {
            'total_frames': self.frame_count,
            'dropped_frames': self.dropped_count,
            'drop_rate': (self.dropped_count / self.frame_count * 100) 
                        if self.frame_count > 0 else 0
        }


# ============================================================================
# 3. ADAPTIVE ONE EURO FILTER
# ============================================================================

class OneEuroFilter:
    """Implementation du filtre 1€ classique"""
    
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
        
        # Calculer la fréquence
        dt = timestamp - self.t_prev
        if dt <= 0:
            return self.x_prev
        
        freq = 1.0 / dt
        
        # Filtrer la dérivée
        dx = (x - self.x_prev) * freq
        edx = self._smoothing_factor(freq, self.d_cutoff)
        dx_filtered = self._exponential_smoothing(edx, dx, self.dx_prev)
        
        # Filtrer la position
        cutoff = self.min_cutoff + self.beta * abs(dx_filtered)
        ex = self._smoothing_factor(freq, cutoff)
        x_filtered = self._exponential_smoothing(ex, x, self.x_prev)
        
        # Sauvegarder l'état
        self.x_prev = x_filtered
        self.dx_prev = dx_filtered
        self.t_prev = timestamp
        
        return x_filtered
    
    @staticmethod
    def _smoothing_factor(freq: float, cutoff: float) -> float:
        r = 2 * np.pi * cutoff / freq
        return r / (r + 1)
    
    @staticmethod
    def _exponential_smoothing(alpha: float, x: float, x_prev: float) -> float:
        return alpha * x + (1 - alpha) * x_prev


class AdaptiveOneEuroFilter:
    """Version adaptative qui ajuste min_cutoff selon la vitesse"""
    
    def __init__(self):
        self.filter_x = OneEuroFilter(min_cutoff=0.004, beta=0.7)
        self.filter_y = OneEuroFilter(min_cutoff=0.004, beta=0.7)
        self.prev_pos = None
        self.prev_time = None
        
        # Seuils de vitesse (pixels/seconde)
        self.FAST_THRESHOLD = 800
        self.MEDIUM_THRESHOLD = 300
        
        # Paramètres de filtrage selon vitesse
        self.FAST_CUTOFF = 0.001      # Très réactif
        self.MEDIUM_CUTOFF = 0.004    # Équilibré
        self.SLOW_CUTOFF = 0.010      # Très stable
    
    def __call__(self, x: float, y: float, timestamp: float) -> Tuple[float, float]:
        """Filtrer avec adaptation dynamique"""
        
        # Calculer la vitesse si possible
        if self.prev_pos is not None and self.prev_time is not None:
            dt = timestamp - self.prev_time
            if dt > 0:
                dx = x - self.prev_pos[0]
                dy = y - self.prev_pos[1]
                speed = np.sqrt(dx**2 + dy**2) / dt
                
                # Adapter le min_cutoff selon la vitesse
                if speed > self.FAST_THRESHOLD:
                    cutoff = self.FAST_CUTOFF
                elif speed > self.MEDIUM_THRESHOLD:
                    cutoff = self.MEDIUM_CUTOFF
                else:
                    cutoff = self.SLOW_CUTOFF
                
                # Mise à jour douce du cutoff pour éviter les saccades
                self.filter_x.min_cutoff = (0.7 * self.filter_x.min_cutoff + 
                                           0.3 * cutoff)
                self.filter_y.min_cutoff = (0.7 * self.filter_y.min_cutoff + 
                                           0.3 * cutoff)
        
        # Appliquer le filtre
        x_filtered = self.filter_x(x, timestamp)
        y_filtered = self.filter_y(y, timestamp)
        
        # Sauvegarder pour calcul vitesse
        self.prev_pos = (x, y)
        self.prev_time = timestamp
        
        return x_filtered, y_filtered


# ============================================================================
# 4. CAMERA CONFIGURATION
# ============================================================================

class CameraConfigurator:
    """Configuration optimale de la caméra avec v4l2"""
    
    @staticmethod
    def list_cameras():
        """Lister les caméras disponibles"""
        import subprocess
        result = subprocess.run(['v4l2-ctl', '--list-devices'],
                              capture_output=True, text=True)
        print(result.stdout)
    
    @staticmethod
    def get_controls(device='/dev/video0'):
        """Obtenir les contrôles disponibles"""
        import subprocess
        result = subprocess.run(['v4l2-ctl', '-d', device, '--list-ctrls'],
                              capture_output=True, text=True)
        return result.stdout
    
    @staticmethod
    def configure_camera(device='/dev/video0', 
                        exposure_auto=1,
                        exposure_absolute=150,
                        focus_auto=0,
                        focus_absolute=0,
                        gain=100):
        """
        Configure la caméra pour performance optimale
        
        Args:
            device: Chemin du device (ex: /dev/video0)
            exposure_auto: 1=manuel, 3=auto
            exposure_absolute: Valeur d'exposition (100-500 typique)
            focus_auto: 0=manuel, 1=auto
            focus_absolute: Distance de focus (0-255)
            gain: Gain ISO (0-255)
        """
        import subprocess
        
        commands = [
            f'v4l2-ctl -d {device} --set-ctrl=exposure_auto={exposure_auto}',
            f'v4l2-ctl -d {device} --set-ctrl=exposure_absolute={exposure_absolute}',
        ]
        
        # Focus (si supporté)
        if focus_auto is not None:
            commands.append(f'v4l2-ctl -d {device} --set-ctrl=focus_auto={focus_auto}')
        if focus_absolute is not None:
            commands.append(f'v4l2-ctl -d {device} --set-ctrl=focus_absolute={focus_absolute}')
        
        # Gain
        if gain is not None:
            commands.append(f'v4l2-ctl -d {device} --set-ctrl=gain={gain}')
        
        # White balance manuel (éviter les variations)
        commands.extend([
            f'v4l2-ctl -d {device} --set-ctrl=white_balance_temperature_auto=0',
            f'v4l2-ctl -d {device} --set-ctrl=white_balance_temperature=4600',
        ])
        
        for cmd in commands:
            try:
                subprocess.run(cmd.split(), check=False, 
                             capture_output=True, text=True)
            except Exception as e:
                print(f"⚠️  Commande échouée: {cmd}")
                print(f"   Erreur: {e}")
        
        print("✅ Caméra configurée")
    
    @staticmethod
    def create_optimized_capture(device_id=0, width=640, height=480, fps=30):
        """
        Créer un VideoCapture optimisé avec GStreamer si disponible
        """
        # Essayer GStreamer d'abord
        try:
            pipeline = (
                f'v4l2src device=/dev/video{device_id} ! '
                f'video/x-raw,format=YUY2,width={width},height={height},'
                f'framerate={fps}/1 ! '
                'videoconvert ! '
                'video/x-raw,format=BGR ! '
                'appsink'
            )
            cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            if cap.isOpened():
                print("✅ Pipeline GStreamer activé")
                return cap
        except:
            pass
        
        # Fallback sur OpenCV standard
        cap = cv2.VideoCapture(device_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer minimal
        
        print("⚠️  Pipeline OpenCV standard (pas GStreamer)")
        return cap


# ============================================================================
# 5. PREALLOCATED BUFFERS
# ============================================================================

class PreallocatedBuffers:
    """Gestionnaire de buffers préalloués pour éviter copies"""
    
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        
        # Buffers principaux
        self.capture_buffer = np.empty((height, width, 3), dtype=np.uint8)
        self.rgb_buffer = np.empty((height, width, 3), dtype=np.uint8)
        self.gray_buffer = np.empty((height, width), dtype=np.uint8)
        
        # Buffer pour resize (si nécessaire)
        self.resize_buffer = None
    
    def get_capture_buffer(self) -> np.ndarray:
        """Retourne le buffer de capture"""
        return self.capture_buffer
    
    def convert_to_rgb_inplace(self, bgr_frame: np.ndarray) -> np.ndarray:
        """Conversion BGR→RGB in-place"""
        cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB, dst=self.rgb_buffer)
        return self.rgb_buffer
    
    def convert_to_gray_inplace(self, bgr_frame: np.ndarray) -> np.ndarray:
        """Conversion BGR→GRAY in-place"""
        cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY, dst=self.gray_buffer)
        return self.gray_buffer
    
    def resize_inplace(self, frame: np.ndarray, 
                      target_width: int, 
                      target_height: int) -> np.ndarray:
        """Resize in-place dans un buffer dédié"""
        if (self.resize_buffer is None or 
            self.resize_buffer.shape[:2] != (target_height, target_width)):
            channels = frame.shape[2] if len(frame.shape) == 3 else 1
            self.resize_buffer = np.empty((target_height, target_width, channels), 
                                         dtype=frame.dtype)
        
        cv2.resize(frame, (target_width, target_height),
                  dst=self.resize_buffer,
                  interpolation=cv2.INTER_LINEAR)
        return self.resize_buffer


# ============================================================================
# 6. DWELL CLICK DETECTOR
# ============================================================================

class DwellClickDetector:
    """Détecteur de clic par maintien de position"""
    
    def __init__(self, dwell_time=0.4, tolerance_px=15):
        self.dwell_time = dwell_time
        self.tolerance = tolerance_px
        self.dwell_start = None
        self.dwell_pos = None
        self.in_dwell = False
    
    def update(self, x: float, y: float, timestamp: float) -> Tuple[bool, float]:
        """
        Mise à jour du détecteur
        
        Returns:
            (click_detected, progress): click_detected est True si clic confirmé,
                                       progress est entre 0.0 et 1.0
        """
        if self.dwell_pos is None:
            # Premier point
            self.dwell_pos = (x, y)
            self.dwell_start = timestamp
            self.in_dwell = True
            return False, 0.0
        
        # Calculer distance depuis point de départ
        distance = np.sqrt((x - self.dwell_pos[0])**2 + 
                          (y - self.dwell_pos[1])**2)
        
        if distance > self.tolerance:
            # Mouvement détecté → reset
            self.dwell_pos = (x, y)
            self.dwell_start = timestamp
            self.in_dwell = True
            return False, 0.0
        
        # Calculer progression
        elapsed = timestamp - self.dwell_start
        progress = min(elapsed / self.dwell_time, 1.0)
        
        if elapsed >= self.dwell_time:
            # Clic détecté!
            self.dwell_pos = None
            self.in_dwell = False
            return True, 1.0
        
        return False, progress
    
    def reset(self):
        """Réinitialiser le détecteur"""
        self.dwell_pos = None
        self.dwell_start = None
        self.in_dwell = False


# ============================================================================
# 7. VISUAL FEEDBACK
# ============================================================================

class VisualFeedback:
    """Rendu de feedback visuel pour l'utilisateur"""
    
    @staticmethod
    def draw_dwell_progress(frame: np.ndarray, 
                           x: int, y: int, 
                           progress: float,
                           radius: int = 30):
        """Dessiner cercle de progression pour dwell click"""
        # Cercle de fond
        cv2.circle(frame, (x, y), radius, (50, 50, 50), 2)
        
        # Arc de progression
        if progress > 0:
            angle = int(360 * progress)
            # Couleur: vert → jaune → rouge selon progression
            if progress < 0.5:
                color = (0, 255, 0)  # Vert
            elif progress < 0.8:
                color = (0, 255, 255)  # Jaune
            else:
                color = (0, 165, 255)  # Orange
            
            cv2.ellipse(frame, (x, y), (radius, radius),
                       -90, 0, angle, color, 3)
        
        # Point central
        cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)
    
    @staticmethod
    def draw_hand_skeleton(frame: np.ndarray, 
                          landmarks: List[Tuple[int, int]],
                          connections: List[Tuple[int, int]] = None):
        """Dessiner le squelette de la main"""
        if connections is None:
            # Connexions standards MediaPipe
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),  # Pouce
                (0, 5), (5, 6), (6, 7), (7, 8),  # Index
                (0, 9), (9, 10), (10, 11), (11, 12),  # Majeur
                (0, 13), (13, 14), (14, 15), (15, 16),  # Annulaire
                (0, 17), (17, 18), (18, 19), (19, 20),  # Auriculaire
                (5, 9), (9, 13), (13, 17)  # Paume
            ]
        
        # Dessiner les connexions
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                pt1 = landmarks[start_idx]
                pt2 = landmarks[end_idx]
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
        
        # Dessiner les points
        for point in landmarks:
            cv2.circle(frame, point, 4, (255, 0, 0), -1)
    
    @staticmethod
    def draw_fps(frame: np.ndarray, fps: float):
        """Afficher les FPS"""
        text = f"FPS: {fps:.1f}"
        cv2.putText(frame, text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    @staticmethod
    def draw_status(frame: np.ndarray, status: str, color=(0, 255, 0)):
        """Afficher un message de statut"""
        cv2.putText(frame, status, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


# ============================================================================
# 8. CALIBRATION SYSTEM
# ============================================================================

class CalibrationSystem:
    """Système de calibration 4-points pour mapping caméra→écran"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.transform_matrix = None
        self.is_calibrated = False
    
    def calibrate(self, camera_points: List[Tuple[float, float]]) -> bool:
        """
        Effectuer la calibration
        
        Args:
            camera_points: 4 points détectés par la caméra 
                          [top-left, top-right, bottom-right, bottom-left]
        
        Returns:
            True si succès
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
        """Sauvegarder la calibration"""
        if self.is_calibrated:
            np.save(filepath, self.transform_matrix)
    
    def load(self, filepath: str) -> bool:
        """Charger une calibration"""
        try:
            self.transform_matrix = np.load(filepath)
            self.is_calibrated = True
            return True
        except:
            return False


# ============================================================================
# 9. ADAPTIVE SENSITIVITY MAPPING
# ============================================================================

class AdaptiveSensitivityMapper:
    """Mapping non-linéaire avec sensibilité adaptative"""
    
    def __init__(self, screen_width: int, screen_height: int, gamma=1.3):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gamma = gamma
        self.deadzone = 0.05  # 5% au centre
    
    def map(self, x_normalized: float, y_normalized: float) -> Tuple[float, float]:
        """
        Mapper coordonnées normalisées [0,1] vers écran avec courbe adaptative
        
        Args:
            x_normalized, y_normalized: Coordonnées entre 0 et 1
        
        Returns:
            (x_screen, y_screen): Coordonnées écran en pixels
        """
        # Normaliser [-1, 1] centré
        x_centered = (x_normalized - 0.5) * 2
        y_centered = (y_normalized - 0.5) * 2
        
        # Appliquer deadzone centrale
        if abs(x_centered) < self.deadzone:
            x_mapped = 0
        else:
            # Courbe expo: plus de contrôle au centre
            x_mapped = np.sign(x_centered) * (abs(x_centered) ** self.gamma)
        
        if abs(y_centered) < self.deadzone:
            y_mapped = 0
        else:
            y_mapped = np.sign(y_centered) * (abs(y_centered) ** self.gamma)
        
        # Reconvertir en coordonnées écran
        x_screen = (x_mapped / 2 + 0.5) * self.screen_width
        y_screen = (y_mapped / 2 + 0.5) * self.screen_height
        
        # Clamp
        x_screen = np.clip(x_screen, 0, self.screen_width - 1)
        y_screen = np.clip(y_screen, 0, self.screen_height - 1)
        
        return x_screen, y_screen


# ============================================================================
# 10. UINPUT MOUSE DRIVER (Optimisé)
# ============================================================================

class OptimizedMouseDriver:
    """Driver souris optimisé avec événements absolus"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Créer device uinput avec événements absolus
        events = (
            uinput.EV_ABS + (
                (uinput.ABS_X, (0, screen_width, 0, 0)),
                (uinput.ABS_Y, (0, screen_height, 0, 0)),
            ),
            uinput.BTN_LEFT,
            uinput.BTN_RIGHT,
            uinput.BTN_MIDDLE,
        )
        
        self.device = uinput.Device(events, name='HandMouseOS-Optimized')
        print("✅ Device virtuel créé: HandMouseOS-Optimized")
    
    def move(self, x: int, y: int):
        """Déplacer le curseur (coordonnées absolues)"""
        x = int(np.clip(x, 0, self.screen_width - 1))
        y = int(np.clip(y, 0, self.screen_height - 1))
        
        # Événements absolus pour précision maximale
        self.device.emit(uinput.ABS_X, x, syn=False)
        self.device.emit(uinput.ABS_Y, y, syn=True)
    
    def click(self, button='left'):
        """Effectuer un clic"""
        btn_map = {
            'left': uinput.BTN_LEFT,
            'right': uinput.BTN_RIGHT,
            'middle': uinput.BTN_MIDDLE,
        }
        
        btn = btn_map.get(button, uinput.BTN_LEFT)
        
        # Clic = press + release
        self.device.emit(btn, 1)  # Press
        self.device.emit(btn, 0)  # Release
    
    def press(self, button='left'):
        """Presser un bouton (sans relâcher)"""
        btn_map = {
            'left': uinput.BTN_LEFT,
            'right': uinput.BTN_RIGHT,
            'middle': uinput.BTN_MIDDLE,
        }
        btn = btn_map.get(button, uinput.BTN_LEFT)
        self.device.emit(btn, 1)
    
    def release(self, button='left'):
        """Relâcher un bouton"""
        btn_map = {
            'left': uinput.BTN_LEFT,
            'right': uinput.BTN_RIGHT,
            'middle': uinput.BTN_MIDDLE,
        }
        btn = btn_map.get(button, uinput.BTN_LEFT)
        self.device.emit(btn, 0)
    
    def close(self):
        """Fermer le device"""
        if hasattr(self, 'device'):
            del self.device


# ============================================================================
# 11. EXEMPLE D'INTÉGRATION COMPLÈTE
# ============================================================================

def example_optimized_pipeline():
    """
    Exemple d'utilisation de tous les composants ensemble
    """
    import screeninfo
    
    # Configuration
    CAMERA_ID = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Obtenir résolution écran
    screen = screeninfo.get_monitors()[0]
    SCREEN_WIDTH = screen.width
    SCREEN_HEIGHT = screen.height
    
    print("="*60)
    print("🚀 HAND MOUSE OS - Pipeline Optimisé")
    print("="*60)
    print(f"Écran: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"Caméra: {CAMERA_WIDTH}x{CAMERA_HEIGHT} @ {CAMERA_FPS}fps")
    print("="*60 + "\n")
    
    # Initialisation composants
    profiler = PerformanceProfiler()
    frame_buffer = LatestFrameBuffer()
    buffers = PreallocatedBuffers(CAMERA_WIDTH, CAMERA_HEIGHT)
    cursor_filter = AdaptiveOneEuroFilter()
    dwell_detector = DwellClickDetector()
    calibration = CalibrationSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    sensitivity_mapper = AdaptiveSensitivityMapper(SCREEN_WIDTH, SCREEN_HEIGHT)
    mouse = OptimizedMouseDriver(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Configuration caméra
    print("⚙️  Configuration de la caméra...")
    CameraConfigurator.configure_camera(
        device='/dev/video0',
        exposure_absolute=150,
        gain=100
    )
    
    # Ouvrir caméra
    cap = CameraConfigurator.create_optimized_capture(
        CAMERA_ID, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS
    )
    
    if not cap.isOpened():
        print("❌ Impossible d'ouvrir la caméra")
        return
    
    print("\n✅ Système prêt!")
    print("👋 Montrez votre main devant la caméra")
    print("⏱️  Maintenez position 0.4s pour cliquer")
    print("🔴 Appuyez sur 'q' pour quitter\n")
    
    # Boucle principale
    try:
        frame_count = 0
        last_report_time = time.time()
        
        while True:
            profiler.mark('start')
            
            # Capture
            ret, frame = cap.read()
            if not ret:
                continue
            
            profiler.mark('captured')
            profiler.measure('capture', 'start', 'captured')
            
            # Déposer dans buffer (pour découplage si multiprocessing)
            frame_buffer.put(frame)
            
            # TODO: Ici, intégrer MediaPipe inference
            # Pour l'exemple, on simule des coordonnées
            # hand_detected = True
            # hand_x, hand_y = 0.5, 0.5  # Coordonnées normalisées [0,1]
            
            profiler.mark('inferred')
            profiler.measure('inference', 'captured', 'inferred')
            
            # Filtrage & mapping
            timestamp = time.time()
            # filtered_x, filtered_y = cursor_filter(hand_x, hand_y, timestamp)
            # screen_x, screen_y = sensitivity_mapper.map(filtered_x, filtered_y)
            
            profiler.mark('filtered')
            profiler.measure('postprocess', 'inferred', 'filtered')
            
            # Détection clic
            # click_detected, progress = dwell_detector.update(
            #     screen_x, screen_y, timestamp
            # )
            
            # if click_detected:
            #     mouse.click('left')
            # else:
            #     mouse.move(int(screen_x), int(screen_y))
            
            # Feedback visuel
            display_frame = frame.copy()
            VisualFeedback.draw_fps(display_frame, 
                                   1000 / profiler.get_stats('total')['avg']
                                   if profiler.metrics['total'] else 0)
            
            cv2.imshow('Hand Mouse OS', display_frame)
            
            profiler.mark('end')
            profiler.measure('total', 'start', 'end')
            
            # Rapport toutes les 5 secondes
            frame_count += 1
            if time.time() - last_report_time > 5.0:
                profiler.print_report()
                buffer_stats = frame_buffer.get_stats()
                print(f"📊 Frames droppées: {buffer_stats['dropped_frames']} "
                      f"({buffer_stats['drop_rate']:.1f}%)\n")
                last_report_time = time.time()
            
            # Gestion clavier
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        mouse.close()
        print("\n✅ Arrêt propre du système")


if __name__ == '__main__':
    print(__doc__)
    print("\n⚠️  Ce fichier contient les implémentations de référence.")
    print("Pour exécuter l'exemple complet: décommentez la ligne ci-dessous\n")
    
    # Décommenter pour tester:
    # example_optimized_pipeline()
