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

class TerminalVoiceTest:
    def __init__(self):
        """Initialize the terminal voice test"""
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
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        
    def test_microphone(self):
        """Test if microphone is accessible"""
        print("🎤 Testing microphone access...")
        
        try:
            # Test if we can record a short sample
            test_recording = sd.rec(int(0.1 * self.sample_rate), 
                                 samplerate=self.sample_rate, 
                                 channels=self.channels, 
                                 dtype=np.float32)
            sd.wait()  # Wait for recording to complete
            
            print("✅ Microphone access successful!")
            return True
            
        except Exception as e:
            print(f"❌ Microphone access failed: {e}")
            return False
    
    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        print(f"🎙️ Recording for {duration} seconds...")
        print("📢 Speak now!")
        
        # Record audio using sounddevice
        recording = sd.rec(int(duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=self.channels, 
                          dtype=np.float32)
        
        # Show progress
        for i in range(duration):
            print(f"\r⏱️ Recording... {i+1}/{duration} seconds", end="", flush=True)
            time.sleep(1)
        
        print("\n✅ Recording complete!")
        
        # Wait for recording to finish
        sd.wait()
        
        return recording
    
    def save_audio(self, recording, filename="test_recording.wav"):
        """Save recorded audio to file"""
        print(f"💾 Saving audio to {filename}...")
        
        # Convert float32 to int16 for WAV file
        audio_data = (recording * 32767).astype(np.int16)
        
        # Create WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(self.sample_rate)
        wf.writeframes(audio_data.tobytes())
        wf.close()
        
        print(f"✅ Audio saved to {filename}")
        return filename
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio file using Google STT"""
        print(f"🔄 Transcribing {audio_file}...")
        
        # Read audio file
        with io.open(audio_file, 'rb') as audio_file_obj:
            content = audio_file_obj.read()
        
        # Configure speech recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code='en-IN',  # English India
            enable_automatic_punctuation=True
        )
        
        audio = speech.RecognitionAudio(content=content)
        
        # Perform the transcription
        response = self.speech_client.recognize(config=config, audio=audio)
        
        # Process results
        if response.results:
            result = response.results[0]
            alternative = result.alternatives[0]
            
            print(f"\n📝 TRANSCRIPTION RESULT:")
            print(f"   Text: {alternative.transcript}")
            print(f"   Confidence: {alternative.confidence:.2f} ({alternative.confidence*100:.1f}%)")
            
            # Show confidence interpretation
            if alternative.confidence >= 0.8:
                print(f"   🟢 Excellent quality - Very clear speech")
            elif alternative.confidence >= 0.6:
                print(f"   🟡 Good quality - Clear speech")
            elif alternative.confidence >= 0.4:
                print(f"   🟠 Fair quality - Some background noise or unclear speech")
            else:
                print(f"   🔴 Poor quality - Very unclear or noisy audio")
            
            return alternative.transcript
        else:
            print("❌ No transcription results found!")
            return None
    
    def run_test(self):
        """Run the complete test"""
        print("🎤 Terminal Voice Test")
        print("=" * 40)
        
        # Step 1: Test microphone
        if not self.test_microphone():
            return
        
        # Step 2: Record audio
        frames = self.record_audio(duration=5)
        
        # Step 3: Save audio
        audio_file = self.save_audio(frames)
        
        # Step 4: Transcribe audio
        transcript = self.transcribe_audio(audio_file)
        
        if transcript:
            print(f"\n🎯 SUCCESS! Your speech was transcribed as:")
            print(f"   '{transcript}'")
        else:
            print("\n❌ Transcription failed!")
        
        # Cleanup (sounddevice doesn't need explicit cleanup)
        
        # Ask if user wants to keep the audio file
        keep_file = input("\n🗑️ Delete test audio file? (y/n): ").lower()
        if keep_file == 'y':
            os.remove(audio_file)
            print("✅ Audio file deleted")
        else:
            print(f"💾 Audio file kept: {audio_file}")

def main():
    """Main function"""
    try:
        tester = TerminalVoiceTest()
        tester.run_test()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Google Cloud credentials set up")
        print("   2. Required Python packages installed")
        print("   3. Microphone access enabled")

if __name__ == "__main__":
    main()
