import os
import io
import wave
import sounddevice as sd
import numpy as np
import time
from google.cloud import speech
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimulatedTwoPersonTest:
    def __init__(self):
        """Initialize simulated two-person test"""
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './google-credentials.json')
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")
        
        print(f"✅ Using credentials file: {creds_path}")
        self.speech_client = speech.SpeechClient()
        self.sample_rate = 16000
        self.channels = 1
        
    def create_simulated_conversation(self):
        """Create a simulated conversation for testing"""
        print("🎭 Creating simulated conversation for testing...")
        print("💡 This will help us test the scam detection logic.")
        
        # Simulated conversation data
        conversation_data = [
            {
                'speaker': 'Caller',
                'text': 'Hello sir, your bank account has been blocked due to suspicious activity.',
                'timestamp': 0.0,
                'is_scammer': True
            },
            {
                'speaker': 'Receiver', 
                'text': 'Oh no, what should I do?',
                'timestamp': 3.0,
                'is_scammer': False
            },
            {
                'speaker': 'Caller',
                'text': 'You need to share your OTP immediately to unblock your account.',
                'timestamp': 6.0,
                'is_scammer': True
            },
            {
                'speaker': 'Receiver',
                'text': 'Okay, my OTP is 123456.',
                'timestamp': 9.0,
                'is_scammer': False
            }
        ]
        
        return conversation_data
    
    def analyze_simulated_conversation(self, conversation_data):
        """Analyze the simulated conversation for scam indicators"""
        print("\n🔍 ANALYZING SIMULATED CONVERSATION:")
        print("=" * 60)
        
        scam_keywords = [
            'otp', 'password', 'pin', 'account', 'blocked', 'suspended',
            'urgent', 'immediately', 'verify', 'confirm', 'share', 'send',
            'bank', 'rbi', 'government', 'tax', 'refund', 'win', 'prize'
        ]
        
        caller_phrases = []
        receiver_phrases = []
        
        for message in conversation_data:
            text_lower = message['text'].lower()
            found_keywords = [kw for kw in scam_keywords if kw in text_lower]
            
            if message['speaker'] == 'Caller':
                caller_phrases.extend(found_keywords)
            else:
                receiver_phrases.extend(found_keywords)
        
        # Analyze caller (potential scammer)
        caller_risk_score = len(set(caller_phrases)) / len(scam_keywords)
        caller_is_scammer = caller_risk_score > 0.3
        
        # Analyze receiver (potential victim)
        receiver_risk_score = len(set(receiver_phrases)) / len(scam_keywords)
        receiver_is_vulnerable = receiver_risk_score > 0.1
        
        print(f"\n👤 CALLER ANALYSIS:")
        print(f"   Messages: {len([m for m in conversation_data if m['speaker'] == 'Caller'])}")
        print(f"   Scam Keywords Found: {', '.join(set(caller_phrases))}")
        print(f"   Risk Score: {caller_risk_score:.2f}")
        print(f"   Status: {'🚨 POTENTIAL SCAMMER' if caller_is_scammer else '✅ SAFE'}")
        
        print(f"\n👤 RECEIVER ANALYSIS:")
        print(f"   Messages: {len([m for m in conversation_data if m['speaker'] == 'Receiver'])}")
        print(f"   Scam Keywords Found: {', '.join(set(receiver_phrases))}")
        print(f"   Risk Score: {receiver_risk_score:.2f}")
        print(f"   Status: {'⚠️ VULNERABLE' if receiver_is_vulnerable else '✅ SAFE'}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if caller_is_scammer:
            print(f"🚨 ALERT: This is a SCAM CONVERSATION!")
            print(f"   Recommendation: Hang up immediately!")
            print(f"   Reason: Caller is asking for OTP and claiming account is blocked")
        elif receiver_is_vulnerable:
            print(f"⚠️ WARNING: Receiver may be vulnerable to scams")
            print(f"   Recommendation: Be cautious with personal information")
        else:
            print(f"✅ SAFE: No significant scam indicators detected")
        
        # Show conversation flow
        print(f"\n📝 CONVERSATION FLOW:")
        print("-" * 40)
        for message in conversation_data:
            speaker_icon = "👤" if message['speaker'] == 'Caller' else "👤"
            risk_icon = "🚨" if message['is_scammer'] else "✅"
            print(f"{speaker_icon} {message['speaker']} ({message['timestamp']:.1f}s): {message['text']} {risk_icon}")
        
        return {
            'caller_is_scammer': caller_is_scammer,
            'receiver_is_vulnerable': receiver_is_vulnerable,
            'caller_risk_score': caller_risk_score,
            'receiver_risk_score': receiver_risk_score
        }
    
    def run_simulated_test(self):
        """Run the simulated conversation test"""
        print("🎭 SIMULATED Two-Person Scam Detection Test")
        print("=" * 60)
        print("💡 This test uses simulated conversation data to test scam detection logic.")
        print("   No microphone recording needed - perfect for testing alone!")
        
        # Create simulated conversation
        conversation_data = self.create_simulated_conversation()
        
        # Analyze the conversation
        analysis = self.analyze_simulated_conversation(conversation_data)
        
        print(f"\n🎯 TEST RESULTS:")
        print(f"   Caller Scam Detection: {'✅ WORKING' if analysis['caller_is_scammer'] else '❌ FAILED'}")
        print(f"   Receiver Vulnerability: {'✅ WORKING' if analysis['receiver_is_vulnerable'] else '❌ FAILED'}")
        
        if analysis['caller_is_scammer']:
            print(f"\n🎉 SUCCESS: Scam detection is working correctly!")
            print(f"   The system correctly identified the caller as a potential scammer.")
        else:
            print(f"\n❌ FAILED: Scam detection needs improvement.")
            print(f"   The system should have identified the caller as a scammer.")

def main():
    """Main function"""
    try:
        tester = SimulatedTwoPersonTest()
        tester.run_simulated_test()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


