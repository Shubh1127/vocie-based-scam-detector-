#!/usr/bin/env python3
"""
Test script for bank analysis functionality
"""

import sys
sys.path.append('.')

from complete_scam_detector import CompleteScamDetector

def test_bank_analysis():
    """Test bank analysis functionality"""
    print("🏦 TESTING BANK ANALYSIS")
    print("=" * 40)
    
    # Initialize scam detector
    scam_detector = CompleteScamDetector()
    
    # Test bank-related content detection
    test_transcriptions = [
        {
            "text": "Hello, this is your bank calling about your account. We need to verify your PIN number for security purposes.",
            "keywords": ["bank", "account", "pin", "verify"]
        },
        {
            "text": "Hi, I'm calling about your credit card payment. Can you please provide your card details?",
            "keywords": ["credit card", "payment", "card details"]
        },
        {
            "text": "Hello, this is a regular phone call about the weather today.",
            "keywords": ["weather"]
        },
        {
            "text": "Your account has been compromised. Please transfer all your money to this secure account immediately.",
            "keywords": ["account", "compromised", "transfer", "money"]
        }
    ]
    
    for i, test in enumerate(test_transcriptions, 1):
        print(f"\n🧪 Test {i}: {test['text'][:50]}...")
        
        # Test bank detection
        bank_analysis = scam_detector.detect_bank_related_content(
            test['text'], 
            test['keywords']
        )
        
        print(f"   Bank Related: {bank_analysis['is_bank_related']}")
        print(f"   Keywords Detected: {bank_analysis['bank_keywords_detected']}")
        print(f"   Confidence: {bank_analysis['confidence']:.2f}")
        
        # Test bank rules generation if bank-related
        if bank_analysis['is_bank_related']:
            print("   🏦 Generating bank rules...")
            try:
                bank_rules = scam_detector.get_bank_rules_from_gemini(
                    test['text'],
                    bank_analysis['bank_keywords_detected']
                )
                print(f"   ✅ Bank rules generated ({len(bank_rules)} characters)")
                print(f"   📋 Preview: {bank_rules[:100]}...")
            except Exception as e:
                print(f"   ❌ Error generating bank rules: {e}")
        else:
            print("   ℹ️ No bank rules needed")
    
    print(f"\n🎯 BANK ANALYSIS TEST COMPLETE!")
    print("=" * 40)

if __name__ == "__main__":
    test_bank_analysis()
