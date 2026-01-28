import time
try:
    import uinput
    UINPUT_AVAILABLE = True
except ImportError:
    UINPUT_AVAILABLE = False
    print("Warning: python-uinput not found. Falling back to PyAutoGUI (slower).")

import pyautogui
from one_euro_filter import OneEuroFilter

class MouseDriver:
    def __init__(self, screen_w=1920, screen_h=1080):
        self.sw, self.sh = pyautogui.size()
        print(f"DEBUG: Screen size detected: {self.sw}x{self.sh}")
        self.mode = "pyautogui"
        self.device = None
        
        # --- One Euro Filter Setup ---
        # Tuned parameters for hand tracking
        # min_cutoff: 0.05 (very smooth at low speed) to 1.0 (very responsive)
        # beta: speed coefficient (0 = no adaptive, 0.001+ = adaptive)
        # Fix: Init t0 to 0 (or close to 0) because engine sends relative timestamp (since start)
        # using time.time() here while engine used (time.time() - start) caused massive negative delta
        self.filter_x = OneEuroFilter(t0=0, x0=0, min_cutoff=0.1, beta=0.005)
        self.filter_y = OneEuroFilter(t0=0, x0=0, min_cutoff=0.1, beta=0.005)
        
        # --- UInput Setup ---
        if UINPUT_AVAILABLE:
            try:
                events = (
                    uinput.BTN_LEFT,
                    uinput.BTN_RIGHT,
                    uinput.ABS_X + (0, self.sw, 0, 0),
                    uinput.ABS_Y + (0, self.sh, 0, 0),
                )
                self.device = uinput.Device(events)
                self.mode = "uinput"
                print("MouseDriver: Using UINPUT (Kernel Level) - Maximum Performance")
            except Exception as e:
                print(f"MouseDriver: UInput failed ({e}). Falling back to PyAutoGUI.")
                self.mode = "pyautogui"
        
        if self.mode == "pyautogui":
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0 # Turbo Mode
            print("MouseDriver: Using PyAutoGUI")

        self.last_click_time = 0

    def set_smoothing(self, value):
        # Value 1-20 from slider.
        # We assume value 1 = very responsive (min_cutoff high), value 20 = very smooth (min_cutoff low)
        # Mapping: 1 -> 1.0 Hz, 20 -> 0.01 Hz
        
        # mc = 1.0 / value (approx)
        mc = 1.0 / max(1, value * 0.5) 
        self.filter_x.min_cutoff = mc
        self.filter_y.min_cutoff = mc

    def move(self, x, y, frame_w, frame_h, timestamp=None):
        """
        x, y: Coordinates in the camera frame (pixels)
        frame_w, frame_h: Dimensions of the camera frame
        timestamp: Time in seconds (float) associated with the frame
        """
        if timestamp is None:
            timestamp = time.time()

        # 1. Filter raw input
        # Use try/except just in case init failed subtly, though __init__ should cover it
        x_filtered = self.filter_x(timestamp, x)
        y_filtered = self.filter_y(timestamp, y)

        # 2. Map to Screen
        screen_x = int( (x_filtered / frame_w) * self.sw )
        screen_y = int( (y_filtered / frame_h) * self.sh )
        
        # Clamp
        screen_x = max(0, min(self.sw - 1, screen_x))
        screen_y = max(0, min(self.sh - 1, screen_y))
        
        # 3. Apply
        # print(f"DEBUG: Move to {screen_x}, {screen_y} (Mode: {self.mode})") 
        if self.mode == "uinput" and self.device:
            self.device.emit(uinput.ABS_X, screen_x, syn=False)
            self.device.emit(uinput.ABS_Y, screen_y)
        else:
            pyautogui.moveTo(screen_x, screen_y)

    def click(self):
        now = time.time()
        if now - self.last_click_time > 0.3: # Debounce
            if self.mode == "uinput" and self.device:
                self.device.emit(uinput.BTN_LEFT, 1)
                self.device.emit(uinput.BTN_LEFT, 0)
            else:
                pyautogui.click()
            self.last_click_time = now
