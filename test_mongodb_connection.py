#!/usr/bin/env python3
"""
Test MongoDB connection with different SSL configurations
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection with various configurations"""
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment variables")
        return False
    
    print(f"🔍 Testing MongoDB connection...")
    print(f"🔍 URI: {mongodb_uri[:50]}...")  # Show first 50 chars for security
    
    # Configuration 1: Basic TLS
    print("\n📋 Configuration 1: Basic TLS")
    try:
        client1 = MongoClient(
            mongodb_uri,
            tls=True,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=15000
        )
        client1.admin.command('ping')
        print("✅ Configuration 1: SUCCESS")
        client1.close()
        return True
    except Exception as e:
        print(f"❌ Configuration 1: FAILED - {e}")
    
    # Configuration 2: TLS with invalid certificates allowed
    print("\n📋 Configuration 2: TLS with invalid certificates allowed")
    try:
        client2 = MongoClient(
            mongodb_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=15000
        )
        client2.admin.command('ping')
        print("✅ Configuration 2: SUCCESS")
        client2.close()
        return True
    except Exception as e:
        print(f"❌ Configuration 2: FAILED - {e}")
    
    # Configuration 3: Full TLS with all options
    print("\n📋 Configuration 3: Full TLS with all options")
    try:
        client3 = MongoClient(
            mongodb_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            retryWrites=True,
            w='majority',
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=15000,
            socketTimeoutMS=20000,
            maxPoolSize=50,
            minPoolSize=5
        )
        client3.admin.command('ping')
        print("✅ Configuration 3: SUCCESS")
        client3.close()
        return True
    except Exception as e:
        print(f"❌ Configuration 3: FAILED - {e}")
    
    # Configuration 4: No TLS (for local MongoDB)
    print("\n📋 Configuration 4: No TLS (local MongoDB)")
    try:
        # Replace the URI to remove TLS requirements
        local_uri = mongodb_uri.replace('mongodb+srv://', 'mongodb://')
        local_uri = local_uri.split('?')[0]  # Remove query parameters
        
        client4 = MongoClient(
            local_uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=15000
        )
        client4.admin.command('ping')
        print("✅ Configuration 4: SUCCESS (Local MongoDB)")
        client4.close()
        return True
    except Exception as e:
        print(f"❌ Configuration 4: FAILED - {e}")
    
    print("\n❌ All MongoDB connection configurations failed!")
    return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    if success:
        print("\n🎉 MongoDB connection test completed successfully!")
    else:
        print("\n💡 Suggestions:")
        print("1. Check your MONGODB_URI in .env file")
        print("2. Verify your MongoDB Atlas cluster is running")
        print("3. Check your network connection")
        print("4. Try whitelisting your IP in MongoDB Atlas")
        print("5. Verify your MongoDB credentials")
