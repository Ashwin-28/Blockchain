import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000/api"
IMAGES_DIR = "c:/Users/Ramanathan/Desktop/Kavin/Blockchain_AG/images"

def test_mismatch():
    print("1. Enrolling Vijay1...")
    vijay_path = os.path.join(IMAGES_DIR, "Vijay1.jpeg")
    if not os.path.exists(vijay_path):
        print(f"Error: {vijay_path} not found")
        print(f"Dir listing: {os.listdir(IMAGES_DIR)}")
        return

    with open(vijay_path, 'rb') as f:
        files = {'file': ('Vijay1.jpeg', f, 'image/jpeg')}
        data = {'name': 'Vijay', 'type': 'facial'}
        r = requests.post(f"{BASE_URL}/enroll", files=files, data=data)
    
    enroll_res = r.json()
    print(json.dumps(enroll_res, indent=2))
    
    if r.status_code != 201:
        print("Enrollment failed")
        return

    subject_id = enroll_res['subject_id']
    print(f"\nSubject ID: {subject_id}")

    print("\n2. Authenticating with Simran1 (Should FAIL)...")
    simran_path = os.path.join(IMAGES_DIR, "Simran1.jpg")
    if not os.path.exists(simran_path):
        print(f"Error: {simran_path} not found")
        return

    with open(simran_path, 'rb') as f:
        files = {'file': ('Simran1.jpg', f, 'image/jpeg')}
        data = {'subject_id': subject_id, 'type': 'facial'}
        r = requests.post(f"{BASE_URL}/authenticate", files=files, data=data)
    
    auth_res = r.json()
    print(f"Status Code: {r.status_code}")
    print("Full Response:", json.dumps(auth_res, indent=2))

    if auth_res.get('success') or auth_res.get('authenticated'):
        print("\n❌ ISSUE REPRODUCED: Wrong person was verified!")
    else:
        print("\n✅ CORRECT BEHAVIOR: Wrong person was rejected.")

if __name__ == "__main__":
    test_mismatch()
