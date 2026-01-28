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
        
        # --- NEW API SETUP ---
        base_options = python.BaseOptions(model_asset_path='assets/hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5)
        
        self.landmarker = vision.HandLandmarker.create_from_options(options)
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
        
        start_time = time.time()
        
        while self.running:
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
            
            # 3. Detect (Video Mode requires timestamp)
            timestamp_ms = int((time.time() - start_time) * 1000)
            detection_result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

            # 4. Process Results
            if detection_result.hand_landmarks:
                # We only asked for 1 hand
                hand_lms = detection_result.hand_landmarks[0]
                
                # Convert NormalizedLandmark (0.0-1.0) to Pixels
                lm_list = []
                for lm in hand_lms:
                    px, py = int(lm.x * w), int(lm.y * h)
                    lm_list.append([px, py])

                # Draw Hand (Simple Skeleton manually since solutions.drawing_utils is gone)
                # Wrist(0) -> Thumb(1-4) | Index(5-8) | Middle(9-12) | Ring(13-16) | Pinky(17-20)
                connections = [
                    (0,1),(1,2),(2,3),(3,4),
                    (0,5),(5,6),(6,7),(7,8),
                    (5,9),(9,10),(10,11),(11,12),
                    (9,13),(13,14),(14,15),(15,16),
                    (13,17),(17,18),(18,19),(19,20),
                    (0,17)
                ]
                for p1_idx, p2_idx in connections:
                     cv2.line(img, tuple(lm_list[p1_idx]), tuple(lm_list[p2_idx]), (200, 200, 200), 2)
                for pt in lm_list:
                    cv2.circle(img, (pt[0], pt[1]), 3, (255, 0, 0), cv2.FILLED)

                # Logic
                if len(lm_list) > 12:
                    x1, y1 = lm_list[8] # Index Tip
                    x2, y2 = lm_list[4] # Thumb Tip
                    
                    # Distance for Click
                    distance = self._get_distance(lm_list[8], lm_list[4])
                    
                    if distance < 40: # Click
                        cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                        self.mouse.click()
                    else: # Move
                        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                        self.mouse.move(x1, y1, w, h)

            # Show preview window (optional, can be disabled or embedded)
            cv2.imshow("Hand_mouseOS Vision", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                
            time.sleep(0.005)
        
        self.cap.release()
        cv2.destroyAllWindows()

    def set_smoothing(self, value):
        self.mouse.set_smoothing(value)
