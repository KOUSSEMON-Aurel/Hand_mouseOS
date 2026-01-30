import platform
import time
import math
import os
from src.optimized_utils import AdaptiveOneEuroFilter, AdaptiveSensitivityMapper

# Try to import evdev (Linux only) for uinput support
UINPUT_ERROR = None
try:
    import evdev
    from evdev import UInput, ecodes as E
    UINPUT_AVAILABLE = True
except Exception as err:
    UINPUT_AVAILABLE = False
    UINPUT_ERROR = str(err)

try:
    from pynput.mouse import Controller, Button
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

class MouseDriver:
    def __init__(self, smoothing_enabled=True):
        self.os_name = platform.system()
        self._pyautogui = None
        self.sw, self.sh = 1920, 1080 # Default
        
        # Try to get real screen size via pyautogui
        pg = self._get_pyautogui()
        if pg:
            try:
                self.sw, self.sh = pg.size()
            except Exception:
                print("MouseDriver: Failed to get screen size, using 1920x1080")

        # --- OPTIMIZATION INTEGRATION ---
        self.filter = AdaptiveOneEuroFilter()
        self.mapper = AdaptiveSensitivityMapper(self.sw, self.sh, gamma=1.3)
        # -------------------------------
        
        self.mode = "pyautogui"
        self.frozen_until = 0  # Stability: Freeze cursor during clicks
        
        # Check for Linux & UInput support
        if self.os_name == "Linux" and UINPUT_AVAILABLE:
            try:
                # Configuration du device virtuel avec evdev
                cap = {
                    E.EV_KEY: [E.BTN_LEFT, E.BTN_RIGHT],
                    E.EV_ABS: [
                        (E.ABS_X, evdev.AbsInfo(value=0, min=0, max=self.sw, fuzz=0, flat=0, resolution=0)),
                        (E.ABS_Y, evdev.AbsInfo(value=0, min=0, max=self.sh, fuzz=0, flat=0, resolution=0)),
                    ],
                    E.EV_REL: [E.REL_WHEEL]
                }
                self.device = UInput(cap, name="Hand Mouse Output")
                self.mode = "uinput"
                print("MouseDriver: Using EVDEV-UINPUT (Kernel Level) - Maximum Performance")
            except Exception as err:
                print(f"MouseDriver: UInput failed ({err}). (/dev/uinput missing or perms?)")
                self.mode = "fallback"
        else:
            reason = UINPUT_ERROR if UINPUT_ERROR else "Module not loaded or OS not Linux"
            print(f"MouseDriver: UInput not available ({reason}).")
            self.mode = "fallback"

        if self.mode == "fallback":
            if PYNPUT_AVAILABLE:
                try:
                    self.pynput_mouse = Controller()
                    self.mode = "pynput"
                    print("MouseDriver: Using Pynput")
                except Exception as e:
                    print(f"MouseDriver: Pynput failed ({e}). Trying PyAutoGUI...")
                    self.mode = "pyautogui"
            else:
                self.mode = "pyautogui"

        if self.mode == "pyautogui":
            pg = self._get_pyautogui()
            if pg:
                try:
                    pg.PAUSE = 0
                    pg.FAILSAFE = False
                    print("MouseDriver: Using PyAutoGUI")
                except Exception as e:
                    print(f"MouseDriver: PyAutoGUI initialization failed ({e})")
                    self.mode = "none"
            else:
                self.mode = "none"
                print("💡 TIP: Verify X11 authorization or use 'uinput' with proper permissions.")

        # Session check for Wayland
        if os.environ.get('XDG_SESSION_TYPE') == 'wayland' and self.mode != "uinput":
            print("⚠️ WARNING: Wayland detected! PyAutoGUI/Pynput might move the cursor 'invisibly'.")
            print("💡 TIP: Use 'uinput' for better Wayland support (requires /dev/uinput permissions).")

    def _get_pyautogui(self):
        """Lazy loader for pyautogui to prevent global import crashes."""
        if self._pyautogui is None:
            try:
                import pyautogui
                self._pyautogui = pyautogui
            except Exception:
                return None
        return self._pyautogui

    def move(self, x, y, frame_w, frame_h, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        if time.time() < self.frozen_until:
            return

        # 1. Normalize Coordinates [0, 1]
        norm_x = x / frame_w
        norm_y = y / frame_h
        
        # 2. Map to Screen
        target_x, target_y = self.mapper.map(norm_x, norm_y)

        # 3. Apply Smoothing
        screen_x, screen_y = self.filter(target_x, target_y, timestamp)
        
        # 4. Clamp
        screen_x = int(max(0, min(self.sw - 1, screen_x)))
        screen_y = int(max(0, min(self.sh - 1, screen_y)))
        
        # 5. Apply Movement
        if self.mode == "uinput" and hasattr(self, 'device'):
            self.device.write(E.EV_ABS, E.ABS_X, screen_x)
            self.device.write(E.EV_ABS, E.ABS_Y, screen_y)
            self.device.syn()
        elif self.mode == "pynput" and hasattr(self, 'pynput_mouse'):
            self.pynput_mouse.position = (screen_x, screen_y)
        elif self.mode == "pyautogui":
            pg = self._get_pyautogui()
            if pg:
                try:
                    pg.moveTo(screen_x, screen_y)
                except Exception:
                    pass

    def click(self):
        self.frozen_until = time.time() + 0.2
        if self.mode == "uinput" and hasattr(self, 'device'):
            self.device.write(E.EV_KEY, E.BTN_LEFT, 1)
            self.device.syn()
            self.device.write(E.EV_KEY, E.BTN_LEFT, 0)
            self.device.syn()
        elif self.mode == "pynput" and hasattr(self, 'pynput_mouse'):
            self.pynput_mouse.click(Button.left)
        elif self.mode == "pyautogui":
            pg = self._get_pyautogui()
            if pg: pg.click()
            
    def right_click(self):
        self.frozen_until = time.time() + 0.2
        if self.mode == "uinput" and hasattr(self, 'device'):
            self.device.write(E.EV_KEY, E.BTN_RIGHT, 1)
            self.device.syn()
            self.device.write(E.EV_KEY, E.BTN_RIGHT, 0)
            self.device.syn()
        elif self.mode == "pynput" and hasattr(self, 'pynput_mouse'):
            self.pynput_mouse.click(Button.right)
        elif self.mode == "pyautogui":
            pg = self._get_pyautogui()
            if pg: pg.rightClick()
            
    def scroll(self, dx, dy):
        if self.mode == "uinput" and hasattr(self, 'device'):
            # evdev REL_WHEEL: +1 is UP, -1 is DOWN
            self.device.write(E.EV_REL, E.REL_WHEEL, int(dy * 5))
            self.device.syn()
        elif self.mode == "pyautogui":
            pg = self._get_pyautogui()
            if pg: pg.scroll(int(dy * 50))

    def set_smoothing(self, value):
        normalized = max(0.001, (21 - value) * 0.001) 
        self.filter.MEDIUM_CUTOFF = normalized
