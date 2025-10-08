#!/usr/bin/env python3
"""
Quick MongoDB Connection Test
This script tests if MongoDB connection is working properly.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB Connection...")
    
    mongodb_url = os.getenv('MONGODB_URI')
    print(f"MongoDB URL: {mongodb_url}")
    
    if not mongodb_url:
        print("❌ MONGODB_URI environment variable not found!")
        return False
    
    try:
        # Test connection
        client = MongoClient(mongodb_url)
        
        # Test database access
        db = client['voice_scam_detector']
        
        # Test collections
        users_collection = db['users']
        analyzed_calls_collection = db['analyzed_calls']
        
        # Test write operation
        test_doc = {
            "test": True,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = analyzed_calls_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test document
        analyzed_calls_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        # Test read operation
        count = analyzed_calls_collection.count_documents({})
        print(f"✅ Analyzed calls collection has {count} documents")
        
        client.close()
        print("✅ MongoDB connection test successful!")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ MongoDB test error: {e}")
        return False

def test_models():
    """Test if the models can be imported and initialized"""
    print("\n🔍 Testing Model Imports...")
    
    try:
        from user_model import user_model
        print("✅ UserModel imported successfully")
        
        from analyzed_call_model import analyzed_call_model
        print("✅ AnalyzedCallModel imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MongoDB Connection Test")
    print("=" * 40)
    
    # Test MongoDB connection
    mongodb_ok = test_mongodb_connection()
    
    # Test model imports
    models_ok = test_models()
    
    print("\n📋 Test Results:")
    print(f"   MongoDB Connection: {'✅ OK' if mongodb_ok else '❌ FAILED'}")
    print(f"   Model Imports: {'✅ OK' if models_ok else '❌ FAILED'}")
    
    if mongodb_ok and models_ok:
        print("\n✅ All tests passed! MongoDB should be working.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
