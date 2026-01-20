"""
Biometric Engine Module

Handles biometric feature extraction using:
- DeepFace with FaceNet model for accurate facial recognition
- Fingerprint and Iris fallbacks
- L2-normalized embeddings for consistent comparison
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
    print("[WARN] OpenCV not installed")

# Import DeepFace for face recognition
try:
    from deepface import DeepFace
    from scipy.spatial.distance import cosine # Added scipy.spatial.distance.cosine for comparison
    DEEPFACE_AVAILABLE = True
    print("[OK] DeepFace loaded for facial recognition")
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("[WARN] DeepFace or Scipy not installed. Install with: pip install deepface scipy")

# Import TensorFlow with fallback (used for fingerprint/iris)
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("[WARN] TensorFlow not installed")


class BiometricEngine:
    """Biometric feature extraction and comparison engine using DeepFace."""
    
    # ArcFace produces 512-dimensional embeddings (better accuracy)
    # FaceNet produces 128-dimensional embeddings
    ARCFACE_DIM = 512
    FACENET_DIM = 128
    
    def __init__(self, feature_dim: int = 512):
        set_seeds()
        self.feature_dim = feature_dim
        # Use ArcFace for better accuracy (>70% requirement)
        # Fallback to FaceNet512 if ArcFace fails, then FaceNet
        self.face_model_name = 'ArcFace'  # Best accuracy: ArcFace > FaceNet512 > FaceNet
        self.detector_backend = 'retinaface'  # Best detection: retinaface > mtcnn > opencv
        self._warmup_deepface()
    
    def _warmup_deepface(self):
        """Pre-load DeepFace model to avoid cold start delays"""
        if DEEPFACE_AVAILABLE:
            try:
                # Use FaceNet for 128D embeddings (matches app.py config)
                self.face_model_name = 'Facenet'
                self.feature_dim = 128
                
                try:
                    DeepFace.build_model('Facenet')
                    print(f"[OK] DeepFace FaceNet model initialized (128D embeddings)")
                except Exception as e:
                    print(f"[WARN] FaceNet build failed: {e}")
                    # Fallback to FaceNet512 if basic FaceNet fails
                    try:
                        DeepFace.build_model('Facenet512')
                        print(f"[OK] DeepFace FaceNet512 model initialized (512D embeddings)")
                        self.face_model_name = 'Facenet512'
                        self.feature_dim = 512
                    except Exception as e2:
                        print(f"[WARN] FaceNet512 build failed: {e2}")

                # Test detector backends in order of preference
                test_image = np.zeros((224, 224, 3), dtype=np.uint8)
                dummy_path = os.path.join(os.path.dirname(__file__), '..', 'uploads', '_warmup.jpg')
                os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
                if CV2_AVAILABLE:
                    cv2.imwrite(dummy_path, test_image)
                
                # Try detectors in order: retinaface > mtcnn > opencv
                for detector in ['retinaface', 'mtcnn', 'opencv']:
                    try:
                        if os.path.exists(dummy_path):
                            DeepFace.represent(
                                img_path=dummy_path,
                                model_name=self.face_model_name,
                                detector_backend=detector,
                                enforce_detection=False
                            )
                            self.detector_backend = detector
                            print(f"[OK] Using detector backend: {detector}")
                            break
                    except Exception:
                        continue
                
                # Cleanup
                if os.path.exists(dummy_path):
                    os.remove(dummy_path)
            except Exception as e:
                print(f"[WARN] DeepFace warmup note: {e}")

    def extract_features(self, image_path: str, biometric_type: str = 'facial') -> Optional[np.ndarray]:
        """Extract biometric features using DeepFace for facial recognition."""
        
        if biometric_type == 'facial':
            return self._extract_facial_features(image_path)
        elif biometric_type == 'fingerprint':
            return self._extract_fingerprint_features(image_path)
        elif biometric_type == 'iris':
            return self._extract_iris_features(image_path)
        else:
            return self._fallback_features(image_path)
    
    def _extract_facial_features(self, image_path: str) -> Optional[np.ndarray]:
        """Extract facial features using DeepFace with improved face detection."""
        
        if not DEEPFACE_AVAILABLE:
            print("[WARN] DeepFace not available, using fallback")
            return self._fallback_features(image_path)
        
        # Try multiple detector backends in order of accuracy
        detector_backends = [self.detector_backend, 'retinaface', 'mtcnn', 'opencv']
        
        for detector in detector_backends:
            try:
                # First, verify face is detected (enforce_detection=True for quality)
                try:
                    # Try with enforce_detection=True first to ensure face is found
                    result = DeepFace.represent(
                        img_path=image_path,
                        model_name=self.face_model_name,
                        enforce_detection=True,  # Require face detection
                        detector_backend=detector,
                        align=True  # Face alignment improves accuracy
                    )
                except ValueError as ve:
                    # If enforce_detection=True fails, try with False but log warning
                    if "Face could not be detected" in str(ve) or "could not detect a face" in str(ve).lower():
                        print(f"[WARN] Face not detected with {detector}, trying with relaxed detection...")
                        result = DeepFace.represent(
                            img_path=image_path,
                            model_name=self.face_model_name,
                            enforce_detection=False,
                            detector_backend=detector,
                            align=True
                        )
                    else:
                        raise
                
                if result and len(result) > 0:
                    embedding = np.array(result[0]['embedding'], dtype=np.float32)
                    
                    # Verify embedding quality
                    if len(embedding) == 0 or np.isnan(embedding).any() or np.isinf(embedding).any():
                        print(f"[WARN] Invalid embedding from {detector}, trying next detector...")
                        continue
                    
                    # L2 normalize for consistent cosine similarity
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm
                    else:
                        print(f"[WARN] Zero norm embedding from {detector}, trying next detector...")
                        continue
                    
                    # Ensure correct feature dimension
                    if len(embedding) != self.feature_dim:
                        if len(embedding) > self.feature_dim:
                            # Truncate if larger
                            embedding = embedding[:self.feature_dim]
                        else:
                            # Pad if smaller
                            padding = np.zeros(self.feature_dim - len(embedding), dtype=np.float32)
                            embedding = np.concatenate([embedding, padding])
                    
                    print(f"[OK] Extracted {len(embedding)}D facial embedding using {detector} + {self.face_model_name}")
                    print(f"   Embedding stats: min={embedding.min():.4f}, max={embedding.max():.4f}, mean={embedding.mean():.4f}, norm={np.linalg.norm(embedding):.4f}")
                    return embedding
                else:
                    print(f"[WARN] No face embedding returned from {detector}")
                    continue
                    
            except Exception as e:
                print(f"[WARN] DeepFace extraction error with {detector}: {e}")
                continue
        
        # If all detectors fail, try OpenCV fallback
        print("[WARN] All DeepFace detectors failed, trying OpenCV fallback...")
        return self._opencv_facial_features(image_path)
    
    def _opencv_facial_features(self, image_path: str) -> Optional[np.ndarray]:
        """Fallback facial feature extraction using OpenCV with improved preprocessing."""
        if not CV2_AVAILABLE:
            return self._fallback_features(image_path)
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                print("[WARN] Could not read image with OpenCV")
                return self._fallback_features(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Face detection with multiple cascades for better detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) > 0:
                # Use largest face
                (x, y, w, h) = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
                
                # Crop face with padding
                p = 0.2  # 20% padding
                y1 = max(0, int(y - h * p))
                y2 = min(img.shape[0], int(y + h * (1 + p)))
                x1 = max(0, int(x - w * p))
                x2 = min(img.shape[1], int(x + w * (1 + p)))
                face_img = gray[y1:y2, x1:x2]
                
                # Resize to standard size for feature extraction
                face_img = cv2.resize(face_img, (160, 160))
                
                # Apply histogram equalization for better contrast
                face_img = cv2.equalizeHist(face_img)
                
                # Extract multiple feature types for better representation
                # 1. Histogram features
                hist = cv2.calcHist([face_img], [0], None, [128], [0, 256])
                hist = hist.flatten().astype(np.float32)
                
                # 2. LBP-like features (Local Binary Pattern approximation)
                # Divide image into blocks and compute histograms
                features_list = [hist]
                block_size = 40
                for i in range(0, face_img.shape[0] - block_size, block_size):
                    for j in range(0, face_img.shape[1] - block_size, block_size):
                        block = face_img[i:i+block_size, j:j+block_size]
                        block_hist = cv2.calcHist([block], [0], None, [32], [0, 256])
                        features_list.append(block_hist.flatten().astype(np.float32))
                
                # Combine all features
                combined_features = np.concatenate(features_list).astype(np.float32)
                
                # Pad or truncate to feature_dim
                if len(combined_features) < self.feature_dim:
                    padding = np.zeros(self.feature_dim - len(combined_features), dtype=np.float32)
                    combined_features = np.concatenate([combined_features, padding])
                else:
                    combined_features = combined_features[:self.feature_dim]
                
                # Normalize
                norm = np.linalg.norm(combined_features)
                if norm > 0:
                    combined_features = combined_features / norm
                
                print(f"✓ Extracted {len(combined_features)}D features using OpenCV fallback")
                return combined_features
            else:
                print("⚠ No face detected with OpenCV cascade")
                return self._fallback_features(image_path)
            
        except Exception as e:
            print(f"⚠ OpenCV fallback error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_features(image_path)
    
    def _extract_fingerprint_features(self, image_path: str) -> Optional[np.ndarray]:
        """Extract fingerprint features (placeholder for future implementation)."""
        return self._fallback_features(image_path)
    
    def _extract_iris_features(self, image_path: str) -> Optional[np.ndarray]:
        """Extract iris features (placeholder for future implementation)."""
        return self._fallback_features(image_path)

    def _fallback_features(self, image_path: str) -> np.ndarray:
        """Deterministic fallback features based on perceptual hashing."""
        try:
            if not CV2_AVAILABLE:
                # Absolute fallback if CV2 is missing
                h = hashlib.sha256(image_path.encode()).digest()
                return np.frombuffer(h * (self.feature_dim // 32 + 1), dtype=np.float32)[:self.feature_dim]
            
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            small = cv2.resize(img, (16, 8)) if img is not None else np.zeros((8, 16))
            features = small.flatten().astype(np.float32) / 255.0
            return features if len(features) == self.feature_dim else np.resize(features, self.feature_dim)
        except Exception:
            return np.zeros(self.feature_dim, dtype=np.float32)

    def compare(self, f1, f2, method='cosine'):
        """Compare two feature vectors and return similarity score (0-1)."""
        if f1 is None or f2 is None: 
            print("[WARN] Comparison failed: one or both features are None")
            return 0.0
        
        # Ensure same shape and type
        f1 = np.array(f1, dtype=np.float32).flatten()
        f2 = np.array(f2, dtype=np.float32).flatten()
        
        if len(f1) != len(f2):
            min_len = min(len(f1), len(f2))
            f1 = f1[:min_len]
            f2 = f2[:min_len]
            print(f"[WARN] Feature dimension mismatch, using first {min_len} dimensions")
        
        # Check for invalid values
        if np.isnan(f1).any() or np.isnan(f2).any():
            print("[WARN] Comparison failed: NaN values in features")
            return 0.0
        
        if np.isinf(f1).any() or np.isinf(f2).any():
            print("[WARN] Comparison failed: Inf values in features")
            return 0.0
        
        # Normalize both vectors for consistent comparison
        norm1 = np.linalg.norm(f1)
        norm2 = np.linalg.norm(f2)
        if norm1 > 0:
            f1 = f1 / norm1
        if norm2 > 0:
            f2 = f2 / norm2
        
        if method == 'cosine':
            # Cosine similarity: dot product of normalized vectors
            # Since vectors are normalized, cosine similarity = dot product
            # Range is [-1, 1], but for normalized vectors it's typically [0, 1]
            cosine_sim = np.clip(np.dot(f1, f2), -1.0, 1.0)
            # Map from [-1, 1] to [0, 1] for consistency
            similarity = float((cosine_sim + 1) / 2)
            return similarity
        else:
            # Euclidean distance converted to similarity
            euclidean_dist = np.linalg.norm(f1 - f2)
            similarity = float(1 / (1 + euclidean_dist))
            return similarity

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

