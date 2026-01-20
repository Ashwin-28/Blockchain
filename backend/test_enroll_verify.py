#!/usr/bin/env python3
"""
Enrollment and Verification Test Script

This script demonstrates:
1. Enrolling a person with one image
2. Verifying with the same image (should PASS)
3. Verifying with another image of the same person (should PASS)
4. Verifying with a different person's image (should FAIL - NOT VERIFIED)
"""

import os
import sys
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.biometric_engine import BiometricEngine

# ============================================================
# CONFIGURATION
# ============================================================
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')
SIMILARITY_THRESHOLD = 0.65  # 65% similarity threshold for verification

# ============================================================
# PRETTY PRINTING
# ============================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}▶ {text}{Colors.END}")
    print(f"{Colors.YELLOW}{'-'*58}{Colors.END}")

def print_result(verified, similarity, msg):
    if verified:
        icon = "✅"
        status = f"{Colors.GREEN}VERIFIED{Colors.END}"
    else:
        icon = "❌"
        status = f"{Colors.RED}NOT VERIFIED{Colors.END}"
    
    sim_color = Colors.GREEN if similarity >= SIMILARITY_THRESHOLD else Colors.RED
    print(f"  {icon} {msg}")
    print(f"     Similarity: {sim_color}{similarity*100:.2f}%{Colors.END} (threshold: {SIMILARITY_THRESHOLD*100:.0f}%)")
    print(f"     Status: {status}")
    print()

# ============================================================
# MAIN TEST FUNCTIONS
# ============================================================
class BiometricEnrollmentSystem:
    """Simple enrollment system for testing."""
    
    def __init__(self):
        self.engine = BiometricEngine()
        self.enrolled_users = {}  # user_id -> embedding
    
    def enroll(self, user_id: str, image_path: str) -> bool:
        """Enroll a user with their biometric image."""
        print(f"  📝 Enrolling '{user_id}' with image: {os.path.basename(image_path)}")
        
        if not os.path.exists(image_path):
            print(f"  {Colors.RED}❌ Image not found: {image_path}{Colors.END}")
            return False
        
        # Extract features
        features = self.engine.extract_features(image_path, biometric_type='facial')
        
        if features is None:
            print(f"  {Colors.RED}❌ Failed to extract features{Colors.END}")
            return False
        
        # Store enrollment
        self.enrolled_users[user_id] = features
        print(f"  {Colors.GREEN}✅ Successfully enrolled '{user_id}' ({len(features)}D embedding){Colors.END}")
        return True
    
    def verify(self, user_id: str, image_path: str) -> tuple:
        """Verify if the image matches the enrolled user."""
        if user_id not in self.enrolled_users:
            print(f"  {Colors.RED}❌ User '{user_id}' not enrolled{Colors.END}")
            return False, 0.0
        
        if not os.path.exists(image_path):
            print(f"  {Colors.RED}❌ Image not found: {image_path}{Colors.END}")
            return False, 0.0
        
        # Extract features from verification image
        features = self.engine.extract_features(image_path, biometric_type='facial')
        
        if features is None:
            print(f"  {Colors.RED}❌ Failed to extract features from verification image{Colors.END}")
            return False, 0.0
        
        # Compare with enrolled features
        enrolled_features = self.enrolled_users[user_id]
        similarity = self.engine.compare(enrolled_features, features)
        
        verified = similarity >= SIMILARITY_THRESHOLD
        return verified, similarity


