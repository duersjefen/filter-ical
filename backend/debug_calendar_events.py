#!/usr/bin/env python3
"""Debug script to test calendar events endpoint."""

import requests

print("🧪 Testing calendar events endpoint...")
print(f"📤 Requesting: /calendars/99999/events")

try:
    response = requests.get("http://localhost:3000/calendars/99999/events")
    print(f"📥 Response status: {response.status_code}")
    print(f"📥 Response headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"📥 Response body: {response_data}")
    except:
        print(f"📥 Response text: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Error: {e}")