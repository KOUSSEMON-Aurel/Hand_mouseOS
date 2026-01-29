# -*- coding: utf-8 -*-
"""
AppCoordinator - Orchestrateur principal de l'application
Responsabilité unique : Coordination des modules, boucle principale épurée
"""
import threading
import time
import cv2
from typing import Optional

from src.vision.camera.manager import CameraManager
from src.vision.tracking.hand_tracker import HandTracker
from src.core.state_manager import StateManager, AppMode
from src.core.event_bus import EventBus, EventType
from src.ui.rendering.skeleton_renderer import SkeletonRenderer

# Import des modules existants (compatibilité)
from src.gesture_classifier import StaticGestureClassifier
from src.context_mode import ContextModeDetector, ContextMode
from src.action_dispatcher import ActionDispatcher, ActionType
from src.feedback_overlay import FeedbackOverlay
from src.mouse_driver import MouseDriver
from src.advanced_filter import HybridMouseFilter
from src.virtual_keyboard import VirtualKeyboard
from src.asl_manager import ASLManager
from src.optimized_utils import PerformanceProfiler


class AppCoordinator:
    """Coordinateur principal - Architecture modulaire"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        print("🔧 Initializing AppCoordinator...")
        
        # Core
        self.state = StateManager()
        self.event_bus = EventBus()
        
        # Vision
        self.camera = CameraManager()
        self.tracker = HandTracker(callback=self._on_detection_result)
        
        # Processing (modules existants)
        self.gesture_classifier = StaticGestureClassifier()
        self.mode_detector = ContextModeDetector()
        
        # Control
        self.mouse = MouseDriver()
        self.filter = HybridMouseFilter()
        self.dispatcher = ActionDispatcher()
        
        # UI
        self.overlay = FeedbackOverlay(position="top_left")
        self.skeleton_renderer = SkeletonRenderer()
        self.virtual_keyboard = VirtualKeyboard(layout="azerty", mode="dwell")
        
        # Features
        self.asl_manager = ASLManager()
        
        # Performance
        self.profiler = PerformanceProfiler()
        
        # Threading
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Timestamps
        self._start_time = 0
        self._last_timestamp_ms = 0
        
        # État interne
        self._current_mode = ContextMode.CURSOR
        self._current_action = ActionType.NONE
        self._active_hand_pos = (0, 0)
        
        self._setup_event_handlers()
        self._start_thread()
        
        print("✅ AppCoordinator initialized")
    
    def _setup_event_handlers(self):
        """Configure les handlers d'événements"""
        self.event_bus.subscribe(EventType.GESTURE_DETECTED, self._on_gesture_event)
    
    def _start_thread(self):
        """Démarre le thread principal"""
        self.state.is_running = True
        self._thread = threading.Thread(target=self._main_loop, daemon=True)
        self._thread.start()
    
    # --- API Publique ---
    
    def start(self):
        """Démarre le traitement"""
        print("▶️ STARTING ENGINE PROCESSING")
        self.state.is_processing = True
        self.event_bus.publish(EventType.ENGINE_STARTED)
    
    def stop(self):
        """Arrête le traitement"""
        print("⏹️ STOPPING ENGINE PROCESSING")
        self.state.is_processing = False
        self.event_bus.publish(EventType.ENGINE_STOPPED)
    
    def shutdown(self):
        """Arrête complètement l'application"""
        self.state.is_running = False
        self.state.is_processing = False
        if self._thread:
            self._thread.join(timeout=2)
        self.camera.release()
        self.tracker.close()
    
    # --- Properties (Compatibilité GUI) ---
    
    @property
    def asl_enabled(self) -> bool:
        return self.asl_manager.enabled
    
    @asl_enabled.setter
    def asl_enabled(self, value: bool):
        self.asl_manager.set_enabled(value)
    
    @property
    def keyboard_enabled(self) -> bool:
        return self.state.keyboard_enabled
    
    @keyboard_enabled.setter
    def keyboard_enabled(self, value: bool):
        self.state.keyboard_enabled = value
    
    @property
    def is_processing(self) -> bool:
        return self.state.is_processing
    
    @property
    def running(self) -> bool:
        return self.state.is_running
    
    # --- Boucle Principale (Simplifiée) ---
    
    def _main_loop(self):
        """Boucle principale épurée"""
        print(f"DEBUG: Thread _run_loop started. Running={self.state.is_running}")
        
        try:
            while self.state.is_running:
                # Attente si pause
                if not self.state.is_processing:
                    self._handle_pause()
                    time.sleep(0.5)
                    continue
                
                # Initialisation si nécessaire
                if not self.camera.is_opened:
                    if not self._initialize_resources():
                        time.sleep(2)
                        continue
                
                # Traitement d'une frame
                self._process_frame()
                
        except Exception as e:
            import traceback
            print(f"❌ CRITICAL ERROR IN MAIN LOOP: {e}")
            traceback.print_exc()
    
    def _handle_pause(self):
        """Gère l'état pause (libère les ressources)"""
        if self.camera.is_opened:
            print("DEBUG: Pausing Engine (Releasing resources)...")
            self.camera.release()
            self.tracker.close()
            if not self.headless:
                cv2.destroyAllWindows()
    
    def _initialize_resources(self) -> bool:
        """Initialise caméra et tracker"""
        print("DEBUG: Initializing Camera and Engine...")
        
        if not self.camera.open():
            return False
        
        if not self.tracker.initialize():
            self.camera.release()
            return False
        
        self._start_time = time.time()
        self._last_timestamp_ms = 0
        
        if not self.headless:
            cv2.namedWindow("Hand Mouse AI - Unified View", cv2.WINDOW_GUI_NORMAL)
        
        return True
    
    def _process_frame(self):
        """Traite une frame complète"""
        self.profiler.mark('start')
        
        # 1. Capture
        frame = self.camera.read()
        if frame is None:
            time.sleep(0.05)
            return
        
        self.profiler.mark('capture')
        
        # 2. Détection (asynchrone)
        timestamp_ms = int((time.time() - self._start_time) * 1000)
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        
        self.tracker.detect(frame, timestamp_ms)
        self.profiler.mark('inference_sent')
        
        # 3. Rendering
        display_frame = self._render_frame(frame)
        
        # 4. Affichage
        if not self.headless:
            self._display_windows(display_frame)
        
        self.profiler.mark('end')
        self.profiler.measure('total', 'start', 'end')
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
    
    def _render_frame(self, frame) -> 'np.ndarray':
        """Rendu de la frame avec overlay"""
        import numpy as np
        h, w = frame.shape[:2]
        
        # Mode d'affichage
        overlay_mode = self._current_mode.value
        display_gesture = "UNKNOWN"
        display_action = ""
        
        with self._lock:
            if self.state.state.primary_hand:
                display_gesture = self.state.state.primary_hand.gesture
        
        # Override ASL
        if self.asl_enabled:
            overlay_mode = "asl"
            display_action = f"SIGNE: {self.asl_manager.get_display_text()}"
            display_gesture = self.asl_manager.last_prediction
        else:
            action_info = self.dispatcher.get_action_info(self._current_action)
            display_action = f"{action_info['emoji']} {action_info['name']}"
        
        # Dessine l'overlay
        frame = self.overlay.draw_zone_indicators(frame, overlay_mode)
        
        if self._active_hand_pos and self._active_hand_pos != (0, 0):
            frame = self.overlay.draw_hand_halo(frame, self._active_hand_pos, overlay_mode)
        
        frame = self.overlay.draw(
            frame=frame,
            mode=overlay_mode,
            gesture=display_gesture,
            action=display_action,
            confidence=1.0
        )
        
        # FPS
        fps = self.profiler.get_fps()
        cv2.putText(frame, f"{int(fps)} FPS", (w - 80, h - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame
    
    def _display_windows(self, frame):
        """Affiche les fenêtres OpenCV"""
        import numpy as np
        
        # Résultats courants
        with self._lock:
            result = getattr(self, '_latest_result', None)
        
        # Skeleton 4-view
        landmarks = None
        world_landmarks = None
        if result and result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            if result.hand_world_landmarks:
                world_landmarks = result.hand_world_landmarks[0]
        
        skeleton_img = self.skeleton_renderer.render_4view(landmarks, world_landmarks)
        
        # Combine video + skeleton
        video_resized = cv2.resize(frame, (533, 400))
        combined = np.hstack([video_resized, skeleton_img])
        cv2.imshow("Hand Mouse AI - Unified View", combined)
        
        # Clavier virtuel
        if self.keyboard_enabled:
            keyboard_canvas = self.virtual_keyboard.draw(np.zeros((480, 960, 3), dtype=np.uint8))
            cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_GUI_NORMAL)
            cv2.imshow("Virtual Keyboard", keyboard_canvas)
        else:
            try:
                cv2.destroyWindow("Virtual Keyboard")
            except:
                pass
    
    # --- Callbacks ---
    
    def _on_detection_result(self, result, output_image, timestamp_ms: int):
        """Callback MediaPipe"""
        if not self.state.is_processing:
            return
        
        with self._lock:
            self._latest_result = result
            
            if not result.hand_landmarks:
                return
            
            # Mise à jour état
            self.state.update_hands(
                result.hand_landmarks,
                result.hand_world_landmarks or [],
                result.handedness or []
            )
            
            # Classification geste
            primary_landmarks = result.hand_landmarks[0]
            h, w = 480, 640  # Approximation
            
            gesture = self.gesture_classifier.classify([
                (lm.x, lm.y) for lm in primary_landmarks
            ])
            self.state.update_gesture(gesture)
            
            # Détection mode
            index_tip = primary_landmarks[8]
            screen_x, screen_y = int(index_tip.x * 1920), int(index_tip.y * 1080)
            self._current_mode = self.mode_detector.detect((screen_x, screen_y))
            self._active_hand_pos = (int(index_tip.x * w), int(index_tip.y * h))
            
            # Actions
            self._current_action = self.dispatcher.dispatch(
                gesture, self._current_mode, (screen_x, screen_y)
            )
            
            # Souris
            if gesture in ["POINTING", "PALM"] and not self.state.state.mouse_frozen:
                filtered_x, filtered_y = self.filter.filter(screen_x, screen_y)
                self.mouse.move(int(filtered_x), int(filtered_y))
            
            # ASL
            if self.asl_enabled:
                self.asl_manager.process(primary_landmarks)
    
    def _on_gesture_event(self, event_type, gesture):
        """Handler événement geste"""
        pass  # Extension future
    
    # --- Compatibilité ---
    
    def set_smoothing(self, value: float):
        """Compatibilité avec l'ancienne API"""
        self.mouse.set_smoothing(value)
