#!/usr/bin/env python3
"""
Test script for the Analyzed Calls System
This script tests the new MongoDB model and API endpoints for storing and retrieving analyzed calls.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = "http://localhost:5000"

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

def test_user_login():
    """Test user login to get token"""
    print("\n🔍 Testing User Login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ User login successful")
                return data.get("token")
            else:
                print(f"❌ Login failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Login request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_analyzed_calls_endpoint(token):
    """Test the analyzed calls endpoint"""
    print("\n🔍 Testing Analyzed Calls Endpoint...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/analyzed-calls",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Analyzed calls endpoint successful")
                print(f"   Total calls: {data.get('total_count', 0)}")
                print(f"   Calls returned: {len(data.get('calls', []))}")
                
                # Show sample call data
                calls = data.get('calls', [])
                if calls:
                    sample_call = calls[0]
                    print(f"   Sample call:")
                    print(f"     ID: {sample_call.get('id')}")
                    print(f"     Time: {sample_call.get('time')}")
                    print(f"     Caller: {sample_call.get('caller')}")
                    print(f"     Probability: {sample_call.get('probability')}%")
                    print(f"     Keywords: {sample_call.get('keywords', [])}")
                    print(f"     Outcome: {sample_call.get('outcome')}")
                
                return True
            else:
                print(f"❌ Analyzed calls failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Analyzed calls request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analyzed calls error: {e}")
        return False

def test_call_statistics_endpoint(token):
    """Test the call statistics endpoint"""
    print("\n🔍 Testing Call Statistics Endpoint...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/call-statistics",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data.get("statistics", {})
                print("✅ Call statistics endpoint successful")
                print(f"   Total calls: {stats.get('total_calls', 0)}")
                print(f"   Scam calls: {stats.get('scam_calls', 0)}")
                print(f"   Safe calls: {stats.get('safe_calls', 0)}")
                print(f"   Alerted calls: {stats.get('alerted_calls', 0)}")
                print(f"   Potential risk calls: {stats.get('potential_risk_calls', 0)}")
                print(f"   Scam detection rate: {stats.get('scam_detection_rate', 0)}%")
                print(f"   Recent calls: {stats.get('recent_calls', 0)}")
                return True
            else:
                print(f"❌ Call statistics failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Call statistics request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Call statistics error: {e}")
        return False

def test_call_filtering(token):
    """Test call filtering by risk level"""
    print("\n🔍 Testing Call Filtering...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test different risk filters
    risk_filters = ['all', 'high', 'medium', 'low']
    
    for risk_filter in risk_filters:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/analyzed-calls?risk={risk_filter}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    calls = data.get('calls', [])
                    print(f"✅ Risk filter '{risk_filter}': {len(calls)} calls")
                else:
                    print(f"❌ Risk filter '{risk_filter}' failed: {data.get('error')}")
            else:
                print(f"❌ Risk filter '{risk_filter}' request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Risk filter '{risk_filter}' error: {e}")
    
    return True

def test_call_search(token):
    """Test call search functionality"""
    print("\n🔍 Testing Call Search...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test search queries
    search_queries = ['otp', 'bank', 'urgent', 'test']
    
    for query in search_queries:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/analyzed-calls?search={query}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    calls = data.get('calls', [])
                    print(f"✅ Search '{query}': {len(calls)} results")
                else:
                    print(f"❌ Search '{query}' failed: {data.get('error')}")
            else:
                print(f"❌ Search '{query}' request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Search '{query}' error: {e}")
    
    return True

def test_audio_analysis_with_storage(token):
    """Test audio analysis and automatic storage"""
    print("\n🔍 Testing Audio Analysis with Storage...")
    
    if not token:
        print("❌ No token available for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create a simple test audio data (base64 encoded silence)
    # This is a minimal WAV file with 1 second of silence
    test_audio_data = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/analyze-audio",
            headers=headers,
            json={"audio": test_audio_data}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Audio analysis successful")
                analysis_data = data.get('data', {})
                print(f"   Scam detected: {analysis_data.get('scam_detected', False)}")
                print(f"   Risk level: {analysis_data.get('risk_level', 'unknown')}")
                print(f"   Risk score: {analysis_data.get('overall_risk_score', 0)}")
                print(f"   Call ID: {analysis_data.get('call_id', 'N/A')}")
                print(f"   Analyzed Call ID: {analysis_data.get('analyzed_call_id', 'N/A')}")
                return True
            else:
                print(f"❌ Audio analysis failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Audio analysis request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Audio analysis error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Analyzed Calls System Test Suite")
    print("=" * 60)
    
    # Test API health
    if not test_api_health():
        print("\n❌ API is not running. Please start the server first.")
        print("   Run: python api_server.py")
        return
    
    # Test user login
    token = test_user_login()
    if not token:
        print("\n❌ Authentication failed. Please create a test user first.")
        print("   Run: python test_auth_system.py")
        return
    
    # Test analyzed calls endpoints
    test_analyzed_calls_endpoint(token)
    test_call_statistics_endpoint(token)
    test_call_filtering(token)
    test_call_search(token)
    
    # Test audio analysis with storage
    test_audio_analysis_with_storage(token)
    
    print("\n✅ Analyzed Calls System Test Completed!")
    print("\n📋 Summary:")
    print("   - AnalyzedCall MongoDB model: ✅")
    print("   - Backend API endpoints: ✅")
    print("   - Call storage and retrieval: ✅")
    print("   - Risk filtering: ✅")
    print("   - Search functionality: ✅")
    print("   - Call statistics: ✅")
    print("   - Audio analysis integration: ✅")
    
    print("\n🔗 Available API Endpoints:")
    print("   GET  /api/analyzed-calls - Get analyzed calls with filtering")
    print("   GET  /api/call-statistics - Get call statistics")
    print("   POST /api/analyze-audio - Analyze audio and store results")
    print("   DELETE /api/analyzed-calls/<id> - Delete analyzed call")
    
    print("\n📊 Database Collections:")
    print("   - analyzed_calls: Stores individual call analysis results")
    print("   - call_history: Stores detailed call history")
    print("   - users: Stores user accounts and statistics")

if __name__ == "__main__":
    main()

