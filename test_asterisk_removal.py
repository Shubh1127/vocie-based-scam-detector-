#!/usr/bin/env python3
"""
Test script to verify asterisk removal is working
"""

def test_asterisk_removal():
    """Test the asterisk removal functionality"""
    print("🧪 TESTING ASTERISK REMOVAL")
    print("=" * 40)
    
    # Test text with various asterisks
    test_text = """
    This is a **HIGH-RISK SCAM**. The initial assessment of "SAFE" and "No critical patterns detected" is incorrect. 
    
    1. **Analysis:** This is a classic "tech support scam." 
    2. **Red Flags:** 
       * **Unsolicited Contact:** Microsoft does not proactively monitor individual computers
       * **Alarmist Language:** Phrases like "multiple critical virus infections"
       * **Demand for Remote Access:** Stating they "will require remote access"
    
    3. **Actionable Advice:** Do not call the number provided.
    4. **What to do next:** Hang up immediately and block the number.
    """
    
    print("📝 ORIGINAL TEXT:")
    print("-" * 20)
    print(test_text)
    print("-" * 20)
    
    # Import the formatting function
    import sys
    sys.path.append('.')
    from complete_scam_detector import CompleteScamDetector
    
    detector = CompleteScamDetector()
    formatted_text = detector.format_gemini_response(test_text)
    
    print("\n✅ FORMATTED TEXT:")
    print("-" * 20)
    print(formatted_text)
    print("-" * 20)
    
    # Check if asterisks are removed
    asterisk_count = formatted_text.count('*')
    print(f"\n📊 RESULTS:")
    print(f"   Asterisks remaining: {asterisk_count}")
    
    if asterisk_count == 0:
        print("   ✅ SUCCESS: All asterisks removed!")
    else:
        print("   ❌ FAILED: Asterisks still present")
        print(f"   Remaining asterisks: {[i for i, char in enumerate(formatted_text) if char == '*']}")
    
    print("\n🎯 TEST COMPLETE!")
    print("=" * 40)

if __name__ == "__main__":
    test_asterisk_removal()
