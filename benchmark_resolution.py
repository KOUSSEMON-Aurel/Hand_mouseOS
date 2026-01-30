import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time

def benchmark_resolution(width, height, iterations=10):
    """Benchmark MediaPipe at a specific resolution"""
    model_path = 'assets/hand_landmarker.task'
    
    # Create test image
    image_data = np.zeros((height, width, 3), dtype=np.uint8)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_data)
    
    # Setup MediaPipe
    base_options = python.BaseOptions(model_asset_path=model_path, delegate=python.BaseOptions.Delegate.CPU)
    options = vision.HandLandmarkerOptions(base_options=base_options, running_mode=vision.RunningMode.IMAGE)
    
    latencies = []
    with vision.HandLandmarker.create_from_options(options) as landmarker:
        # Warmup
        for _ in range(3):
            landmarker.detect(mp_image)
        
        # Benchmark
        for _ in range(iterations):
            start = time.time()
            landmarker.detect(mp_image)
            latencies.append((time.time() - start) * 1000)
    
    avg_latency = sum(latencies) / len(latencies)
    return avg_latency

if __name__ == "__main__":
    print("=== MediaPipe Resolution Benchmark ===\n")
    
    resolutions = [
        (640, 480, "VGA (Default)"),
        (320, 240, "QVGA (Optimized)"),
        (160, 120, "QQVGA (Ultra-fast)"),
    ]
    
    for width, height, name in resolutions:
        latency = benchmark_resolution(width, height)
        print(f"{name:20} ({width}x{height}): {latency:6.2f}ms")
