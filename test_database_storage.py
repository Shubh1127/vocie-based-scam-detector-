#!/usr/bin/env python3
"""
Test script to verify database storage functionality
"""

import os
import sys
from datetime import datetime
import uuid

# Add current directory to path
sys.path.append('.')

def test_database_storage():
    """Test the database storage functionality"""
    print("🧪 TESTING DATABASE STORAGE")
    print("=" * 50)
    
    try:
        # Import the models
        from analyzed_call_model import analyzed_call_model
        print("✅ AnalyzedCallModel imported successfully")
        
        # Test data
        test_data = {
            'analysis_id': str(uuid.uuid4()),
            'user_id': None,  # No user for this test
            'timestamp': datetime.utcnow(),
            'audio_file_path': '/test/path/audio.wav',
            'transcription': {
                'full_text': 'Hello, this is a test call with scam keywords like otp and password',
                'speaker_text': {'0': ['hello', 'this', 'is', 'test'], '1': ['otp', 'password']},
                'words': []
            },
            'speaker_analysis': {
                '0': {
                    'text': 'hello this is test',
                    'scam_keywords': [],
                    'risk_score': 0.1,
                    'is_potential_scammer': False
                },
                '1': {
                    'text': 'otp password',
                    'scam_keywords': ['otp', 'password'],
                    'risk_score': 0.8,
                    'is_potential_scammer': True
                }
            },
            'overall_risk_score': 0.7,
            'risk_level': 'high',
            'scam_detected': True,
            'gemini_suggestion': 'This is a test scam call',
            'logic_scam_detected': True,
            'logic_reason': 'Test scam pattern detected',
            'call_summary': 'Test call summary',
            'audio_duration': 10.5,
            'speakers_detected': 2,
            'keywords_found': ['otp', 'password']
        }
        
        print("🔍 Test data created:")
        print(f"   Analysis ID: {test_data['analysis_id']}")
        print(f"   Transcription: {test_data['transcription']['full_text'][:50]}...")
        print(f"   Risk Score: {test_data['overall_risk_score']}")
        print(f"   Keywords: {test_data['keywords_found']}")
        
        # Test saving
        print("\n🔄 Testing database save...")
        save_result = analyzed_call_model.save_analyzed_call(None, test_data)
        print(f"🔍 Save result: {save_result}")
        
        if save_result.get('success'):
            print("✅ Test data saved successfully!")
            
            # Test retrieving
            print("\n🔄 Testing database retrieval...")
            calls = analyzed_call_model.get_analyzed_calls(None, 10, 0)
            print(f"🔍 Retrieved calls: {len(calls)}")
            
            if calls:
                print("✅ Test data retrieved successfully!")
                latest_call = calls[0]
                print(f"   Latest call ID: {latest_call.get('analysis_id')}")
                print(f"   Latest call text: {latest_call.get('transcription', {}).get('full_text', '')[:50]}...")
            else:
                print("❌ No calls retrieved")
        else:
            print(f"❌ Save failed: {save_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
    
    print("\n🎯 DATABASE STORAGE TEST COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    test_database_storage()
