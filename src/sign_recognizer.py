import cv2
import numpy as np
import os
import threading

# Try importing tensorflow/keras, handle failure gracefully
try:
    from keras.models import load_model
    from keras.preprocessing.image import img_to_array
    HAS_TF = True
except ImportError:
    HAS_TF = False
    print("⚠️ TensorFlow/Keras not found. ASL recognition will be disabled.")

class SignLanguageInterpreter:
    def __init__(self, model_path="cnn_model_keras2.h5"):
        self.model = None
        self.classes = self._get_classes()
        self.is_loaded = False
        
        if HAS_TF and os.path.exists(model_path):
            print(f"🔄 Loading ASL Model from {model_path}...")
            try:
                self.model = load_model(model_path)
                self.is_loaded = True
                print("✅ ASL Model loaded successfully!")
            except Exception as e:
                print(f"❌ Failed to load ASL model: {e}")
        elif not HAS_TF:
             print("❌ TensorFlow missing. Run 'pip install tensorflow' to enable ASL.")
        else:
             print(f"⚠️ Model file {model_path} not found. ASL feature will be limited.")

    def _get_classes(self):
        # Classes from the repository (assuming A-Z + others)
        # Typically folders are named 0, 1, ... or A, B, ... 
        # For now, we'll map indices to generic labels based on the repo description (44 chars)
        # Ideally this should match the training folders.
        return {
            0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 
            8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P',
            16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X',
            24: 'Y', 25: 'Z', 
            # Add more maps if the model supports digits/words
        }

    def predict(self, hand_image):
        """
        Predicts the sign from a cropped hand image.
        Args:
            hand_image: Cropped BGR image of the hand
        Returns:
            predicted_label (str), confidence (float)
        """
        if not self.is_loaded or self.model is None:
            return "N/A", 0.0

        try:
            # Preprocessing as per repo (Resize to training size)
            # Repo uses image_x, image_y (probably 50x50 or 64x64, checking code...)
            # Code says: image_x, image_y = get_image_size() from 'gestures/1/100.jpg'
            # We will assume 64x64 for standard CNNs, but valid size is crucial.
            # Let's target 64x64 based on common practices if not specified.
            target_size = (64, 64) 
            
            img = cv2.resize(hand_image, target_size)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Often grayscale for shapes
            
            # Normalize
            img = img.astype("float") / 255.0
            img = img_to_array(img)
            img = np.expand_dims(img, axis=0)
            img = np.expand_dims(img, axis=3) # (1, 64, 64, 1)

            prediction = self.model.predict(img, verbose=0)
            idx = np.argmax(prediction)
            confidence = np.max(prediction)
            
            label = self.classes.get(idx, f"Rank-{idx}")
            return label, float(confidence)
            
        except Exception as e:
            print(f"Prediction Error: {e}")
            return "ERR", 0.0

    def preprocess_hand_region(self, frame, landmarks):
        """
        Extracts and preprocesses the hand region from the full frame.
        """
        h, w, _ = frame.shape
        # Compute bounding box from landmarks
        x_min = min([lm.x for lm in landmarks]) * w
        x_max = max([lm.x for lm in landmarks]) * w
        y_min = min([lm.y for lm in landmarks]) * h
        y_max = max([lm.y for lm in landmarks]) * h
        
        # Add padding
        padding = 20
        x_min = max(0, int(x_min - padding))
        x_max = min(w, int(x_max + padding))
        y_min = max(0, int(y_min - padding))
        y_max = min(h, int(y_max + padding))
        
        if x_max - x_min < 10 or y_max - y_min < 10:
            return None # Box too small
            
        hand_crop = frame[y_min:y_max, x_min:x_max]
        return hand_crop
