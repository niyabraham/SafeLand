import requests

# Test Coordinates (Kochi, Kerala)
url = "http://127.0.0.1:5000/predict-by-location"
payload = {"latitude": 9.9312, "longitude": 76.2673}

try:
    print("Testing backend...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ Success! Response:")
        print(response.json())
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"❌ Connection Failed: {e}")
    print("Make sure the backend is running in a separate terminal!")