def run_tests():
    """Run comprehensive enrollment and verification tests."""
    
    print_header("BIOMETRIC ENROLLMENT & VERIFICATION TEST")
    
    # Initialize system
    system = BiometricEnrollmentSystem()
    
    # Define test images
    image_paths = {
        'Ajith1': os.path.join(IMAGES_DIR, 'Ajith1.jpg'),
        'Ajith2': os.path.join(IMAGES_DIR, 'Ajith2.jpg'),
        'Vijay1': os.path.join(IMAGES_DIR, 'Vijay1.jpeg'),
        'Vijay2': os.path.join(IMAGES_DIR, 'Vijay2.jpg'),
        'Simran1': os.path.join(IMAGES_DIR, 'Simran1.jpg'),
    }
    
    # Check all images exist
    print_section("Checking Available Images")
    all_exist = True
    for name, path in image_paths.items():
        exists = os.path.exists(path)
        status = f"{Colors.GREEN}✅ Found{Colors.END}" if exists else f"{Colors.RED}❌ Not Found{Colors.END}"
        print(f"  {name}: {status}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print(f"\n{Colors.RED}❌ Some images are missing. Please ensure all images are in {IMAGES_DIR}{Colors.END}")
        return
    
    # ============================================================
    # TEST 1: Enroll with Ajith1.jpg
    # ============================================================
    print_section("Step 1: ENROLLMENT - Enrolling 'Ajith' with Ajith1.jpg")
    enrolled = system.enroll("Ajith", image_paths['Ajith1'])
    
    if not enrolled:
        print(f"{Colors.RED}❌ Enrollment failed. Cannot proceed.{Colors.END}")
        return
    
    # ============================================================
    # TEST 2: Verify with SAME image (Ajith1.jpg)
    # ============================================================
    print_section("Step 2: VERIFICATION - Same image (Ajith1.jpg)")
    print(f"  Testing: Can we verify Ajith with the SAME image used for enrollment?")
    verified, similarity = system.verify("Ajith", image_paths['Ajith1'])
    print_result(verified, similarity, "Ajith1.jpg → Enrolled as Ajith")
    
    # ============================================================
    # TEST 3: Verify with DIFFERENT image of SAME person (Ajith2.jpg)
    # ============================================================
    print_section("Step 3: VERIFICATION - Different image, SAME person (Ajith2.jpg)")
    print(f"  Testing: Can we verify Ajith with a DIFFERENT image of the same person?")
    verified, similarity = system.verify("Ajith", image_paths['Ajith2'])
    print_result(verified, similarity, "Ajith2.jpg → Should match Ajith")
    
    # ============================================================
    # TEST 4: Verify with DIFFERENT person (Vijay1.jpeg)
    # ============================================================
    print_section("Step 4: VERIFICATION - DIFFERENT person (Vijay1.jpeg)")
    print(f"  Testing: Should Vijay's image match Ajith? (Expected: NO)")
    verified, similarity = system.verify("Ajith", image_paths['Vijay1'])
    print_result(verified, similarity, "Vijay1.jpeg → Should NOT match Ajith")
    
    # ============================================================
    # TEST 5: Verify with DIFFERENT person (Simran1.jpg)
    # ============================================================
    print_section("Step 5: VERIFICATION - DIFFERENT person (Simran1.jpg)")
    print(f"  Testing: Should Simran's image match Ajith? (Expected: NO)")
    verified, similarity = system.verify("Ajith", image_paths['Simran1'])
    print_result(verified, similarity, "Simran1.jpg → Should NOT match Ajith")
    
    # ============================================================
    # ADDITIONAL TEST: Enroll Vijay and verify
    # ============================================================
    print_section("Step 6: ENROLLMENT - Enrolling 'Vijay' with Vijay1.jpeg")
    system.enroll("Vijay", image_paths['Vijay1'])
    
    print_section("Step 7: VERIFICATION - Different image, SAME person (Vijay2.jpg)")
    print(f"  Testing: Can we verify Vijay with a DIFFERENT image of the same person?")
    verified, similarity = system.verify("Vijay", image_paths['Vijay2'])
    print_result(verified, similarity, "Vijay2.jpg → Should match Vijay")
    
    print_section("Step 8: CROSS-VERIFICATION - Vijay enrolled vs Ajith image")
    print(f"  Testing: Should Ajith's image match Vijay? (Expected: NO)")
    verified, similarity = system.verify("Vijay", image_paths['Ajith1'])
    print_result(verified, similarity, "Ajith1.jpg → Should NOT match Vijay")
    
    # ============================================================
    # SUMMARY
    # ============================================================
    print_header("TEST SUMMARY")
    print(f"""
  {Colors.BOLD}Key Results:{Colors.END}
  
  ✅ = VERIFIED (similarity >= {SIMILARITY_THRESHOLD*100:.0f}%)
  ❌ = NOT VERIFIED (similarity < {SIMILARITY_THRESHOLD*100:.0f}%)
  
  {Colors.BOLD}Expected Behavior:{Colors.END}
  - Same person, same image    → ✅ VERIFIED (100% match)
  - Same person, diff image    → ✅ VERIFIED (>= 65% match)
  - Different person           → ❌ NOT VERIFIED (< 65% match)
    """)


if __name__ == '__main__':
    print(f"\n{Colors.BOLD}🔐 Starting Biometric Enrollment & Verification Test...{Colors.END}\n")
    run_tests()
    print(f"\n{Colors.BOLD}🏁 Test Complete!{Colors.END}\n")
