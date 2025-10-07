import os
import io
import wave
import pyaudio
from google.cloud import speech
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class VoiceScamDetector:
    def __init__(self):
        """Initialize the voice scam detector with Google Cloud services"""
        # Check if credentials file exists
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './google-credentials.json')
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            print("💡 Please make sure you have:")
            print("   1. Downloaded the service account JSON file")
            print("   2. Renamed it to 'google-credentials.json'")
            print("   3. Placed it in the project folder")
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")
        
        print(f"✅ Using credentials file: {creds_path}")
        
        # Initialize Google Cloud Speech client
        self.speech_client = speech.SpeechClient()
        
        # Initialize Google Cloud Translate client
        self.translate_client = translate.Client()
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
    def transcribe_audio_file(self, audio_file_path):
        """
        Transcribe audio file with speaker diarization
        Returns: List of transcriptions with speaker labels
        """
        print(f"🎤 Processing audio file: {audio_file_path}")
        
        # Read audio file
        with io.open(audio_file_path, 'rb') as audio_file:
            content = audio_file.read()
        
        # Configure speech recognition with speaker diarization
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code='en-IN',  # English India
            enable_speaker_diarization=True,
            diarization_speaker_count=2,  # Expecting 2 speakers (caller + receiver)
            enable_automatic_punctuation=True,
            model='phone_call'  # Optimized for phone calls
        )
        
        audio = speech.RecognitionAudio(content=content)
        
        # Perform the transcription
        print("🔄 Sending to Google Speech-to-Text...")
        response = self.speech_client.recognize(config=config, audio=audio)
        
        # Process results
        results = []
        for result in response.results:
            alternative = result.alternatives[0]
            print(f"📝 Transcript: {alternative.transcript}")
            print(f"🎯 Confidence: {alternative.confidence:.2f}")
            
            # Extract speaker information
            for word_info in alternative.words:
                speaker_tag = word_info.speaker_tag
                word = word_info.word
                start_time = word_info.start_time.total_seconds()
                end_time = word_info.end_time.total_seconds()
                
                results.append({
                    'speaker': f"Speaker {speaker_tag}",
                    'word': word,
                    'start_time': start_time,
                    'end_time': end_time,
                    'confidence': alternative.confidence
                })
        
        return results
    
    def analyze_conversation(self, transcription_results):
        """
        Analyze conversation for scam indicators
        """
        print("\n🔍 Analyzing conversation for scam indicators...")
        
        # Group words by speaker
        caller_words = []
        receiver_words = []
        
        for result in transcription_results:
            if result['speaker'] == 'Speaker 1':
                caller_words.append(result['word'])
            else:
                receiver_words.append(result['word'])
        
        caller_text = ' '.join(caller_words)
        receiver_text = ' '.join(receiver_words)
        
        print(f"\n👤 Caller (Speaker 1): {caller_text}")
        print(f"👤 Receiver (Speaker 2): {receiver_text}")
        
        # Simple scam detection keywords
        scam_keywords = [
            'otp', 'password', 'pin', 'account', 'blocked', 'suspended',
            'urgent', 'immediately', 'verify', 'confirm', 'share', 'send',
            'bank', 'rbi', 'government', 'tax', 'refund', 'win', 'prize'
        ]
        
        caller_risk = self.check_scam_indicators(caller_text, scam_keywords)
        receiver_risk = self.check_scam_indicators(receiver_text, scam_keywords)
        
        return {
            'caller': {
                'text': caller_text,
                'risk_score': caller_risk['score'],
                'scam_phrases': caller_risk['phrases'],
                'is_scammer': caller_risk['score'] > 0.5
            },
            'receiver': {
                'text': receiver_text,
                'risk_score': receiver_risk['score'],
                'scam_phrases': receiver_risk['phrases'],
                'is_vulnerable': receiver_risk['score'] > 0.3
            }
        }
    
    def check_scam_indicators(self, text, keywords):
        """Check text for scam indicators"""
        text_lower = text.lower()
        found_phrases = []
        
        for keyword in keywords:
            if keyword in text_lower:
                found_phrases.append(keyword)
        
        # Calculate risk score (simple approach)
        risk_score = len(found_phrases) / len(keywords)
        
        return {
            'score': risk_score,
            'phrases': found_phrases
        }
    
    def print_analysis_results(self, analysis):
        """Print formatted analysis results"""
        print("\n" + "="*60)
        print("🚨 SCAM DETECTION ANALYSIS")
        print("="*60)
        
        caller = analysis['caller']
        receiver = analysis['receiver']
        
        print(f"\n👤 CALLER ANALYSIS:")
        print(f"   Risk Score: {caller['risk_score']:.2f}")
        print(f"   Scam Phrases: {', '.join(caller['scam_phrases']) if caller['scam_phrases'] else 'None'}")
        print(f"   Status: {'🚨 POTENTIAL SCAMMER' if caller['is_scammer'] else '✅ SAFE'}")
        
        print(f"\n👤 RECEIVER ANALYSIS:")
        print(f"   Risk Score: {receiver['risk_score']:.2f}")
        print(f"   Scam Phrases: {', '.join(receiver['scam_phrases']) if receiver['scam_phrases'] else 'None'}")
        print(f"   Status: {'⚠️ VULNERABLE' if receiver['is_vulnerable'] else '✅ SAFE'}")
        
        # Overall assessment
        if caller['is_scammer']:
            print(f"\n🚨 ALERT: This appears to be a SCAM CALL!")
            print(f"   Recommendation: Hang up immediately!")
        elif receiver['is_vulnerable']:
            print(f"\n⚠️ WARNING: Receiver may be vulnerable to scams")
            print(f"   Recommendation: Be cautious with personal information")
        else:
            print(f"\n✅ SAFE: No significant scam indicators detected")

def main():
    """Main function to test the voice scam detector"""
    print("🎤 Voice-Based Scam Detector")
    print("="*40)
    
    # Initialize detector
    detector = VoiceScamDetector()
    
    # Test with audio file (you'll need to provide a sample audio file)
    audio_file = "sample_call.wav"  # Replace with your audio file path
    
    if not os.path.exists(audio_file):
        print(f"❌ Audio file '{audio_file}' not found!")
        print("📝 Please provide a sample audio file to test with.")
        print("   You can record a test call or use any audio file.")
        return
    
    try:
        # Step 1: Transcribe audio with speaker diarization
        transcription_results = detector.transcribe_audio_file(audio_file)
        
        if not transcription_results:
            print("❌ No transcription results found!")
            return
        
        # Step 2: Analyze conversation
        analysis = detector.analyze_conversation(transcription_results)
        
        # Step 3: Print results
        detector.print_analysis_results(analysis)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have:")
        print("   1. Google Cloud credentials set up")
        print("   2. Required Python packages installed")
        print("   3. Valid audio file provided")

if __name__ == "__main__":
    main()
