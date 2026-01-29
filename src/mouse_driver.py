import platform
import time
import math
import pyautogui
from optimized_utils import AdaptiveOneEuroFilter, AdaptiveSensitivityMapper

# Try to import uinput (Linux only)
try:
    import uinput
    UINPUT_AVAILABLE = True
except ImportError:
    UINPUT_AVAILABLE = False
except OSError:
    UINPUT_AVAILABLE = False # Permission denied case

class MouseDriver:
    def __init__(self, smoothing_enabled=True):
        self.os_name = platform.system()
        self.sw, self.sh = pyautogui.size()
        
        # --- OPTIMIZATION INTEGRATION ---
        self.filter = AdaptiveOneEuroFilter()
        self.mapper = AdaptiveSensitivityMapper(self.sw, self.sh, gamma=1.3)
        # self.calibration removed
        # -------------------------------
        
        self.mode = "pyautogui"
        self.frozen_until = 0  # Stability: Freeze cursor during clicks
        
        # Optimize PyAutoGUI for speed (Default is 0.1s pause!)
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False
        
        # Check for Linux & UInput support
        if self.os_name == "Linux" and UINPUT_AVAILABLE:
            try:
                events = (
                    uinput.BTN_LEFT,
                    uinput.BTN_RIGHT,
                    uinput.ABS_X + (0, self.sw, 0, 0),
                    uinput.ABS_Y + (0, self.sh, 0, 0),
                )
                self.device = uinput.Device(events, name="Hand Mouse Output")
                self.mode = "uinput"
                print("MouseDriver: Using UINPUT (Kernel Level) - Maximum Performance")
            except Exception as e:
                print(f"MouseDriver: UInput failed ({e}). Falling back to PyAutoGUI.")
                self.mode = "pyautogui"
        else:
             print("MouseDriver: Using PyAutoGUI")

    def move(self, x, y, frame_w, frame_h, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        # STABILITY: If frozen (clicking), do not move cursor
        if time.time() < self.frozen_until:
            return

        # 1. Normalize Coordinates [0, 1]
        norm_x = x / frame_w
        norm_y = y / frame_h
        
        # 2. Map directly to Screen Coordinates using Smart Mapper (Non-linear)
        # Calibration removed by user request - Back to standard mapping
        target_x, target_y = self.mapper.map(norm_x, norm_y)

        # 3. Apply Adaptive Filter (Smart Smoothing)
        screen_x, screen_y = self.filter(target_x, target_y, timestamp)
        
        # 4. Clamp & Integer Cast
        screen_x = int(max(0, min(self.sw - 1, screen_x)))
        screen_y = int(max(0, min(self.sh - 1, screen_y)))
        
        # 5. Apply Movement
        if self.mode == "uinput" and hasattr(self, 'device'):
            self.device.emit(uinput.ABS_X, screen_x, syn=False)
            self.device.emit(uinput.ABS_Y, screen_y)
        else:
            print(f"DEBUG: Move -> {screen_x}, {screen_y}")
            try:
                pyautogui.moveTo(screen_x, screen_y)
            except Exception as e:
                print(f"❌ PyAutoGUI Error: {e}")

    def click(self):
        # STABILITY: Freeze cursor for 200ms to allow clean click without jitter
        self.frozen_until = time.time() + 0.2
        
        if self.mode == "uinput" and hasattr(self, 'device'):
            self.device.emit(uinput.BTN_LEFT, 1)
            self.device.emit(uinput.BTN_LEFT, 0)
        else:
            pyautogui.click()
            
    def set_smoothing(self, value):
        # Value 1-20 from slider.
        # Map to filter strength if needed.
        # With adaptive filter, internal logic handles most cases.
        normalized = max(0.001, (21 - value) * 0.001) 
        self.filter.MEDIUM_CUTOFF = normalized
