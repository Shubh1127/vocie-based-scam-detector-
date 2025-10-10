#!/usr/bin/env python3
"""
Environment check script
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 CHECKING ENVIRONMENT")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check Google Cloud credentials
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if google_creds:
        print(f"✅ Google Cloud credentials: {google_creds}")
        if os.path.exists(google_creds):
            print("   ✅ Credentials file exists")
        else:
            print("   ❌ Credentials file not found!")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
    
    # Check Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        print(f"✅ Gemini API key: {gemini_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY not set")
    
    # Check MongoDB URI
    mongodb_uri = os.getenv('MONGODB_URI')
    if mongodb_uri:
        print(f"✅ MongoDB URI: {mongodb_uri[:20]}...")
    else:
        print("❌ MONGODB_URI not set")
    
    # Check JWT secret
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if jwt_secret:
        print(f"✅ JWT Secret: {jwt_secret[:10]}...")
    else:
        print("❌ JWT_SECRET_KEY not set")
    
    print("\n🎯 ENVIRONMENT CHECK COMPLETE!")
    print("=" * 40)

if __name__ == "__main__":
    check_environment()
