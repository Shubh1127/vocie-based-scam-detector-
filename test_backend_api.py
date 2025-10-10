#!/usr/bin/env python3
"""
Test script to check if the backend API is returning data correctly
"""

import requests
import json

def test_backend_api():
    """Test the backend API directly"""
    print("🧪 TESTING BACKEND API")
    print("=" * 40)
    
    try:
        # Test the analyzed-calls endpoint
        url = "http://localhost:5000/api/analyzed-calls"
        print(f"🔍 Testing URL: {url}")
        
        response = requests.get(url)
        print(f"🔍 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Response data: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                calls = data.get('data', [])
                print(f"✅ API working! Found {len(calls)} calls")
                
                if calls:
                    print("\n📊 Sample call data:")
                    sample_call = calls[0]
                    print(f"   - Timestamp: {sample_call.get('timestamp')}")
                    print(f"   - Caller: {sample_call.get('caller')}")
                    print(f"   - Probability: {sample_call.get('probability')}")
                    print(f"   - Keywords: {sample_call.get('keywords', [])}")
                    print(f"   - Outcome: {sample_call.get('outcome')}")
                else:
                    print("⚠️ No calls found in response")
            else:
                print(f"❌ API returned error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    print("\n🎯 API TEST COMPLETE!")
    print("=" * 40)

if __name__ == "__main__":
    test_backend_api()
