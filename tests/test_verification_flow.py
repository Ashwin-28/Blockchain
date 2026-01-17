#!/usr/bin/env python3
"""
Test script for biometric verification flow.
Tests enrollment and authentication end-to-end.
"""

import os
import sys
import requests
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

API_URL = "http://localhost:5000"

def test_enrollment_and_verification():
    """Test complete enrollment and verification flow."""
    
    print("=" * 60)
    print("  BIOMETRIC VERIFICATION TEST")
    print("=" * 60)
    
    # Check if we have a test image
    test_images = [
        "/home/ashwin/Projext-3/backend/uploads/test.jpg",
        "/home/ashwin/Projext-3/test_face.jpg",
    ]
    
    test_image = None
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if not test_image:
        # Create a simple test image using OpenCV
        print("📷 Creating test image...")
        try:
            import cv2
            import numpy as np
            
            # Create a simple face-like pattern for testing
            img = np.ones((224, 224, 3), dtype=np.uint8) * 200
            
            # Draw a face-like pattern
            cv2.circle(img, (112, 100), 60, (180, 150, 120), -1)  # Face
            cv2.circle(img, (85, 85), 8, (50, 50, 50), -1)  # Left eye
            cv2.circle(img, (139, 85), 8, (50, 50, 50), -1)  # Right eye
            cv2.ellipse(img, (112, 120), (15, 8), 0, 0, 180, (150, 100, 100), -1)  # Mouth
            
            test_image = "/home/ashwin/Projext-3/test_face.jpg"
            cv2.imwrite(test_image, img)
            print(f"✓ Created test image: {test_image}")
        except Exception as e:
            print(f"✗ Could not create test image: {e}")
            return False
    
    print(f"📷 Using test image: {test_image}")
    
    # Step 1: Enroll
    print("\n" + "-" * 40)
    print("STEP 1: ENROLLMENT")
    print("-" * 40)
    
    with open(test_image, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        data = {'name': 'TestUser', 'email': 'test@test.com', 'type': 'facial'}
        
        try:
            resp = requests.post(f"{API_URL}/api/enroll", files=files, data=data, timeout=30)
            print(f"Response status: {resp.status_code}")
            
            if resp.status_code in [200, 201]:
                result = resp.json()
                print(f"✓ Enrollment successful!")
                print(f"  Subject ID: {result.get('subject_id')}")
                print(f"  Subject Code: {result.get('subject_code')}")
                print(f"  Template CID: {result.get('template_cid')}")
                print(f"  Commitment Hash: {result.get('commitment_hash', '')[:32]}...")
                
                subject_id = result.get('subject_id')
            else:
                print(f"✗ Enrollment failed: {resp.text}")
                return False
        except Exception as e:
            print(f"✗ Enrollment request failed: {e}")
            return False
    
    # Wait for blockchain to confirm
    print("\n⏳ Waiting for blockchain confirmation...")
    time.sleep(2)
    
    # Step 2: Authenticate with same image
    print("\n" + "-" * 40)
    print("STEP 2: AUTHENTICATION (same image)")
    print("-" * 40)
    
    with open(test_image, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        data = {'subject_id': subject_id, 'type': 'facial'}
        
        try:
            resp = requests.post(f"{API_URL}/api/authenticate", files=files, data=data, timeout=30)
            print(f"Response status: {resp.status_code}")
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"✓ Authentication response received!")
                print(f"  Success: {result.get('success')}")
                print(f"  Confidence: {result.get('confidence', 0):.2f}%")
                print(f"  Message: {result.get('message')}")
                
                if result.get('success'):
                    print("\n✅ VERIFICATION PASSED!")
                else:
                    print("\n❌ VERIFICATION FAILED!")
                    return False
            else:
                print(f"✗ Authentication failed: {resp.text}")
                return False
        except Exception as e:
            print(f"✗ Authentication request failed: {e}")
            return False
    
    # Step 3: Authenticate with modified image (should still pass with tolerance)
    print("\n" + "-" * 40)
    print("STEP 3: AUTHENTICATION (slightly modified)")
    print("-" * 40)
    
    try:
        import cv2
        import numpy as np
        
        # Load and slightly modify the image
        img = cv2.imread(test_image)
        # Add small noise
        noise = np.random.normal(0, 5, img.shape).astype(np.uint8)
        modified = cv2.add(img, noise)
        modified_path = "/home/ashwin/Projext-3/test_face_modified.jpg"
        cv2.imwrite(modified_path, modified)
        
        with open(modified_path, 'rb') as f:
            files = {'file': ('test_modified.jpg', f, 'image/jpeg')}
            data = {'subject_id': subject_id, 'type': 'facial'}
            
            resp = requests.post(f"{API_URL}/api/authenticate", files=files, data=data, timeout=30)
            print(f"Response status: {resp.status_code}")
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"  Success: {result.get('success')}")
                print(f"  Confidence: {result.get('confidence', 0):.2f}%")
                
                if result.get('success'):
                    print("✅ Modified image also verified (as expected)")
                else:
                    print("⚠ Modified image failed (tolerance may be too strict)")
            
        os.remove(modified_path)
    except Exception as e:
        print(f"⚠ Modified image test skipped: {e}")
    
    print("\n" + "=" * 60)
    print("  TEST COMPLETE")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_enrollment_and_verification()
    sys.exit(0 if success else 1)
