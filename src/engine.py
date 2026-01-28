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
    def __init__(self, on_frame_callback=None):
        self.cap = None
        self.running = False
        self.on_frame_callback = on_frame_callback
        self.mouse = MouseDriver()
        
        # --- NEW API SETUP ---
        base_options = python.BaseOptions(model_asset_path='assets/hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5)
        
        self.options = options # Save options for later
        self.last_timestamp_ms = 0
        self.prev_fps_time = 0
        self.last_gui_update = 0
        # ---------------------

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
                
                # FPS Calculation
                curr_time = time.time()
                fps = 1 / (curr_time - self.prev_fps_time) if (curr_time - self.prev_fps_time) > 0 else 0
                self.prev_fps_time = curr_time
                cv2.putText(img, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # 3. Detect (Video Mode requires timestamp)
                timestamp_ms = int((time.time() - start_time) * 1000)
                if timestamp_ms <= self.last_timestamp_ms:
                    timestamp_ms = self.last_timestamp_ms + 1
                self.last_timestamp_ms = timestamp_ms
                
                detection_result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

                # 4. Process Results
                if detection_result.hand_landmarks:
                    if len(detection_result.hand_landmarks) > 0:
                         pass # print("DEBUG: Hand Found")
                    
                    for hand_landmarks in detection_result.hand_landmarks:
                        # Draw connections (Skeleton)
                        # MediaPipe Hand Connections indices
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
                            # Convert normalized to pixel coordinates
                            px, py = int(lm.x * w), int(lm.y * h)
                            lm_list.append((px, py))
                            
                            # Draw landmark points
                            cv2.circle(img, (px, py), 3, (0, 255, 255), cv2.FILLED) # Yellow points

                        # Draw lines
                        for start_idx, end_idx in CONNECTIONS:
                             if start_idx < len(lm_list) and end_idx < len(lm_list):
                                 cv2.line(img, lm_list[start_idx], lm_list[end_idx], (0, 255, 0), 2) # Green lines

                        # Logic for Mouse (using the first hand found)
                        if len(lm_list) > 12:
                            x1, y1 = lm_list[8] # Index Tip
                            x2, y2 = lm_list[4] # Thumb Tip
                            
                            # Distance for Click
                            distance = self._get_distance(lm_list[8], lm_list[4])
                            
                            # Pass timestamp (in seconds) to driver for OneEuroFilter
                            ts_seconds = timestamp_ms / 1000.0
                            
                            # Draw Interaction Info
                            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2) # Line between Thumb and Index
                            
                            # HUD Variables
                            gesture_name = "POINTER"
                            color = (0, 255, 0) # Green
                            
                            if distance < 40: # Click
                                gesture_name = "PINCH"
                                color = (0, 0, 255) # Red
                                cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED) # Red Click Indicator
                                self.mouse.click()
                            else: # Move
                                self.mouse.move(x1, y1, w, h, timestamp=ts_seconds)

                            # Draw HUD (Like in the Svelte app)
                            # Transparent Box
                            overlay = img.copy()
                            cv2.rectangle(overlay, (20, 60), (250, 160), (0, 0, 0), cv2.FILLED)
                            alpha = 0.4
                            img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
                            
                            # Text
                            cv2.putText(img, f"MODE: {gesture_name}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                            
                            # Confidence (Simulated or from Handedness)
                            # Using detection score if available
                            score = 0.95 # Default high confidence if tracking works
                            if detection_result.handedness:
                                 score = detection_result.handedness[0][0].score
                            
                            cv2.putText(img, f"Conf: {int(score*100)}%", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                            
                            # Bar
                            cv2.rectangle(img, (30, 150), (30 + int(200 * score), 155), color, cv2.FILLED)

                # 5. Send Frame to GUI (if callback exists)
                # Throttle GUI updates to ~30 FPS (0.033s) for smoothness vs performance
                current_time = time.time()
                if self.on_frame_callback and (current_time - self.last_gui_update) > 0.033:
                    self.last_gui_update = current_time
                    
                    # OPTIMIZATION: Resize for faster Base64 transfer
                    # Preview doesn't need to be full tracking resolution
                    preview_img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
                    
                    # Encode via JPEG with lower quality (50-70) for speed
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                    success_enc, buffer = cv2.imencode('.jpg', preview_img, encode_param)
                    
                    if success_enc:
                        import base64
                        b64_str = base64.b64encode(buffer).decode('utf-8')
                        self.on_frame_callback(b64_str)
                    
                time.sleep(0.001) # Yield execution to keep GUI responsive
            except Exception as e:
                import traceback
                print("Error in Engine Loop (Recovering...):")
                traceback.print_exc()
                time.sleep(0.1) # Brief pause to avoid log spam if error persists
        
        # Cleanup after loop (if running becomes False)
        if self.landmarker:
            self.landmarker.close()
        self.cap.release()
        cv2.destroyAllWindows()

    def set_smoothing(self, value):
        self.mouse.set_smoothing(value)
