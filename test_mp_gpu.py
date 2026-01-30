import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time

def test_gpu():
    model_path = 'assets/hand_landmarker.task'
    image_data = np.zeros((480, 640, 3), dtype=np.uint8)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_data)

    print("--- Testing GPU Delegate ---")
    try:
        base_options = python.BaseOptions(model_asset_path=model_path, delegate=python.BaseOptions.Delegate.GPU)
        options = vision.HandLandmarkerOptions(base_options=base_options, running_mode=vision.RunningMode.IMAGE)
        with vision.HandLandmarker.create_from_options(options) as landmarker:
            start = time.time()
            landmarker.detect(mp_image)
            print(f"GPU Success! Latency: {(time.time()-start)*1000:.2f}ms")
    except Exception as e:
        print(f"GPU Failed: {e}")

    print("\n--- Testing CPU Delegate ---")
    try:
        base_options = python.BaseOptions(model_asset_path=model_path, delegate=python.BaseOptions.Delegate.CPU)
        options = vision.HandLandmarkerOptions(base_options=base_options, running_mode=vision.RunningMode.IMAGE)
        with vision.HandLandmarker.create_from_options(options) as landmarker:
            start = time.time()
            landmarker.detect(mp_image)
            print(f"CPU Success! Latency: {(time.time()-start)*1000:.2f}ms")
    except Exception as e:
        print(f"CPU Failed: {e}")

if __name__ == "__main__":
    test_gpu()
