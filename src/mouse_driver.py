import pyautogui
import numpy as np
import time

class MouseDriver:
    def __init__(self, smoothing_factor=5, sensitivity=1.0):
        """
        Initialize the Mouse Driver.
        :param smoothing_factor: Higher value = smoother but more lag (1-10 recommended).
        :param sensitivity: Multiplier for mouse movement speed.
        """
        pyautogui.FAILSAFE = False
        self.screen_w, self.screen_h = pyautogui.size()
        self.smoothing = smoothing_factor
        self.sensitivity = sensitivity
        
        # State for smoothing
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        
        # Click state to avoid spamming clicks
        self.last_click_time = 0
        self.click_cooldown = 0.5 # Seconds

    def move(self, x_rel, y_rel, frame_w, frame_h):
        """
        Move the mouse based on relative coordinates from the camera frame.
        x_rel, y_rel: Coordinates in the camera frame (0 to frame_w/h).
        """
        # 1. Normalize coordinates (0.0 to 1.0)
        x_norm = np.interp(x_rel, (0, frame_w), (0, 1))
        y_norm = np.interp(y_rel, (0, frame_h), (0, 1))

        # 2. Map to Screen Coordinates
        # Use a localized box for better reach (optional, here we map full screen)
        # To make it usable, we often map a smaller center box of the cam to full screen
        cam_margin = 100 # Pixels from edge of camera frame to ignore
        
        x_screen = np.interp(x_rel, (cam_margin, frame_w - cam_margin), (0, self.screen_w))
        y_screen = np.interp(y_rel, (cam_margin, frame_h - cam_margin), (0, self.screen_h))

        # 3. Smoothing (Exponential Moving Average)
        self.curr_x = self.prev_x + (x_screen - self.prev_x) / self.smoothing
        self.curr_y = self.prev_y + (y_screen - self.prev_y) / self.smoothing

        # 4. Apply Sensitivity (Simple clamp or multiplier if delta based, but here we use absolute mapping)
        # For absolute mapping, sensitivity is usually adjusting the mapped area size.
        # We'll stick to the mapped area approach above.

        # 5. Move Mouse
        # Clamp to screen size
        final_x = max(0, min(self.screen_w, self.curr_x))
        final_y = max(0, min(self.screen_h, self.curr_y))
        
        pyautogui.moveTo(final_x, final_y)
        
        self.prev_x, self.prev_y = self.curr_x, self.curr_y

    def click(self):
        """Perform a left click with cooldown."""
        if time.time() - self.last_click_time > self.click_cooldown:
            pyautogui.click()
            self.last_click_time = time.time()
            return True
        return False
        
    def set_smoothing(self, factor):
        self.smoothing = max(1, factor)

