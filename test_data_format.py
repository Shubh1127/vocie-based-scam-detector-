#!/usr/bin/env python3
"""
Quick test to see what data format we're getting from the database
"""

import sys
sys.path.append('.')

from analyzed_call_model import analyzed_call_model

def test_data_format():
    """Test what data format we're getting"""
    print("🧪 TESTING DATA FORMAT")
    print("=" * 40)
    
    try:
        # Get calls from database
        calls = analyzed_call_model.get_analyzed_calls(None, 5, 0)
        print(f"🔍 Retrieved {len(calls)} calls")
        
        if calls:
            call = calls[0]
            print(f"\n📊 Sample call data structure:")
            print(f"   Keys: {list(call.keys())}")
            print(f"   Timestamp: {call.get('timestamp')}")
            print(f"   Caller: {call.get('caller')}")
            print(f"   Probability: {call.get('probability')}")
            print(f"   Keywords: {call.get('keywords')}")
            print(f"   Outcome: {call.get('outcome')}")
            print(f"   Scam detected: {call.get('scam_detected')}")
            print(f"   Overall risk score: {call.get('overall_risk_score')}")
            
            # Check transcription structure
            transcription = call.get('transcription', {})
            print(f"   Transcription type: {type(transcription)}")
            if isinstance(transcription, dict):
                print(f"   Transcription keys: {list(transcription.keys())}")
                print(f"   Full text: {transcription.get('full_text', 'NOT FOUND')[:50]}...")
            
            print(f"\n🔍 What frontend expects:")
            print(f"   - c.transcription?.full_text")
            print(f"   - c.overall_risk_score")
            print(f"   - c.keywords_found")
            print(f"   - c.scam_detected")
            
            print(f"\n🔍 What we have:")
            print(f"   - transcription.full_text: {'✅' if transcription.get('full_text') else '❌'}")
            print(f"   - overall_risk_score: {'✅' if call.get('overall_risk_score') is not None else '❌'}")
            print(f"   - keywords_found: {'❌' if 'keywords_found' not in call else '✅'}")
            print(f"   - scam_detected: {'✅' if call.get('scam_detected') is not None else '❌'}")
            
        else:
            print("❌ No calls found in database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_data_format()
