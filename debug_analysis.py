#!/usr/bin/env python3
"""
Debug script to test audio transcription and AI analysis
"""

import os
import sys
from complete_scam_detector import CompleteScamDetector

def debug_audio_analysis():
    """Debug the audio analysis pipeline"""
    print("🔍 DEBUGGING AUDIO ANALYSIS")
    print("=" * 50)
    
    # Initialize detector
    detector = CompleteScamDetector()
    
    # Check for test audio files
    test_files = [
        "two_person_test.wav",
        "conversation.wav", 
        "test_audio.wav",
        "recording.wav"
    ]
    
    test_file = None
    for file in test_files:
        if os.path.exists(file):
            test_file = file
            break
    
    if not test_file:
        print("❌ No test audio file found!")
        print("💡 Please record some audio first using your frontend")
        return
    
    print(f"🎵 Testing with file: {test_file}")
    
    # Step 1: Test transcription
    print("\n📝 STEP 1: Testing Transcription")
    print("-" * 30)
    
    transcription_result = detector.transcribe_with_diarization(test_file)
    
    if not transcription_result:
        print("❌ Transcription failed!")
        return
    
    print(f"✅ Transcription successful!")
    print(f"   Full text: {transcription_result['full_text']}")
    print(f"   Speakers: {len(transcription_result['speaker_text'])}")
    
    # Step 2: Test speaker analysis
    print("\n👥 STEP 2: Testing Speaker Analysis")
    print("-" * 30)
    
    analysis_results = detector.analyze_speakers(transcription_result)
    
    print(f"✅ Speaker analysis successful!")
    for speaker, result in analysis_results.items():
        print(f"   Speaker {speaker}: {result['risk_score']:.2f} risk")
        print(f"   Keywords: {', '.join(result['scam_keywords'][:5])}")
    
    # Step 3: Test Gemini AI
    print("\n🤖 STEP 3: Testing Gemini AI")
    print("-" * 30)
    
    if detector.gemini_model:
        print("✅ Gemini model available")
        
        # Test with actual transcribed text
        full_text = transcription_result['full_text']
        print(f"📝 Sending to Gemini: '{full_text[:100]}...'")
        
        gemini_response = detector.get_gemini_suggestion(
            full_text, 
            True,  # Assume scam detected for testing
            "high"
        )
        
        print(f"🤖 Gemini Response:")
        print(f"   {gemini_response}")
        
    else:
        print("❌ Gemini model not available")
        print("💡 Check your GEMINI_API_KEY in .env file")
    
    # Step 4: Test complete analysis
    print("\n🎯 STEP 4: Testing Complete Analysis")
    print("-" * 30)
    
    complete_result = detector.analyze_conversation(test_file)
    
    if complete_result['success']:
        print("✅ Complete analysis successful!")
        print(f"   Risk Level: {complete_result['risk_level']}")
        print(f"   Risk Score: {complete_result['overall_risk_score']:.2f}")
        print(f"   Gemini Suggestion: {complete_result['gemini_suggestion']}")
    else:
        print(f"❌ Complete analysis failed: {complete_result['error']}")
    
    print("\n🎯 DEBUG COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    debug_audio_analysis()
