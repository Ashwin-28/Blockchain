import requests
import os

BASE_URL = "http://localhost:5000/api"
IMAGE_PATH = "/home/ashwin/.gemini/antigravity/brain/40414d9c-2fc4-44fd-830d-373049de6a3b/uploaded_image_1768598209030.jpg"

def test_workflow():
    print(f"--- Starting Test Workflow with {IMAGE_PATH} ---")
    
    # 1. Enroll
    print("\n1. Enrolling 'Ajith'...")
    with open(IMAGE_PATH, 'rb') as f:
        files = {'file': f}
        data = {'name': 'Ajith', 'type': 'facial'}
        response = requests.post(f"{BASE_URL}/enroll", files=files, data=data)
    
    if response.status_code != 201:
        print(f"Enrollment failed: {response.text}")
        return
    
    enroll_data = response.json()
    subject_id = enroll_data['subject_id']
    subject_code = enroll_data['subject_code']
    print(f"✓ Enrolled successfully!")
    print(f"  Subject ID: {subject_id}")
    print(f"  Human Code: {subject_code}")

    # 2. Verify (using the SAME image)
    print("\n2. Verifying (Base Case)...")
    with open(IMAGE_PATH, 'rb') as f:
        files = {'file': f}
        data = {'subject_id': subject_id, 'type': 'facial'}
        response = requests.post(f"{BASE_URL}/authenticate", files=files, data=data)
    
    if response.status_code == 200:
        auth_data = response.json()
        print(f"✓ Verification Result: {auth_data['message']}")
        print(f"  Confidence Score: {auth_data.get('confidence', 'N/A')}%")
        print(f"  Logged on Chain: {auth_data.get('logged_on_chain', False)}")
    else:
        print(f"Verification failed: {response.text}")

if __name__ == "__main__":
    test_workflow()
