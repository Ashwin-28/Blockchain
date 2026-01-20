"""
Backend API Test Script
Tests the enrollment endpoint to diagnose the database issue
"""

import requests
import json
import os
from io import BytesIO
from PIL import Image

print("=" * 60)
print("BACKEND API TEST")
print("=" * 60)
print()

# Test health endpoint
print("1. Testing health endpoint...")
try:
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    print("   ✗ Backend server may not be running!")
print()

# Test stats endpoint
print("2. Testing stats endpoint...")
try:
    response = requests.get("http://localhost:5000/api/stats", timeout=5)
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Database Connected: {data.get('database_connected', 'Unknown')}")
    print(f"   Total Subjects: {data.get('total_subjects', 'Unknown')}")
    print(f"   Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"   ✗ Error: {e}")
print()

# Test enrollment endpoint with a dummy image
print("3. Testing enrollment endpoint...")
try:
    # Create a simple test image
    img = Image.new('RGB', (640, 480), color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    files = {
        'file': ('test.jpg', img_byte_arr, 'image/jpeg')
    }
    data = {
        'name': 'Test User',
        'type': 'facial'
    }
    
    response = requests.post(
        "http://localhost:5000/api/enroll",
        files=files,
        data=data,
        timeout=10
    )
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 201:
        print()
        print("   ⚠ ENROLLMENT FAILED!")
        if 'Database not available' in response.text:
            print("   ✗ Database is not available in the running backend")
            print("   → Backend needs to be restarted")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
