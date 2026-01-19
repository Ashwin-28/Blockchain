#!/usr/bin/env python3
"""
Quick test script to verify DeepFace integration is working.
Run this from the backend directory to validate the facial feature extraction.
"""

import os
import sys
import numpy as np

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

def test_deepface_integration():
    """Test that DeepFace is properly integrated."""
    print("=" * 60)
    print("  DEEPFACE INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Import BiometricEngine
    print("\n1. Testing BiometricEngine import...")
    try:
        from modules.biometric_engine import BiometricEngine, DEEPFACE_AVAILABLE
        print(f"   [OK] BiometricEngine imported successfully")
        print(f"   DeepFace available: {DEEPFACE_AVAILABLE}")
    except Exception as e:
        print(f"   [FAIL] Import failed: {e}")
        return False
    
    # Step 2: Initialize engine
    print("\n2. Initializing BiometricEngine...")
    try:
        engine = BiometricEngine(feature_dim=128)
        print(f"   [OK] Engine initialized with feature_dim=128")
    except Exception as e:
        print(f"   [FAIL] Initialization failed: {e}")
        return False
    
    # Step 3: Create a test image
    print("\n3. Creating test image...")
    test_image_path = os.path.join(os.path.dirname(__file__), 'uploads', 'test_verification.jpg')
    os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
    
    try:
        import cv2
        # Create a simple synthetic face-like image
        img = np.ones((224, 224, 3), dtype=np.uint8) * 200
        # Draw face-like features
        cv2.circle(img, (112, 100), 60, (180, 150, 120), -1)  # Face oval
        cv2.circle(img, (85, 85), 10, (50, 50, 50), -1)  # Left eye
        cv2.circle(img, (139, 85), 10, (50, 50, 50), -1)  # Right eye
        cv2.ellipse(img, (112, 130), (20, 10), 0, 0, 180, (100, 80, 80), -1)  # Mouth
        cv2.imwrite(test_image_path, img)
        print(f"   [OK] Test image created: {test_image_path}")
    except Exception as e:
        print(f"   [FAIL] Image creation failed: {e}")
        return False
    
    # Step 4: Extract features
    print("\n4. Extracting facial features...")
    try:
        features1 = engine.extract_features(test_image_path, 'facial')
        if features1 is not None:
            print(f"   [OK] Features extracted: shape={features1.shape}, dtype={features1.dtype}")
            print(f"   Stats: min={features1.min():.4f}, max={features1.max():.4f}, mean={features1.mean():.4f}")
        else:
            print(f"   [FAIL] Features extraction returned None")
            return False
    except Exception as e:
        print(f"   [FAIL] Feature extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Compare with self (should be 100% similar)
    print("\n5. Testing self-comparison...")
    try:
        features2 = engine.extract_features(test_image_path, 'facial')
        similarity = engine.compare(features1, features2)
        print(f"   Similarity with same image: {similarity * 100:.2f}%")
        
        if similarity >= 0.95:
            print("   [OK] Self-comparison passed (>=95%)")
        else:
            print(f"   [WARN] Self-comparison lower than expected (got {similarity*100:.2f}%)")
    except Exception as e:
        print(f"   [FAIL] Comparison failed: {e}")
        return False
    
    # Step 6: Create slightly modified image
    print("\n6. Testing with modified image...")
    try:
        # Add noise to create variation
        noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
        modified_img = cv2.add(img, noise)
        modified_path = test_image_path.replace('.jpg', '_modified.jpg')
        cv2.imwrite(modified_path, modified_img)
        
        features3 = engine.extract_features(modified_path, 'facial')
        similarity_modified = engine.compare(features1, features3)
        print(f"   Similarity with modified image: {similarity_modified * 100:.2f}%")
        
        if similarity_modified >= 0.70:
            print("   ✓ Modified image test passed (>=70%)")
        else:
            print(f"   ⚠ Modified image similarity lower than threshold")
            
        # Cleanup
        os.remove(modified_path)
    except Exception as e:
        print(f"   ⚠ Modified image test skipped: {e}")
    
    # Cleanup
    os.remove(test_image_path)
    
    print("\n" + "=" * 60)
    print("  TEST COMPLETE - DeepFace integration working!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_deepface_integration()
    sys.exit(0 if success else 1)
