import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import threading
import time
import math
import os
from mouse_driver import MouseDriver

class HandEngine:
    def __init__(self):
        self.cap = None
        self.running = False
        self.mouse = MouseDriver()
        
        # Async Result Storage
        self.lock = threading.Lock()
        self.latest_result = None
        
        # --- NEW API SETUP ---
        base_options = python.BaseOptions(model_asset_path='assets/hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=1,
            # INCREASED PRECISION: 0.5 -> 0.7 to avoid jitter from bad detections
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            result_callback=self.result_callback)
        
        self.options = options # Save options for later
        self.last_timestamp_ms = 0
        self.prev_fps_time = 0
        # ---------------------

    def result_callback(self, result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        with self.lock:
            self.latest_result = result
            
        # Trigger Mouse Control ASAP (in the callback thread)
        # We need to process this here to ensure low latency for input
        # NOTE: Be careful not to block this callback too long
        if result.hand_landmarks:
             # Basic logic extraction to avoid complex drawing code here
             # We just want to move the mouse
             for hand_landmarks in result.hand_landmarks:
                h, w = 480, 640 # Working resolution
                lm_list = []
                for lm in hand_landmarks:
                    px, py = int(lm.x * w), int(lm.y * h)
                    lm_list.append((px, py))
                
                if len(lm_list) > 12:
                    distance = self._get_distance(lm_list[8], lm_list[4])
                    ts_seconds = timestamp_ms / 1000.0
                    
                    # Logic
                    if distance < 40: # Click
                        self.mouse.click()
                    else: # Move
                         # We use normalized coords from raw Landmarks for precision if preferred,
                         # but here we follow existing logic with px
                         self.mouse.move(lm_list[8][0], lm_list[8][1], w, h, timestamp=ts_seconds)


    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def _get_distance(self, p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def _run_loop(self):
        self.cap = cv2.VideoCapture(0)
        # OPTIMIZATION: Limit resolution to 640x480 to reduce CPU usage and lag
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Create Landmarker for this session
        self.landmarker = vision.HandLandmarker.create_from_options(self.options)
        self.last_timestamp_ms = 0
        
        start_time = time.time()
        
        window_name = "Hand Mouse AI"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        
        # Check Session Type logic for Window Behavior
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        print(f"DEBUG: Session Type detected: {session_type}")
        
        if 'wayland' in session_type:
            try:
                # Try to force TOPMOST on Wayland (implementation dependent)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                print("DEBUG: Attempting Floating Window Mode (Wayland)")
            except:
                pass
        else:
             print("DEBUG: Standard Window Mode (X11)")
        
        while self.running:
            try:
                success, img = self.cap.read()
                if not success:
                    time.sleep(0.1)
                    continue

                # 1. Flip & Convert
                img = cv2.flip(img, 1)
                h, w, c = img.shape
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # 2. Create MP Image
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
                
                # 3. Detect Async (Non-Blocking)
                timestamp_ms = int((time.time() - start_time) * 1000)
                if timestamp_ms <= self.last_timestamp_ms:
                    timestamp_ms = self.last_timestamp_ms + 1
                self.last_timestamp_ms = timestamp_ms
                
                self.landmarker.detect_async(mp_image, timestamp_ms)

                # 4. Draw LATEST known result (Decoupled rendering)
                # FPS Calculation
                curr_time = time.time()
                fps = 1 / (curr_time - self.prev_fps_time) if (curr_time - self.prev_fps_time) > 0 else 0
                self.prev_fps_time = curr_time
                cv2.putText(img, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                local_result = None
                with self.lock:
                    if self.latest_result:
                         local_result = self.latest_result
                
                if local_result and local_result.hand_landmarks:
                    for hand_landmarks in local_result.hand_landmarks:
                        # Draw connections (Skeleton)
                        CONNECTIONS = frozenset([
                            (0, 1), (1, 2), (2, 3), (3, 4),
                            (0, 5), (5, 6), (6, 7), (7, 8),
                            (5, 9), (9, 10), (10, 11), (11, 12),
                            (9, 13), (13, 14), (14, 15), (15, 16),
                            (13, 17), (17, 18), (18, 19), (19, 20),
                            (0, 17)
                        ])
                        
                        lm_list = []
                        for i, lm in enumerate(hand_landmarks):
                            px, py = int(lm.x * w), int(lm.y * h)
                            lm_list.append((px, py))
                            cv2.circle(img, (px, py), 3, (0, 255, 255), cv2.FILLED) 

                        for start_idx, end_idx in CONNECTIONS:
                             if start_idx < len(lm_list) and end_idx < len(lm_list):
                                 cv2.line(img, lm_list[start_idx], lm_list[end_idx], (0, 255, 0), 2)

                        # HUD Logic (Visualization only, Logic is in Callback)
                        if len(lm_list) > 12:
                            x1, y1 = lm_list[8]
                            x2, y2 = lm_list[4]
                            distance = self._get_distance(lm_list[8], lm_list[4])
                            
                            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                            
                            gesture_name = "POINTER"
                            color = (0, 255, 0)
                            if distance < 40:
                                gesture_name = "PINCH"
                                color = (0, 0, 255)
                                cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
                            
                            # HUD
                            overlay = img.copy()
                            cv2.rectangle(overlay, (20, 60), (250, 160), (0, 0, 0), cv2.FILLED)
                            alpha = 0.4
                            img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
                            cv2.putText(img, f"MODE: {gesture_name}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                            
                            score = 0.95
                            if local_result.handedness:
                                 score = local_result.handedness[0][0].score
                            cv2.putText(img, f"Conf: {int(score*100)}%", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                            cv2.rectangle(img, (30, 150), (30 + int(200 * score), 155), color, cv2.FILLED)

                # 5. Show Native Window
                cv2.imshow("Hand Mouse AI", img)
                
                # Check for window close or key press (1ms wait)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    
            except Exception as e:
                import traceback
                print("Error in Engine Loop (Recovering...):")
                traceback.print_exc()
                time.sleep(0.1) 
        
        # Cleanup after loop
        if self.landmarker:
            self.landmarker.close()
        self.cap.release()
        cv2.destroyAllWindows()

    def set_smoothing(self, value):
        self.mouse.set_smoothing(value)
