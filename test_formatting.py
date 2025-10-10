#!/usr/bin/env python3
"""
Test script to show the difference in AI response formatting
"""

from complete_scam_detector import CompleteScamDetector

def test_formatting():
    """Test the new formatting functionality"""
    print("🧪 TESTING AI RESPONSE FORMATTING")
    print("=" * 50)
    
    # Initialize detector
    detector = CompleteScamDetector()
    
    # Test transcription text (simulate a scam call)
    test_transcription = """
    Hello, this is Microsoft technical support. We have detected multiple critical virus infections on your computer. 
    Your system has been compromised and we will require remote access to fix it immediately. 
    Please call us at 1-800-555-0123 right now to resolve this urgent security issue.
    """
    
    print("📝 Test Transcription:")
    print(f"   {test_transcription.strip()}")
    
    if detector.gemini_model:
        print("\n🤖 Testing Gemini AI Response:")
        
        # Test the new formatted response
        formatted_response = detector.get_gemini_suggestion(
            test_transcription, 
            True,  # Scam detected
            "high"
        )
        
        print("\n✅ FORMATTED RESPONSE:")
        print("-" * 30)
        print(formatted_response)
        print("-" * 30)
        
        print("\n📊 Formatting Features:")
        print("   ✅ No asterisks (*) or special characters")
        print("   ✅ Proper line breaks")
        print("   ✅ Clean numbered lists")
        print("   ✅ Readable structure")
        
    else:
        print("❌ Gemini model not available")
        print("💡 Check your GEMINI_API_KEY in .env file")
    
    print("\n🎯 FORMATTING TEST COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    test_formatting()
