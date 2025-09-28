#!/usr/bin/env python3
"""Debug script to test calendar creation."""

import requests
import json

# Test data that should work
test_data = {
    "name": "Test Calendar",
    "source_url": "https://example.com/test.ics"
}

print("🧪 Testing calendar creation...")
print(f"📤 Sending: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post("http://localhost:3000/calendars", json=test_data)
    print(f"📥 Response status: {response.status_code}")
    print(f"📥 Response headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"📥 Response body: {json.dumps(response_data, indent=2)}")
    except:
        print(f"📥 Response text: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")