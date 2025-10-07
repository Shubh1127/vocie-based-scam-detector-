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

class DebugAudioTest:
    def __init__(self):
        """Initialize the debug audio test"""
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './google-credentials.json')
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")
        
        print(f"✅ Using credentials file: {creds_path}")
        self.speech_client = speech.SpeechClient()
        self.sample_rate = 16000
        self.channels = 1
        
    def test_microphone(self):
        """Test microphone with audio level check"""
        print("🎤 Testing microphone with audio level check...")
        
        try:
            # Record a short sample and check audio levels
            test_recording = sd.rec(int(2 * self.sample_rate), 
                                 samplerate=self.sample_rate, 
                                 channels=self.channels, 
                                 dtype=np.float32)
            
            print("📢 Say something now for 2 seconds...")
            sd.wait()
            
            # Check audio levels
            max_level = np.max(np.abs(test_recording))
            avg_level = np.mean(np.abs(test_recording))
            
            print(f"📊 Audio levels:")
            print(f"   Max level: {max_level:.4f}")
            print(f"   Average level: {avg_level:.4f}")
            
            if max_level > 0.01:
                print("✅ Microphone is picking up sound!")
                return True
            else:
                print("❌ Microphone is not picking up sound!")
                print("💡 Check:")
                print("   - Microphone permissions")
                print("   - Microphone volume")
                print("   - Speak louder")
                return False
                
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False
    
    def record_and_save(self, duration=5):
        """Record audio and save with detailed info"""
        print(f"🎙️ Recording for {duration} seconds...")
        print("📢 Speak clearly now!")
        
        recording = sd.rec(int(duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=self.channels, 
                          dtype=np.float32)
        
        # Show progress
        for i in range(duration):
            print(f"\r⏱️ Recording... {i+1}/{duration} seconds", end="", flush=True)
            time.sleep(1)
        
        print("\n✅ Recording complete!")
        sd.wait()
        
        # Check audio levels
        max_level = np.max(np.abs(recording))
        avg_level = np.mean(np.abs(recording))
        
        print(f"📊 Recorded audio levels:")
        print(f"   Max level: {max_level:.4f}")
        print(f"   Average level: {avg_level:.4f}")
        
        if max_level < 0.01:
            print("⚠️  WARNING: Very low audio levels detected!")
            print("   The audio might be too quiet for transcription.")
        
        # Save audio
        filename = "debug_test.wav"
        print(f"💾 Saving audio to {filename}...")
        
        # Convert to int16 for WAV file
        audio_data = (recording * 32767).astype(np.int16)
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(audio_data.tobytes())
        wf.close()
        
        print(f"✅ Audio saved to {filename}")
        
        # Check file size
        file_size = os.path.getsize(filename)
        print(f"📁 File size: {file_size} bytes")
        
        return filename, recording
    
    def test_simple_transcription(self, audio_file):
        """Test simple transcription without diarization"""
        print(f"🔄 Testing simple transcription of {audio_file}...")
        
        with io.open(audio_file, 'rb') as audio_file_obj:
            content = audio_file_obj.read()
        
        print(f"📊 Audio file size: {len(content)} bytes")
        
        # Simple configuration without diarization
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code='en-US',
            enable_automatic_punctuation=True
        )
        
        audio = speech.RecognitionAudio(content=content)
        
        try:
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                result = response.results[0]
                alternative = result.alternatives[0]
                
                print(f"✅ SUCCESS! Transcription found:")
                print(f"   Text: {alternative.transcript}")
                print(f"   Confidence: {alternative.confidence:.2f} ({alternative.confidence*100:.1f}%)")
                
                return True
            else:
                print("❌ No transcription results found!")
                return False
                
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return False
    
    def test_diarization(self, audio_file):
        """Test diarization only if simple transcription works"""
        print(f"🔄 Testing speaker diarization of {audio_file}...")
        
        with io.open(audio_file, 'rb') as audio_file_obj:
            content = audio_file_obj.read()
        
        # Configuration with diarization
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code='en-US',
            enable_automatic_punctuation=True
        )
        
        # Add diarization
        config.diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=1,
            max_speaker_count=3
        )
        
        audio = speech.RecognitionAudio(content=content)
        
        try:
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                result = response.results[0]
                alternative = result.alternatives[0]
                
                print(f"✅ Diarization results:")
                print(f"   Text: {alternative.transcript}")
                print(f"   Confidence: {alternative.confidence:.2f}")
                
                # Count speakers
                speakers = set()
                for word_info in alternative.words:
                    speakers.add(word_info.speaker_tag)
                
                print(f"   Speakers found: {len(speakers)} - {list(speakers)}")
                
                # Show speaker separation
                speaker_texts = {}
                for word_info in alternative.words:
                    speaker = word_info.speaker_tag
                    word = word_info.word
                    
                    if speaker not in speaker_texts:
                        speaker_texts[speaker] = []
                    speaker_texts[speaker].append(word)
                
                print(f"\n👥 Speaker separation:")
                for speaker in sorted(speaker_texts.keys()):
                    text = ' '.join(speaker_texts[speaker])
                    print(f"   Speaker {speaker}: {text}")
                
                return True
            else:
                print("❌ No diarization results found!")
                return False
                
        except Exception as e:
            print(f"❌ Diarization error: {e}")
            return False
    
    def run_debug_test(self):
        """Run the complete debug test"""
        print("🔍 DEBUG Audio Test")
        print("=" * 30)
        
        # Step 1: Test microphone with levels
        if not self.test_microphone():
            print("\n💡 Try:")
            print("   - Speaking louder")
            print("   - Moving closer to microphone")
            print("   - Checking microphone permissions")
            return
        
        # Step 2: Record and save
        audio_file, recording = self.record_and_save(duration=5)
        
        # Step 3: Test simple transcription first
        print(f"\n🧪 Step 1: Testing basic transcription...")
        if not self.test_simple_transcription(audio_file):
            print("\n❌ Basic transcription failed!")
            print("💡 The issue is with basic audio processing, not diarization.")
            print("   Check audio quality and microphone settings.")
            return
        
        # Step 4: Test diarization
        print(f"\n🧪 Step 2: Testing speaker diarization...")
        self.test_diarization(audio_file)
        
        # Cleanup
        keep_file = input("\n🗑️ Delete test audio file? (y/n): ").lower()
        if keep_file == 'y':
            os.remove(audio_file)
            print("✅ Audio file deleted")
        else:
            print(f"💾 Audio file kept: {audio_file}")

def main():
    """Main function"""
    try:
        tester = DebugAudioTest()
        tester.run_debug_test()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


