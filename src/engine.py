import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import threading
import time
import math
import os
import socket
import json
import base64
import numpy as np  # PHASE 8: Required for keyboard canvas
from src.mouse_driver import MouseDriver
from src.optimized_utils import CameraConfigurator, PerformanceProfiler
from src.advanced_filter import HybridMouseFilter # NEW
from src.gesture_classifier import StaticGestureClassifier # Refactored
from src.context_mode import ContextModeDetector, ContextMode # NEW
from src.action_dispatcher import ActionDispatcher, ActionType # NEW
from src.feedback_overlay import FeedbackOverlay # NEW
from src.virtual_keyboard import VirtualKeyboard # PHASE 8
from src.asl_manager import ASLManager # REFACTOR: OOP

class HandEngine:
    def __init__(self, headless=False):
        self.headless = headless
        self.cap = None
        self.is_processing = False # Manual start required
        self.running = True # Thread life flag
        print("DEBUG: Engine initialized. Waiting for start command...")
        
        self.mouse = MouseDriver()
        self.filter = HybridMouseFilter() # NEW: Initialize Filter
        self.gesture_classifier = StaticGestureClassifier() # Refactored
        
        # --- NEW: Simplified Gesture System Components ---
        self.mode_detector = ContextModeDetector()
        self.action_dispatcher = ActionDispatcher()
        self.feedback_overlay = FeedbackOverlay(position="top_left")
        self.virtual_keyboard = VirtualKeyboard(layout="azerty", mode="dwell")  # PHASE 8
        self.asl_manager = ASLManager()
        
        # PHASE 8: Feature Flags (controlled by GUI)
        self.keyboard_enabled = False
        # self.asl_enabled is now a property below
        self.mouse_frozen = False  # NEW: Freeze mouse for typing
        
        # Gesture detection state for freeze toggle
        self._freeze_gesture_frames = 0
        self._freeze_gesture_threshold = 45  # ~1.5s at 30fps
        
        self.current_mode = ContextMode.CURSOR
        self.current_action = ActionType.NONE
        self.active_hand_pos = (0, 0) # For overlay halo
        
        # --- OPTIMIZATION: Profiler ---
        self.profiler = PerformanceProfiler()
        
        # --- HUD STREAMING: UDP ---
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.hud_addr = ("127.0.0.1", 5005)
        # -----------------------------
        # Async Result Storage
        self.lock = threading.Lock()
        self.latest_result = None
        self.latest_landmarks = None # NEW: For 3D HUD
        self.inference_start_times = {} # Map timestamp_ms -> wall_time
        self.current_gestures = [] # NEW PHASE 4

    @property
    def asl_enabled(self):
        return self.asl_manager.enabled
        
    @asl_enabled.setter
    def asl_enabled(self, value):
        self.asl_manager.set_enabled(value)
        
        # --- NEW API SETUP (GPU Default, Fallback in Loop) ---
        # ATTEMPT GPU
        
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
                # We only take the first hand for the principal 3D display for now
                self.latest_landmarks = result.hand_landmarks[0]
                # Capture World Landmarks for 3D visualization
                if result.hand_world_landmarks:
                     self.latest_world_landmarks = result.hand_world_landmarks[0]
                else:
                     self.latest_world_landmarks = None
                
                # --- STREAM TO TAURI HUD ---
                try:
                    data = {
                        "landmarks": [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in result.hand_landmarks[0]],
                        "ts": timestamp_ms / 1000.0
                    }
                    self.udp_socket.sendto(json.dumps(data).encode(), self.hud_addr)
                except:
                    pass
            else:
                self.latest_landmarks = None
            
        if result.hand_landmarks:
             # Calculate Latency
             start_time = self.inference_start_times.pop(timestamp_ms, None)
             if start_time:
                 latency = (time.time() - start_time) * 1000
                 self.profiler.metrics['inference'].append(latency)

             # Identify Primary Hand (Right Hand Preferred for Mouse)
             temp_gestures = []
             
             # Prepare data for simplified system
             primary_hand_landmarks = None
             secondary_hand_landmarks = None
             primary_gesture = "UNKNOWN"
             secondary_gesture = "UNKNOWN"
             primary_hand_idx = -1
             
             # First Pass: Classify all hands and identify Primary/Secondary
             for i, hand_landmarks in enumerate(result.hand_landmarks):
                 # Classify Gesture
                 gesture_label = self.gesture_classifier.classify(hand_landmarks)
                 temp_gestures.append(gesture_label)
                 
                 # Determine Handedness
                 is_right_hand = True # Default
                 if result.handedness and i < len(result.handedness):
                     # MediaPipe: "Left" = Right in mirror mode, but let's trust label for now
                     # Note: Usually "Right" label means Right Hand
                     label = result.handedness[i][0].category_name
                     is_right_hand = (label == "Right")
                 
                 # Assign Primary (Right) / Secondary (Left)
                 # ROBUSTNESS: Use Right as Primary if available, otherwise fallback later
                 if is_right_hand:
                     primary_hand_landmarks = hand_landmarks
                     primary_gesture = gesture_label
                     primary_hand_idx = i
                 else:
                     secondary_hand_landmarks = hand_landmarks
                     secondary_gesture = gesture_label

             # FALLBACK: If no Right Hand detected but hands exist, use the first hand as Primary
             if not primary_hand_landmarks and result.hand_landmarks:
                 primary_hand_landmarks = result.hand_landmarks[0]
                 primary_gesture = temp_gestures[0]
                 primary_hand_idx = 0
                 # If this hand was also assigned to secondary, clear secondary to avoid confusion
                 if secondary_hand_landmarks == primary_hand_landmarks:
                     secondary_hand_landmarks = None
                     secondary_gesture = "UNKNOWN"

             # --- SIMPLIFIED GESTURE SYSTEM LOGIC ---
             if primary_hand_landmarks:
                 # 1. Get Normalized Position (Tip of Index Finger usually, or Wrist)
                 # Using Index MCP (5) or Wrist (0) as robust anchor for mode detection
                 wrist = primary_hand_landmarks[0]
                 
                 # 2. Detect Context Mode
                 # We pass secondary hand info for Shortcut mode detection
                 secondary_wrist = secondary_hand_landmarks[0] if secondary_hand_landmarks else None
                 sec_pos = (secondary_wrist.x, secondary_wrist.y) if secondary_wrist else None
                 
                 new_mode = self.mode_detector.detect_mode(
                     hand_pos=(wrist.x, wrist.y),
                     left_hand_gesture=secondary_gesture,
                     left_hand_pos=sec_pos
                 )
                 self.current_mode = new_mode
                 
                 # 3. Determine Action
                 action = self.action_dispatcher.get_action(
                     mode=new_mode.value,
                     gesture=primary_gesture
                 )
                 self.current_action = action
                 
                 # DEBUG: Print status every 1 second (approx 30 frames)
                 # if int(timestamp_ms / 33) % 30 == 0:
                 #      print(f"DEBUG: Geste={primary_gesture} Mode={new_mode.value} Action={action}")

                 # --- PHASE 8: FREEZE TOGGLE VIA THUMBS GESTURES ---
                 if primary_gesture == "THUMBS_UP":
                     if self.mouse_frozen:
                         self.mouse_frozen = False
                         print(f"👍 Souris: DÉGELÉE ✅")
                 elif primary_gesture == "THUMBS_DOWN":
                     if not self.mouse_frozen:
                         self.mouse_frozen = True
                         print(f"👎 Souris: GELÉE ❄️")

                 # 4. Execute Action (Mouse Movement is special)
                 h, w = 480, 640 # Canvas size
                 
                 # --- MOUSE MOVEMENT (Skip if frozen) ---
                 if action == ActionType.MOVE_CURSOR and not self.mouse_frozen:
                     # Adaptive Tracking Point
                     # POINTING -> InteX Tip (8) for precision
                     # PALM -> Index MCP (5) for stability
                     track_idx = 8 if primary_gesture == "POINTING" else 5
                     
                     track_pt = primary_hand_landmarks[track_idx]
                     raw_x, raw_y = int(track_pt.x * w), int(track_pt.y * h)
                     
                     # Update active hand pos for halo
                     self.active_hand_pos = (raw_x, raw_y)
                     
                     # Apply Hybrid Filter
                     ts_seconds = timestamp_ms / 1000.0
                     smooth_x, smooth_y = self.filter.process(raw_x, raw_y, ts_seconds)
                     self.mouse.move(smooth_x, smooth_y, w, h, timestamp=ts_seconds)
                     
                 # --- OTHER ACTIONS ---
                 elif action == ActionType.CLICK_LEFT:
                     self.mouse.click()
                 elif action == ActionType.CLICK_RIGHT:
                     self.mouse.right_click()
                 elif action == ActionType.SCROLL_UP:
                     # Scroll based on vertical movement of index tip vs previous?
                     # For now static scroll
                     self.mouse.scroll(0, 1) # Scroll UP
                 # Add other actions mappings...
                 
                 # --- PHASE 8: KEYBOARD MODE ---
                 if self.keyboard_enabled:  # Changed: Only process if enabled
                      self.virtual_keyboard.process(primary_hand_landmarks, primary_gesture, img.shape)
                 
                 self.asl_manager.process(primary_hand_landmarks)
             else:
                 # No primary hand detected
                 pass
             
             with self.lock:
                 self.current_gestures = temp_gestures

    def start(self):
        print("▶️ STARTING ENGINE PROCESSING")
        self.is_processing = True

    def stop(self):
        print("⏹️ STOPPING ENGINE PROCESSING")
        self.is_processing = False

    def _get_distance(self, p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def _draw_skeleton_4view(self, result):
        """Draws a 4-view skeleton visualization in a native OpenCV window."""
        # numpy imported globally now
        
        # Canvas 600x400 (4 quadrants: 300x200 each)
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Draw Quadrant Lines
        cv2.line(img, (300, 0), (300, 400), (50, 50, 50), 2)
        cv2.line(img, (0, 200), (600, 200), (50, 50, 50), 2)
        
        # Labels
        cv2.putText(img, 'Main View', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        cv2.putText(img, 'Top View', (310, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        cv2.putText(img, 'Left View', (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        cv2.putText(img, 'Right View', (310, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        
        CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]
        
        def draw_hand(pts, offset_x, offset_y, scale, color):
            # Draw Bones
            for start, end in CONNECTIONS:
                if start < len(pts) and end < len(pts):
                    pt1 = (int(pts[start][0] * scale + offset_x), int(pts[start][1] * scale + offset_y))
                    pt2 = (int(pts[end][0] * scale + offset_x), int(pts[end][1] * scale + offset_y))
                    cv2.line(img, pt1, pt2, (180, 180, 180), 2)
            # Draw Joints
            for p in pts:
                px = int(p[0] * scale + offset_x)
                py = int(p[1] * scale + offset_y)
                cv2.circle(img, (px, py), 3, color, -1)
        
        if result and result.hand_landmarks:
            for i, hand_landmarks in enumerate(result.hand_landmarks):
                color = (0, 255, 255) if i == 0 else (255, 0, 255)  # Yellow / Purple
                
                # 1. Main View (Top-Left) - Screen Landmarks
                screen_pts = np.array([(lm.x * 300, lm.y * 200) for lm in hand_landmarks])
                draw_hand(screen_pts, 0, 0, 1.0, color)
                
                # 2. 3D Views - World Landmarks
                if result.hand_world_landmarks and i < len(result.hand_world_landmarks):
                    w_lms = result.hand_world_landmarks[i]
                    w_pts = np.array([(lm.x, lm.y, lm.z) for lm in w_lms])
                    scale_3d = 600  # Reduced for better fit in quadrants
                    
                    # Top View (XZ plane) -> Top-Right quadrant (center: 450, 100)
                    top_pts = np.column_stack((w_pts[:, 0], -w_pts[:, 2]))
                    draw_hand(top_pts, 450, 100, scale_3d, color)
                    
                    # Left View (ZY plane) -> Bottom-Left quadrant (center: 150, 300)
                    left_pts = np.column_stack((-w_pts[:, 2], w_pts[:, 1]))
                    draw_hand(left_pts, 150, 300, scale_3d, color)
                    
                    # Right View (ZY plane, inverted) -> Bottom-Right quadrant (center: 450, 300)
                    right_pts = np.column_stack((w_pts[:, 2], w_pts[:, 1]))
                    draw_hand(right_pts, 450, 300, scale_3d, color)
        else:
            cv2.putText(img, "WAITING...", (240, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return img

    def _run_loop(self):
        print(f"DEBUG: Thread _run_loop started. Running={self.running}")
        try:
            # Persistent thread loop
            self.landmarker = None
            window_name = "Hand Mouse AI"
            
            # Init options once
            print("DEBUG: Configuring MediaPipe Options...")
            base_options_gpu = python.BaseOptions(model_asset_path='assets/hand_landmarker.task', delegate=python.BaseOptions.Delegate.GPU)
            self.options = vision.HandLandmarkerOptions(
                base_options=base_options_gpu,
                running_mode=vision.RunningMode.LIVE_STREAM,
                num_hands=2,
                min_hand_detection_confidence=0.3,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                result_callback=self.result_callback)
            print("DEBUG: MediaPipe Options Configured.")

            while self.running:
                if not self.is_processing:
                    if self.cap is not None:
                        print("DEBUG: Pausing Engine (Releasing resources)...")
                        self.cap.release()
                        self.cap = None
                        if not self.headless:
                            cv2.destroyAllWindows()
                        if self.landmarker:
                             self.landmarker.close()
                             self.landmarker = None
                    time.sleep(0.5)
                    continue
            
                # ACTIVE STATE: Initialize if needed
                if self.cap is None:
                    print("DEBUG: Initializing Camera and Engine...")
                    # Auto-detect camera
                    self.cap = None
                    for cam_idx in range(5):
                        print(f"📷 Testing camera index {cam_idx}...")
                        temp_cap = cv2.VideoCapture(cam_idx)
                        if temp_cap.isOpened():
                            # Try reading a frame to be sure
                            ret, _ = temp_cap.read()
                            if ret:
                                self.cap = temp_cap
                                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                                print(f"✅ Found working camera at index {cam_idx}")
                                break
                            else:
                                temp_cap.release()
                    
                    if self.cap is None:
                        print("❌ NO WORKING CAMERA FOUND! Please check connections.")
                        # Sleep to avoid CPU spin if no camera
                        time.sleep(2)
                        continue

                    # Window creation moved to unified view display
                    if not self.headless:
                        # Create window with GUI_NORMAL to hide toolbar
                        cv2.namedWindow("Hand Mouse AI - Unified View", cv2.WINDOW_GUI_NORMAL)
                    
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
                    
                    if self.cap is None:
                        time.sleep(0.1)
                        continue

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
                    local_result = None
                    local_mode = ContextMode.CURSOR
                    local_action = ActionType.NONE
                    local_hand_halo_pos = None
                    local_gestures = []
                    
                    with self.lock:
                        if self.latest_result:
                             local_result = self.latest_result
                             local_gestures = self.current_gestures
                             local_mode = self.current_mode
                             local_action = self.current_action
                             local_hand_halo_pos = self.active_hand_pos
                    
                    # --- NEW FEEDBACK OVERLAY ---
                    # 1. Draw Zones (Background)
                    h, w = img.shape[:2]
                    img = self.feedback_overlay.draw_zone_indicators(img, local_mode.value)
                    
                    # 2. Draw Hand Halo
                    if local_hand_halo_pos and local_hand_halo_pos != (0, 0):
                        img = self.feedback_overlay.draw_hand_halo(img, local_hand_halo_pos, local_mode.value)
                        
                    # 3. Draw Skeleton & Debug Lines
                    if local_result and local_result.hand_landmarks:
                        # h, w already defined above
                        for i, hand_landmarks in enumerate(local_result.hand_landmarks):
                            # ... (Keep connection logic if needed, or rely on overlay)
                            # Simplified drawing for debug (dots + lines)
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
                                cv2.circle(img, (px, py), 2, (100, 100, 100), cv2.FILLED) 

                            for start_idx, end_idx in CONNECTIONS:
                                 if start_idx < len(lm_list) and end_idx < len(lm_list):
                                     cv2.line(img, lm_list[start_idx], lm_list[end_idx], (50, 50, 50), 1)

                    # 4. Draw Info Overlay (Foreground)
                    # Find primary gesture label equivalent for display
                    display_gesture = "UNKNOWN"
                    if local_gestures:
                        display_gesture = local_gestures[0] # Assuming Primary logic
                    
                    # Hack: Pass raw gesture to overlay for debug
                    self.feedback_overlay.debug_raw_gesture = display_gesture
                    
                    display_action = self.action_dispatcher.get_action_info(local_action)["emoji"] + " " + self.action_dispatcher.get_action_info(local_action)["name"]
                    
                    # Override Display Action if ASL is ON
                    overlay_mode = local_mode.value
                    if self.asl_enabled:
                        overlay_mode = "asl"
                        display_action = f"SIGNE: {self.asl_manager.get_display_text()}"
                        
                    img = self.feedback_overlay.draw(
                        frame=img,
                        mode=overlay_mode,
                        gesture=display_gesture,
                        action=display_action,
                        confidence=1.0 # Placeholder
                    )
                    
                    # FPS (Small debug)
                    fps = self.profiler.get_fps()
                    cv2.putText(img, f"{int(fps)} FPS", (w - 80, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    # --- PHASE 8: KEYBOARD RENDERING (Separate Window) ---
                    if self.keyboard_enabled:
                        # Create keyboard canvas (separate from main video)
                        keyboard_canvas = self.virtual_keyboard.draw(np.zeros((480, 960, 3), dtype=np.uint8))
                        # Create window without toolbar
                        cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_GUI_NORMAL)
                        cv2.imshow("Virtual Keyboard", keyboard_canvas)
                    else:
                        # Close keyboard window if it exists
                        try:
                            cv2.destroyWindow("Virtual Keyboard")
                        except:
                            pass

                    # 4. Show Unified Native Window (Video + Skeleton side by side)
                    if not self.headless:
                        # numpy imported globally now
                        # Resize video to match skeleton height (400px)
                        video_resized = cv2.resize(img, (533, 400))  # 4:3 aspect ratio -> 533x400
                        
                        # Generate skeleton view
                        skel_img = self._draw_skeleton_4view(local_result)
                        
                        # Combine horizontally: [Video 533x400] + [Skeleton 600x400] = 1133x400
                        combined = np.hstack([video_resized, skel_img])
                        cv2.imshow("Hand Mouse AI - Unified View", combined)
                    
                    self.profiler.mark('end')
                    self.profiler.measure('total', 'start', 'end')

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.stop()
                        
                except Exception as e:
                    import traceback
                    print("Error in Engine Loop (Recovering...):")
                    traceback.print_exc()
                    time.sleep(0.1)

        except Exception as e:
            import traceback
            print(f"❌ CRITICAL ERROR IN ENGINE THREAD: {e}")
            traceback.print_exc()

    def set_smoothing(self, value):
        self.mouse.set_smoothing(value)

