import platform
import time
import math
import pyautogui
from src.optimized_utils import AdaptiveOneEuroFilter, AdaptiveSensitivityMapper

# Try to import uinput (Linux only)
try:
    import uinput
    UINPUT_AVAILABLE = True
except ImportError:
    UINPUT_AVAILABLE = False
except OSError:
    UINPUT_AVAILABLE = False # Permission denied case

try:
    from pynput.mouse import Controller, Button
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

import os

class MouseDriver:
    def __init__(self, smoothing_enabled=True):
        self.os_name = platform.system()
        self.sw, self.sh = pyautogui.size()
        
        # --- OPTIMIZATION INTEGRATION ---
        self.filter = AdaptiveOneEuroFilter()
        self.mapper = AdaptiveSensitivityMapper(self.sw, self.sh, gamma=1.3)
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
                    uinput.REL_WHEEL, # Scrolling support
                )
                self.device = uinput.Device(events, name="Hand Mouse Output")
                self.mode = "uinput"
                print("MouseDriver: Using UINPUT (Kernel Level) - Maximum Performance")
            except Exception as e:
                print(f"MouseDriver: UInput failed ({e}). Falling back to other methods.")
                self.mode = "fallback"
        else:
            self.mode = "fallback"

        if self.mode == "fallback":
            if PYNPUT_AVAILABLE:
                try:
                    self.pynput_mouse = Controller()
                    self.mode = "pynput"
                    print("MouseDriver: Using Pynput")
                except Exception as e:
                    print(f"MouseDriver: Pynput failed ({e}). Using PyAutoGUI.")
                    self.mode = "pyautogui"
            else:
                self.mode = "pyautogui"
                print("MouseDriver: Using PyAutoGUI")

        # Session check for Wayland
        if os.environ.get('XDG_SESSION_TYPE') == 'wayland' and self.mode != "uinput":
            print("⚠️ WARNING: Wayland detected! PyAutoGUI/Pynput might move the cursor 'invisibly'.")
            print("💡 TIP: Use 'uinput' for better Wayland support (requires /dev/uinput permissions).")

    def move(self, x, y, frame_w, frame_h, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        # STABILITY: If frozen (clicking), do not move cursor
        if time.time() < self.frozen_until:
            return

        if self.os_name == "Linux" and UINPUT_AVAILABLE:
            # UInput works with absolute coordinates [0, SW]
            # No normalization needed if we map incorrectly earlier.
            pass

        # 1. Normalize Coordinates [0, 1]
        norm_x = x / frame_w
        norm_y = y / frame_h
        
        # 2. Map to Screen with Smart/Adaptive Scaling
        # We assume the user wants the camera FoV to cover the screen
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
        elif self.mode == "pynput" and hasattr(self, 'pynput_mouse'):
            self.pynput_mouse.move(screen_x - self.pynput_mouse.position[0], screen_y - self.pynput_mouse.position[1])
        else:
            # print(f"DEBUG: Move -> {screen_x}, {screen_y}")
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
        elif self.mode == "pynput" and hasattr(self, 'pynput_mouse'):
            self.pynput_mouse.click(Button.left)
        else:
            pyautogui.click()
            
    def right_click(self):
        # STABILITY: Freeze for right click too
        self.frozen_until = time.time() + 0.2
        
        if self.mode == "uinput" and hasattr(self, 'device'):
            self.device.emit(uinput.BTN_RIGHT, 1)
            self.device.emit(uinput.BTN_RIGHT, 0)
        elif self.mode == "pynput" and hasattr(self, 'pynput_mouse'):
            self.pynput_mouse.click(Button.right)
        else:
            pyautogui.rightClick()
            
    def scroll(self, dx, dy):
        """
        Scrolling action.
        dx: Horizontal scroll (not supported by REL_WHEEL standard usually, ignored for now)
        dy: Vertical scroll (+1 UP, -1 DOWN)
        """
        if self.mode == "uinput" and hasattr(self, 'device'):
            # uinput REL_WHEEL: +1 is UP, -1 is DOWN
            self.device.emit(uinput.REL_WHEEL, int(dy * 5)) # Multiplier for speed
        else:
            # PyAutoGUI scroll: amount of clicks
            pyautogui.scroll(int(dy * 50))

    def set_smoothing(self, value):
        # Value 1-20 from slider.
        # Map to filter strength if needed.
        # With adaptive filter, internal logic handles most cases.
        normalized = max(0.001, (21 - value) * 0.001) 
        self.filter.MEDIUM_CUTOFF = normalized


