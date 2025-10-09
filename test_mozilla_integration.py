#!/usr/bin/env python3
"""
Test script to demonstrate Mozilla Voice integration with Complete Scam Detector
"""

from complete_scam_detector import CompleteScamDetector
import os

def test_integration():
    """Test the integrated Mozilla Voice analysis"""
    print("🧪 Testing Mozilla Voice Integration")
    print("=" * 50)
    
    # Initialize detector
    detector = CompleteScamDetector()
    
    # Test with existing audio file if available
    test_files = [
        "two_person_test.wav",
        "conversation.wav",
        "test_audio.wav"
    ]
    
    test_file = None
    for file in test_files:
        if os.path.exists(file):
            test_file = file
            break
    
    if not test_file:
        print("❌ No test audio file found. Please record some audio first.")
        print("💡 You can use: python complete_scam_detector.py")
        return
    
    print(f"🎵 Using test file: {test_file}")
    
    # Test 1: Original analysis
    print("\n📊 Test 1: Original Analysis")
    print("-" * 30)
    original_result = detector.analyze_conversation(test_file)
    
    if original_result['success']:
        print(f"✅ Original analysis successful")
        print(f"   Risk Level: {original_result['risk_level']}")
        print(f"   Risk Score: {original_result['overall_risk_score']:.2f}")
        print(f"   Scammers: {original_result['potential_scammers']}/{original_result['total_speakers']}")
    else:
        print(f"❌ Original analysis failed: {original_result['error']}")
        return
    
    # Test 2: Enhanced analysis with Mozilla Voice
    print("\n🎤 Test 2: Enhanced Analysis with Mozilla Voice")
    print("-" * 50)
    enhanced_result = detector.analyze_conversation_with_mozilla(test_file)
    
    if enhanced_result['success']:
        print(f"✅ Enhanced analysis successful")
        
        # Show combined risk score
        combined_risk = enhanced_result['combined_risk_score']
        print(f"   Combined Risk Level: {combined_risk['risk_level']}")
        print(f"   Combined Score: {combined_risk['combined_score']:.2f}")
        print(f"   Original Score: {combined_risk['existing_score']:.2f}")
        print(f"   Mozilla Score: {combined_risk['mozilla_score']:.2f}")
        
        # Show enhanced suggestions
        suggestions = enhanced_result['enhanced_suggestions']
        print(f"\n💡 Enhanced Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        # Show Mozilla Voice insights
        mozilla_insights = enhanced_result['mozilla_insights']
        if 'overall_assessment' in mozilla_insights:
            assessment = mozilla_insights['overall_assessment']
            print(f"\n🎤 Mozilla Voice Assessment:")
            print(f"   Assessment: {assessment.get('assessment', 'N/A')}")
            print(f"   Confidence: {assessment.get('confidence', 0):.2f}")
        
    else:
        print(f"❌ Enhanced analysis failed")
    
    print("\n🎯 Integration Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_integration()
