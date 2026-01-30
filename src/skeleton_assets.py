import cv2
import numpy as np
import base64
import math

class SkeletonAssets:
    """Generates static skeletal hand images for UI icons."""
    
    @staticmethod
    def get_landmark_pose(gesture_name):
        """Returns normalized (0-1) [x, y] coordinates for ideal gesture poses."""
        points = [(0.5, 0.9)] * 21 # Default Wrist at bottom center
        
        # Helper to set finger state
        def set_finger(start_idx, base_x, base_y, length, angle_deg, curl=0.0):
            # angle_deg: 0 = up, 90 = right
            rad = math.radians(angle_deg - 90)
            
            # Knuckle (MCP)
            points[start_idx] = (base_x, base_y)
            
            # PIP
            p1_len = length * 0.4
            p1_x = base_x + math.cos(rad) * p1_len
            p1_y = base_y + math.sin(rad) * p1_len
            points[start_idx+1] = (p1_x, p1_y)
            
            # DIP (Apply curl)
            curl_rad = math.radians(angle_deg - 90 + curl)
            p2_len = length * 0.3
            p2_x = p1_x + math.cos(curl_rad) * p2_len
            p2_y = p1_y + math.sin(curl_rad) * p2_len
            points[start_idx+2] = (p2_x, p2_y)
            
            # TIP
            curl_rad2 = math.radians(angle_deg - 90 + curl * 2)
            p3_len = length * 0.3
            p3_x = p2_x + math.cos(curl_rad2) * p3_len
            p3_y = p2_y + math.sin(curl_rad2) * p3_len
            points[start_idx+3] = (p3_x, p3_y)

        # Base Knuckle positions (Palm arc)
        wrist = (0.5, 0.9)
        points[0] = wrist
        
        # Default Open Palm positions
        # Thumb (1-4)
        set_finger(1, 0.3, 0.7, 0.3, -45) 
        # Index (5-8)
        set_finger(5, 0.35, 0.55, 0.35, -10)
        # Middle (9-12)
        set_finger(9, 0.45, 0.5, 0.38, 0)
        # Ring (13-16)
        set_finger(13, 0.55, 0.52, 0.35, 10)
        # Pinky (17-20)
        set_finger(17, 0.65, 0.58, 0.25, 25)

        if gesture_name == "PAUME OUVERTE" or gesture_name == "PALM":
            # Already set as default (open palm)
            pass
            
        elif gesture_name == "PINCEMENT" or gesture_name == "PINCH":
            # Index curves to meet thumb
            set_finger(5, 0.35, 0.55, 0.35, -10, curl=150) # Curled index
            # Thumb moves to meet index
            set_finger(1, 0.3, 0.7, 0.3, -20, curl=30)
            
        elif gesture_name == "POING FERMÉ" or gesture_name == "FIST":
            # All fingers curled
            set_finger(5, 0.35, 0.55, 0.35, -10, curl=170)
            set_finger(9, 0.45, 0.5, 0.38, 0, curl=170)
            set_finger(13, 0.55, 0.52, 0.35, 10, curl=170)
            set_finger(17, 0.65, 0.58, 0.25, 25, curl=170)
            # Thumb tucked
            set_finger(1, 0.3, 0.7, 0.3, -45, curl=90)

        elif gesture_name == "VICTOIRE / V" or gesture_name == "TWO_FINGERS":
            # Index and Middle straight, others curled
            set_finger(5, 0.35, 0.55, 0.35, -15) # Spread out
            set_finger(9, 0.45, 0.5, 0.38, 15)   # Spread out
            # Curl Ring, Pinky, Thumb
            set_finger(13, 0.55, 0.52, 0.35, 10, curl=170)
            set_finger(17, 0.65, 0.58, 0.25, 25, curl=170)
            set_finger(1, 0.3, 0.7, 0.3, -45, curl=90)
            
        elif gesture_name == "POUCE LEVÉ" or gesture_name == "POINTING":
            # For POINTING: Only index extended, others curled (including thumb)
            # Index straight up
            set_finger(5, 0.45, 0.55, 0.4, 0)  # Index straight up
            # Curl others
            set_finger(1, 0.3, 0.7, 0.3, -45, curl=90)  # Thumb curled
            set_finger(9, 0.45, 0.5, 0.38, 0, curl=170)
            set_finger(13, 0.55, 0.52, 0.35, 10, curl=170)
            set_finger(17, 0.65, 0.58, 0.25, 25, curl=170)

        return points

    @staticmethod
    def generate_image(gesture_name, width=200, height=200, color=(0, 255, 255), thickness=2):
        """Generates a base64 encoded PNG of the skeleton."""
        img = np.zeros((height, width, 4), dtype=np.uint8) # BGRA transparent
        
        points = SkeletonAssets.get_landmark_pose(gesture_name)
        
        # Scale points to image dimensions
        # Add margin
        margin = 20
        draw_w = width - 2*margin
        draw_h = height - 2*margin
        
        screen_pts = []
        for p in points:
            px = int(p[0] * draw_w + margin)
            py = int(p[1] * draw_h + margin)
            screen_pts.append((px, py))
            
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]
        
        # Draw Bones
        for start, end in connections:
            pt1 = screen_pts[start]
            pt2 = screen_pts[end]
            cv2.line(img, pt1, pt2, (200, 200, 200, 255), thickness)
            
        # Draw Joints
        for pt in screen_pts:
            # BGRA color: B, G, R, A
            # Input color is RGB (likely), let's assume BGR for cv2 or convert
            # Flet Colors are Hex...
            # Let's use standard Cyan and Purple for now as defaults or parse input
            
            # Simple Circle
            cv2.circle(img, pt, thickness+2, (color[0], color[1], color[2], 255), -1)
            
        _, buffer = cv2.imencode('.png', img)
        return base64.b64encode(buffer).decode('utf-8')
