import numpy as np
import cv2
from src.one_euro_filter import OneEuroFilter

try:
    import hand_mouse_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

class HybridMouseFilter:
    def __init__(self, use_rust=True):
        self.use_rust = use_rust and RUST_AVAILABLE
        
        if self.use_rust:
            self.rust_filter = hand_mouse_core.RustHybridFilter()
            print("🚀 Using RUST Accelerated Filter")
        else:
            # 1. OneEuroFilter for jitter reduction in slow movements
            # min_cutoff: Lower = smoother but more latency. 1.0 is a good balance.
            # beta: Higher = less lag during fast movement.
            self.one_euro = OneEuroFilter(t0=0, x0=0, dx0=0, min_cutoff=1.0, beta=0.007)
            self.one_euro_y = OneEuroFilter(t0=0, x0=0, dx0=0, min_cutoff=1.0, beta=0.007)
            
            # 2. Kalman Filter for prediction/latency compensation
            self.kalman = self._init_kalman()
            
            # 3. State & Heuristics
            self.history = []
            self.max_history = 10
            self.last_pos = None
            self.dead_zone = 2.0 # Pixels
            self.last_timestamp = 0
        
    def _init_kalman(self):
        # State: [x, y, vx, vy]
        # Measurement: [x, y]
        kf = cv2.KalmanFilter(4, 2)
        kf.measurementMatrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)
        
        kf.transitionMatrix = np.array([
            [1, 0, 1, 0], # x = x + vx
            [0, 1, 0, 1], # y = y + vy
            [0, 0, 1, 0], # vx constant
            [0, 0, 0, 1]  # vy constant
        ], dtype=np.float32)
        
        # Process Noise Covariance (Q) - Trust in model
        kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
        
        # Measurement Noise Covariance (R) - Trust in measurement
        kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.1
        
        return kf
    
    def process(self, raw_x, raw_y, timestamp_sec):
        if self.use_rust:
            return self.rust_filter.process(float(raw_x), float(raw_y), float(timestamp_sec))

        # Initialize if first run
        if self.last_pos is None:
            self.last_pos = (raw_x, raw_y)
            self.kalman.statePre = np.array([[raw_x], [raw_y], [0], [0]], dtype=np.float32)
            self.kalman.statePost = np.array([[raw_x], [raw_y], [0], [0]], dtype=np.float32)
            self.one_euro(timestamp_sec, raw_x) # Init
            self.one_euro_y(timestamp_sec, raw_y) # Init
            return raw_x, raw_y

        dt = timestamp_sec - self.last_timestamp
        if dt <= 0:
            dt = 0.01 # Fallback
        self.last_timestamp = timestamp_sec

        # --- A. Kalman Step ---
        # 1. Predict
        prediction = self.kalman.predict()
        
        # 2. Correct (Update with measurement)
        measurement = np.array([[np.float32(raw_x)], [np.float32(raw_y)]])
        self.kalman.correct(measurement)
        
        # --- B. Velocity Calculation ---
        self.history.append((raw_x, raw_y, timestamp_sec))
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        velocity = self._compute_velocity()
        
        # --- C. Hybrid Logic ---
        # High velocity -> Trust Kalman (Prediction reduces latency)
        # Low velocity -> Trust OneEuro (Smoothing reduces jitter)
        
        if velocity > 500: # Fast movement (>500 px/sec)
            smooth_x = prediction[0][0]
            smooth_y = prediction[1][0]
        else:
            smooth_x = self.one_euro(timestamp_sec, raw_x)
            smooth_y = self.one_euro_y(timestamp_sec, raw_y)
            
        # --- D. Dead Zone (Anti-Drift) ---
        dist = self._distance(smooth_x, smooth_y, *self.last_pos)
        
        # Dynamic dead zone based on velocity
        current_dead_zone = self.dead_zone
        if velocity < 10: 
            current_dead_zone = 5.0 # Increase deadzone when still
        
        if dist < current_dead_zone:
            # If movement is tiny, stick to last position
            return self.last_pos
            
        self.last_pos = (smooth_x, smooth_y)
        return smooth_x, smooth_y
    
    def _compute_velocity(self):
        if len(self.history) < 2:
            return 0
        
        p1 = self.history[-1]
        p2 = self.history[-2]
        
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        dt = p1[2] - p2[2]
        
        if dt <= 0: return 0
        
        dist = np.sqrt(dx**2 + dy**2)
        return dist / dt # pixels/sec
    
    def _distance(self, x1, y1, x2, y2):
        return np.sqrt((x1-x2)**2 + (y1-y2)**2)
