# test_api.py
import requests
import time
from config import API_BASE_URL, TIMEOUT_SECONDS

print("="*60)
print("TESTING API ENDPOINTS")
print("="*60)
print(f"API URL: {API_BASE_URL}")
print()

# Test healthy endpoint
print("1. Testing /healthy endpoint...")
try:
    start = time.time()
    response = requests.get(f"{API_BASE_URL}/healthy", timeout=TIMEOUT_SECONDS)
    elapsed = time.time() - start
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS - Status: {response.status_code}, Time: {elapsed:.2f}s")
        print(f"   Response: {data}")
    else:
        print(f"   ❌ FAILED - Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ ERROR - {str(e)}")

print()

# Test unreliable endpoint (5 times)
print("2. Testing /unreliable endpoint (5 times)...")
success_count = 0
for i in range(5):
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/unreliable", timeout=TIMEOUT_SECONDS)
        elapsed = time.time() - start
        if response.status_code == 200:
            success_count += 1
            print(f"   Attempt {i+1}: ✅ SUCCESS - Time: {elapsed:.2f}s")
        else:
            print(f"   Attempt {i+1}: ❌ FAILED (HTTP {response.status_code}) - Time: {elapsed:.2f}s")
    except Exception as e:
        print(f"   Attempt {i+1}: ❌ ERROR - {str(e)}")
print(f"   Success rate: {success_count}/5 ({success_count*20}%)")

print()

# Test slow endpoint
print("3. Testing /slow endpoint (this may take up to 10 seconds)...")
try:
    start = time.time()
    response = requests.get(f"{API_BASE_URL}/slow", timeout=12)  # Longer timeout for slow endpoint
    elapsed = time.time() - start
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS - Total time: {elapsed:.2f}s")
        print(f"   API reported delay: {data.get('delay_seconds')}s")
    else:
        print(f"   ❌ FAILED - Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ ERROR - {str(e)}")

print()
print("="*60)
