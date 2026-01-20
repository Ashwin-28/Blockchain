import requests
import os
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"
TEST_IMAGE = "c:/Users/Ramanathan/Desktop/Kavin/Blockchain_AG/test_face.jpg"

def print_section(title):
    print("\n" + "="*60)
    print(f" {title.upper()}")
    print("="*60)

def test_health():
    print_section("1. Testing Health & Status")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
        return r.json().get('status') == 'healthy'
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_enrollment():
    print_section("2. Testing Subject Enrollment")
    if not os.path.exists(TEST_IMAGE):
        print(f"Error: Test image not found at {TEST_IMAGE}")
        return None
    
    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            data = {'name': 'Antigravity Test Bot', 'type': 'facial'}
            r = requests.post(f"{BASE_URL}/enroll", files=files, data=data)
            
        print(f"Status: {r.status_code}")
        res = r.json()
        print(json.dumps(res, indent=2))
        
        if r.status_code == 201:
            print(f"✅ Enrollment successful!")
            return res.get('subject_id')
        else:
            print(f"❌ Enrollment failed: {res.get('error')}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_authentication(subject_id):
    print_section("3. Testing Authentication")
    if not subject_id:
        print("Skipping Auth test - no subject ID available")
        return False
        
    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            data = {'subject_id': subject_id, 'type': 'facial'}
            r = requests.post(f"{BASE_URL}/authenticate", files=files, data=data)
            
        print(f"Status: {r.status_code}")
        res = r.json()
        print(json.dumps(res, indent=2))
        
        if res.get('success'):
            print(f"✅ Authentication verified!")
            return True
        else:
            print(f"❌ Authentication failed: {res.get('error') or res.get('message')}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_stats():
    print_section("4. Testing Statistics")
    try:
        r = requests.get(f"{BASE_URL}/stats")
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_subjects():
    print_section("5. Listing Subjects")
    try:
        r = requests.get(f"{BASE_URL}/subjects")
        print(f"Status: {r.status_code}")
        print(f"Total Subjects: {r.json().get('total')}")
        # print(json.dumps(r.json(), indent=2))
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    if not test_health(): success = False
    
    subject_id = test_enrollment()
    if not subject_id: success = False
    
    # Wait a bit for blockchain to settle
    time.sleep(2)
    
    if not test_authentication(subject_id): success = False
    
    if not test_stats(): success = False
    
    if not test_subjects(): success = False
    
    print_section("FINAL TEST SUMMARY")
    if success:
        print("🎉 ALL SYSTEMS GO! The Biometric Identity system is fully functional.")
    else:
        print("⚠️ SOME TESTS FAILED. Please check the logs above.")
