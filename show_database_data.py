#!/usr/bin/env python3
"""
Simple script to show what's actually in the database
"""

import sys
sys.path.append('.')

from analyzed_call_model import analyzed_call_model
import json

def show_database_data():
    """Show what's actually stored in the database"""
    print("🗄️ DATABASE DATA INSPECTION")
    print("=" * 50)
    
    try:
        # Get all calls from database
        calls = analyzed_call_model.get_analyzed_calls(None, 10, 0)
        print(f"📊 Total calls in database: {len(calls)}")
        
        if calls:
            print(f"\n📋 Sample call data:")
            print("-" * 30)
            
            for i, call in enumerate(calls[:3]):  # Show first 3 calls
                print(f"\n🔍 Call #{i+1}:")
                print(f"   ID: {call.get('_id')}")
                print(f"   Timestamp: {call.get('timestamp')}")
                print(f"   Caller: {call.get('caller')}")
                print(f"   Probability: {call.get('probability')}")
                print(f"   Keywords: {call.get('keywords')}")
                print(f"   Keywords Found: {call.get('keywords_found')}")
                print(f"   Scam Detected: {call.get('scam_detected')}")
                print(f"   Overall Risk Score: {call.get('overall_risk_score')}")
                print(f"   Outcome: {call.get('outcome')}")
                print(f"   Risk Level: {call.get('risk_level')}")
                
                # Show transcription
                transcription = call.get('transcription', {})
                if isinstance(transcription, dict):
                    print(f"   Transcription Keys: {list(transcription.keys())}")
                    print(f"   Full Text: {transcription.get('full_text', 'NOT FOUND')[:100]}...")
                else:
                    print(f"   Transcription: {transcription}")
                
                print(f"   Call Summary: {call.get('call_summary', 'NOT FOUND')[:100]}...")
                print("-" * 30)
            
            print(f"\n🎯 FRONTEND EXPECTS:")
            print(f"   - c.transcription?.full_text")
            print(f"   - c.keywords_found")
            print(f"   - c.scam_detected")
            print(f"   - c.overall_risk_score")
            
            print(f"\n✅ WHAT WE HAVE:")
            sample_call = calls[0]
            transcription = sample_call.get('transcription', {})
            print(f"   - transcription.full_text: {'✅' if transcription.get('full_text') else '❌'}")
            print(f"   - keywords_found: {'✅' if sample_call.get('keywords_found') else '❌'}")
            print(f"   - scam_detected: {'✅' if sample_call.get('scam_detected') is not None else '❌'}")
            print(f"   - overall_risk_score: {'✅' if sample_call.get('overall_risk_score') is not None else '❌'}")
            
        else:
            print("❌ No calls found in database!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    show_database_data()
