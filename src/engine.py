import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import threading
import time
import math
import os
from mouse_driver import MouseDriver
from optimized_utils import CameraConfigurator, PerformanceProfiler
from advanced_filter import HybridMouseFilter # NEW
from gesture_classifier import StaticGestureClassifier # NEW PHASE 4

class HandEngine:
    def __init__(self):
        self.cap = None
        self.is_processing = False # Control flag
        self.is_processing = False # Control flag
        self.running = True # Thread life flag
        self.mouse = MouseDriver()
        self.filter = HybridMouseFilter() # NEW: Initialize Filter
        self.gesture_classifier = StaticGestureClassifier() # NEW PHASE 4
        
        # --- OPTIMIZATION: Profiler ---
        self.profiler = PerformanceProfiler()
        # -----------------------------
        # Async Result Storage
        self.lock = threading.Lock()
        self.latest_result = None
        self.inference_start_times = {} # Map timestamp_ms -> wall_time
        self.current_gestures = [] # NEW PHASE 4
        
        # --- NEW API SETUP (GPU Default, Fallback in Loop) ---
        # ATTEMPT GPU
        base_options_gpu = python.BaseOptions(model_asset_path='assets/hand_landmarker.task', delegate=python.BaseOptions.Delegate.GPU)
        
        print("🚀 INITIALIZING AI ENGINE (Attempting GPU)...")
        self.options = vision.HandLandmarkerOptions(
            base_options=base_options_gpu,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=2, # DUAL HAND SUPPORT
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            result_callback=self.result_callback)
        self.using_gpu = False # Will be updated in loop
        
        self.prev_fps_time = 0
        
        # Start persistent thread
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def result_callback(self, result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        # Only process if we are actually "processing" (avoid backlog callbacks)
        if not self.is_processing:
            return

        with self.lock:
            self.latest_result = result
            
        if result.hand_landmarks:
             # Calculate Latency
             start_time = self.inference_start_times.pop(timestamp_ms, None)
             if start_time:
                 latency = (time.time() - start_time) * 1000
                 self.profiler.metrics['inference'].append(latency)

             # Identify Primary Hand (Right Hand Preferred for Mouse)
             temp_gestures = []

             # Loop through all detected hands
             for i, hand_landmarks in enumerate(result.hand_landmarks):
                 # 1. Classify Gesture
                 gesture_label = self.gesture_classifier.classify(hand_landmarks)
                 temp_gestures.append(gesture_label)

                 # 2. Get Handedness Label (if available)
                 hand_label = "Unknown"
                 if result.handedness and i < len(result.handedness):
                     hand_label = result.handedness[i][0].category_name
                 
                 is_primary = (i == 0) 
                 
                 h, w = 480, 640
                 lm_list = []
                 for lm in hand_landmarks:
                     px, py = int(lm.x * w), int(lm.y * h)
                     lm_list.append((px, py))
                 
                 if len(lm_list) > 12:
                     distance = self._get_distance(lm_list[8], lm_list[4])
                     ts_seconds = timestamp_ms / 1000.0
                     
                     if is_primary:
                         # --- MOUSE CONTROL (Primary Only) ---
                         # Use Gesture for better click detection? (Future)
                         # For now keep distance based for compatibility
                         if distance < 40: # Click
                             self.mouse.click()
                         else: # Move
                             # APPLY HYBRID FILTER
                             raw_x, raw_y = lm_list[8]
                             smooth_x, smooth_y = self.filter.process(raw_x, raw_y, ts_seconds)
                             self.mouse.move(smooth_x, smooth_y, w, h, timestamp=ts_seconds)
                     else:
                         # SECONDARY HAND: Sign language preparation
                         pass
             
             with self.lock:
                 self.current_gestures = temp_gestures


    def start(self):
        self.is_processing = True

    def stop(self):
        self.is_processing = False

    def _get_distance(self, p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def _run_loop(self):
        # Persistent thread loop
        self.landmarker = None
        window_name = "Hand Mouse AI"
        
        # --- OPTIMIZATION: Configure Camera Hardware ---
        print("DEBUG: Configuring Camera Hardware...")
        CameraConfigurator.configure_camera() # Forces Exposure/Focus settings
        # -----------------------------------------------
        
        while self.running:
            if not self.is_processing:
                # IDLE STATE: Release resources if they are open
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                    cv2.destroyAllWindows()
                    if self.landmarker:
                         self.landmarker.close()
                         self.landmarker = None
                time.sleep(0.1)
                continue
            
            # ACTIVE STATE: Initialize if needed
            if self.cap is None:
                print("DEBUG: Initializing Camera and Engine...")
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, 640, 480)
                
                # Try GPU first, fallback to CPU
                try:
                    print("⚡ ATTEMPTING GPU INITIALIZATION...")
                    self.landmarker = vision.HandLandmarker.create_from_options(self.options)
                    self.using_gpu = True
                    print("✅ GPU INITIALIZED SUCCESSFULLY")
                except Exception as e:
                    print(f"⚠️ GPU FAILED ({e}), FALLING BACK TO CPU...")
                    # Fallback to CPU options
                    base_options_cpu = python.BaseOptions(model_asset_path='assets/hand_landmarker.task', delegate=python.BaseOptions.Delegate.CPU)
                    fallback_options = vision.HandLandmarkerOptions(
                        base_options=base_options_cpu,
                        running_mode=vision.RunningMode.LIVE_STREAM,
                        num_hands=2, # DUAL HAND SUPPORT
                        min_hand_detection_confidence=0.5,
                        min_hand_presence_confidence=0.5,
                        min_tracking_confidence=0.5,
                        result_callback=self.result_callback)
                    self.landmarker = vision.HandLandmarker.create_from_options(fallback_options)
                    self.using_gpu = False
                    print("✅ CPU FALLBACK ACTIVE")

                self.start_time = time.time()
                self.last_timestamp_ms = 0
                


            # Processing Loop Step
            try:
                self.profiler.mark('start')
                
                success, img = self.cap.read()
                if not success:
                    time.sleep(0.1)
                    continue

                self.profiler.mark('capture')

                # 1. Flip & Convert
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
                
                # 2. Detect Async
                timestamp_ms = int((time.time() - self.start_time) * 1000)
                if timestamp_ms <= self.last_timestamp_ms:
                    timestamp_ms = self.last_timestamp_ms + 1
                self.last_timestamp_ms = timestamp_ms
                
                if self.landmarker:
                    # TRACKING: Store wall time for this timestamp
                    self.inference_start_times[timestamp_ms] = time.time()
                    
                    # Cleanup old timestamps (prevent memory leak)
                    if len(self.inference_start_times) > 100:
                        # Remove keys older than 1 second (approx)
                        cutoff = timestamp_ms - 2000 
                        keys_to_remove = [k for k in self.inference_start_times.keys() if k < cutoff]
                        for k in keys_to_remove:
                            del self.inference_start_times[k]
                            
                    self.landmarker.detect_async(mp_image, timestamp_ms)
                
                self.profiler.mark('inference_sent')

                # 3. Draw LATEST known result
                # FPS Calculation from Profiler
                fps = self.profiler.get_fps()
                cv2.putText(img, f"OPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # STATUS HUD
                status_color = (0, 255, 0) if self.using_gpu else (0, 165, 255) # Green for GPU, Orange for CPU
                status_text = "GPU: ON" if self.using_gpu else "GPU: OFF (CPU)"
                cv2.putText(img, status_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

                local_result = None
                local_gestures = []
                with self.lock:
                    if self.latest_result:
                         local_result = self.latest_result
                         local_gestures = self.current_gestures
                
                if local_result and local_result.hand_landmarks:
                    h, w, c = img.shape
                    for i, hand_landmarks in enumerate(local_result.hand_landmarks):
                        # Hand Connections (Simplified)
                        CONNECTIONS = frozenset([
                            (0, 1), (1, 2), (2, 3), (3, 4),
                            (0, 5), (5, 6), (6, 7), (7, 8),
                            (5, 9), (9, 10), (10, 11), (11, 12),
                            (9, 13), (13, 14), (14, 15), (15, 16),
                            (13, 17), (17, 18), (18, 19), (19, 20),
                            (0, 17)
                        ])
                        
                        lm_list = []
                        for lm in hand_landmarks:
                            px, py = int(lm.x * w), int(lm.y * h)
                            lm_list.append((px, py))
                            cv2.circle(img, (px, py), 3, (0, 255, 255), cv2.FILLED) 

                        for start_idx, end_idx in CONNECTIONS:
                             if start_idx < len(lm_list) and end_idx < len(lm_list):
                                 cv2.line(img, lm_list[start_idx], lm_list[end_idx], (0, 255, 0), 2)

                        # HUD for this Hand
                        gesture = local_gestures[i] if i < len(local_gestures) else "TRACKING"
                        hand_label = "M" if i == 0 else "S" # Master / Secondary
                        color = (0, 255, 0) if i == 0 else (255, 0, 255) # Primary Green, Secondary Purple
                        
                        root_x, root_y = lm_list[0]
                        cv2.putText(img, f"[{hand_label}] {gesture}", (root_x - 20, root_y + 30), 
                                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # 4. Show Native Window
                cv2.imshow(window_name, img)
                
                self.profiler.mark('end')
                self.profiler.measure('total', 'start', 'end')
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    
            except Exception as e:
                import traceback
                print("Error in Engine Loop (Recovering...):")
                traceback.print_exc()
                time.sleep(0.1)

    def set_smoothing(self, value):
        self.mouse.set_smoothing(value)
    def set_smoothing(self, value):
        self.mouse.set_smoothing(value)
