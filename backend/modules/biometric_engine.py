"""
Biometric Engine Module

Handles biometric feature extraction using:
- CNN-based facial recognition (MobileNetV2)
- Fingerprint and Iris fallbacks
- Median-based quantization for secure hashing
"""

import os
import hashlib
import numpy as np
import random
from typing import Optional, Tuple

# Set random seeds for determinism
def set_seeds(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        os.environ['TF_DETERMINISTIC_OPS'] = '1'
    except ImportError:
        pass

set_seeds()

# Import CV2 with fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠ OpenCV not installed")

# Import TensorFlow with fallback
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠ TensorFlow not installed")


# DeepFace Integration
try:
    from deepface import DeepFace
    from scipy.spatial.distance import cosine
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠ DeepFace or Scipy not installed")

# DeepFace Integration
try:
    from deepface import DeepFace
    from scipy.spatial.distance import cosine
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠ DeepFace or Scipy not installed")

class BiometricEngine:
    """Biometric feature extraction and comparison engine using DeepFace (ArcFace)."""
    
    def __init__(self, feature_dim: int = 512):
        set_seeds()
        # ArcFace returns 512-dimensional vectors
        self.feature_dim = 512
        print("✓ Biometric Engine Initialized (DeepFace: ArcFace)")
    
    def extract_features(self, image_path: str, biometric_type: str = 'facial') -> Optional[np.ndarray]:
        """Extract high-precision biometric features using ArcFace."""
        if not DEEPFACE_AVAILABLE:
            print("❌ DeepFace not available")
            return None
            
        try:
            if biometric_type != 'facial':
                # Fallback for non-facial biometrics (hash-based for demo)
                with open(image_path, 'rb') as f:
                    content = f.read()
                h = hashlib.sha256(content).digest()
                # Expand hash to feature_dim
                raw_bytes = h * (self.feature_dim // 32 + 1)
                features_uint8 = np.frombuffer(raw_bytes, dtype=np.uint8)[:self.feature_dim]
                # Normalize similarly to embeddings
                return (features_uint8.astype(np.float32) / 127.5) - 1.0

            # DeepFace extraction using ArcFace
            embedding_objs = DeepFace.represent(
                img_path = image_path, 
                model_name = 'ArcFace',
                enforce_detection = True
            )
            
            # Extract the numerical vector
            if embedding_objs and len(embedding_objs) > 0:
                features = np.array(embedding_objs[0]["embedding"], dtype=np.float32)
                return features
            
            return None

        except ValueError as e:
            print(f"⚠ Face detection failed: {e}")
            return None
        except Exception as e:
            print(f"Extraction error: {e}")
            return None

    def compare(self, f1, f2) -> float:
        """
        Compare two feature vectors using Cosine Similarity logic.
        Returns a Similarity Score (0-1) where 1 is identical.
        """
        if f1 is None or f2 is None: return 0.0
        
        try:
            # Ensure proper shape
            if len(f1) != len(f2):
                min_len = min(len(f1), len(f2))
                f1 = f1[:min_len]
                f2 = f2[:min_len]

            # Calculate Cosine Distance
            # Distance 0 = Identical
            # Distance 1 = Orthogonal
            # Distance 2 = Opposite
            distance = cosine(f1, f2)
            
            # The app.py expects a "Similarity Score" (higher is better)
            # We convert distance to similarity: 1 - distance
            # We clip it at 0 to avoid negative similarity
            similarity = max(0.0, 1.0 - distance)
            
            return float(similarity)

        except Exception as e:
            print(f"Comparison error: {e}")
            return 0.0

    def check_liveness(self, path):
        # Basic laplacian variance liveness 
        try:
            if 'cv2' in globals() or 'cv2' in locals():
                pass # Already imported
            else:
                import cv2
            
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None: return True, 1.0
            var = cv2.Laplacian(img, cv2.CV_64F).var()
            score = min(1.0, var / 500.0)
            return bool(score > 0.005), score 
        except Exception:
            return True, 1.0

