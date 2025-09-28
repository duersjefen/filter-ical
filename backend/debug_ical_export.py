#!/usr/bin/env python3
"""Debug script to test iCal export."""

import requests

# Test UUID that should not exist
test_uuid = "550e8400-e29b-41d4-a716-446655440000"

print("🧪 Testing iCal export...")
print(f"📤 Requesting: /ical/{test_uuid}.ics")

try:
    response = requests.get(f"http://localhost:3000/ical/{test_uuid}.ics")
    print(f"📥 Response status: {response.status_code}")
    print(f"📥 Response headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"📥 Response body: {response_data}")
    except:
        print(f"📥 Response text: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Error: {e}")