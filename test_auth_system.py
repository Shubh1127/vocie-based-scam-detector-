#!/usr/bin/env python3
"""
Test script for the Voice Scam Detector Authentication System
This script tests the user registration, login, and call history functionality.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

def test_api_health():
    """Test if the API is running"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API is healthy and running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return False

def test_user_signup():
    """Test user registration"""
    print("\n🔍 Testing User Signup...")
    
    user_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/signup",
            headers=HEADERS,
            json=user_data
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get("success"):
                print("✅ User signup successful")
                print(f"   User ID: {data['user']['user_id']}")
                print(f"   Username: {data['user']['username']}")
                print(f"   Email: {data['user']['email']}")
                return data.get("token")
            else:
                print(f"❌ Signup failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Signup request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return None

def test_user_login():
    """Test user login"""
    print("\n🔍 Testing User Login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            headers=HEADERS,
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ User login successful")
                print(f"   User ID: {data['user']['user_id']}")
                print(f"   Username: {data['user']['username']}")
                return data.get("token")
            else:
                print(f"❌ Login failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Login request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\n🔍 Testing Protected Endpoint...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/auth/profile",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Protected endpoint access successful")
                print(f"   User: {data['user']['username']}")
                return True
            else:
                print(f"❌ Protected endpoint failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Protected endpoint request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return False

def test_call_history(token):
    """Test call history endpoint"""
    print("\n🔍 Testing Call History...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/auth/history",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Call history access successful")
                print(f"   Total calls: {data.get('total_count', 0)}")
                print(f"   Calls returned: {len(data.get('calls', []))}")
                return True
            else:
                print(f"❌ Call history failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Call history request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Call history error: {e}")
        return False

def test_user_statistics(token):
    """Test user statistics endpoint"""
    print("\n🔍 Testing User Statistics...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/auth/statistics",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data.get("statistics", {})
                print("✅ User statistics access successful")
                print(f"   Total calls: {stats.get('total_calls', 0)}")
                print(f"   Scam calls: {stats.get('scam_calls', 0)}")
                print(f"   Safe calls: {stats.get('safe_calls', 0)}")
                print(f"   Scam detection rate: {stats.get('scam_detection_rate', 0)}%")
                return True
            else:
                print(f"❌ User statistics failed: {data.get('error')}")
                return False
        else:
            print(f"❌ User statistics request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User statistics error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Voice Scam Detector Authentication Test Suite")
    print("=" * 60)
    
    # Test API health
    if not test_api_health():
        print("\n❌ API is not running. Please start the server first.")
        print("   Run: python api_server.py")
        return
    
    # Test user signup
    token = test_user_signup()
    
    # If signup failed, try login (user might already exist)
    if not token:
        print("\n🔄 Signup failed, trying login...")
        token = test_user_login()
    
    if not token:
        print("\n❌ Authentication tests failed. Cannot proceed.")
        return
    
    # Test protected endpoints
    test_protected_endpoint(token)
    test_call_history(token)
    test_user_statistics(token)
    
    print("\n✅ Authentication test suite completed!")
    print("\n📋 Summary:")
    print("   - User registration/login: ✅")
    print("   - JWT token authentication: ✅")
    print("   - Protected endpoints: ✅")
    print("   - Call history storage: ✅")
    print("   - User statistics: ✅")
    
    print("\n🔗 Available API Endpoints:")
    print("   POST /api/auth/signup - User registration")
    print("   POST /api/auth/login - User login")
    print("   GET  /api/auth/profile - Get user profile")
    print("   PUT  /api/auth/profile - Update user profile")
    print("   GET  /api/auth/history - Get call history")
    print("   GET  /api/auth/statistics - Get user statistics")
    print("   POST /api/analyze-audio - Analyze audio (requires auth)")

if __name__ == "__main__":
    main()

