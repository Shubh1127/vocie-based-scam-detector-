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

class ImprovedSpeakerTest:
    def __init__(self):
        """Initialize the improved speaker test"""
        # Check if credentials file exists
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './google-credentials.json')
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
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
            test_recording = sd.rec(int(0.1 * self.sample_rate), 
                                 samplerate=self.sample_rate, 
                                 channels=self.channels, 
                                 dtype=np.float32)
            sd.wait()
            print("✅ Microphone access successful!")
            return True
        except Exception as e:
            print(f"❌ Microphone access failed: {e}")
            return False
    
    def record_audio(self, duration=15):
        """Record audio for specified duration"""
        print(f"🎙️ Recording for {duration} seconds...")
        print("📢 CRITICAL: Follow these steps EXACTLY:")
        print("   1. Person 1: Say 'Hello, this is Person 1'")
        print("   2. WAIT 5 seconds (count: 1, 2, 3, 4, 5)")
        print("   3. Person 2: Say 'Hi, this is Person 2'")
        print("   4. WAIT 5 seconds")
        print("   5. Person 1: Say 'Goodbye Person 2'")
        print("   ⚠️  SPEAK FROM DIFFERENT SIDES OF THE MICROPHONE!")
        print("   ⚠️  USE DIFFERENT VOICE TONES!")
        
        recording = sd.rec(int(duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=self.channels, 
                          dtype=np.float32)
        
        # Show progress with timing cues
        for i in range(duration):
            if i < 5:
                print(f"\r⏱️ Recording... {i+1}/{duration} seconds - Person 1 should speak NOW!", end="", flush=True)
            elif i < 10:
                print(f"\r⏱️ Recording... {i+1}/{duration} seconds - Person 2 should speak NOW!", end="", flush=True)
            else:
                print(f"\r⏱️ Recording... {i+1}/{duration} seconds - Person 1 should speak NOW!", end="", flush=True)
            time.sleep(1)
        
        print("\n✅ Recording complete!")
        sd.wait()
        return recording
    
    def save_audio(self, recording, filename="improved_test.wav"):
        """Save recorded audio to file"""
        print(f"💾 Saving audio to {filename}...")
        
        audio_data = (recording * 32767).astype(np.int16)
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(audio_data.tobytes())
        wf.close()
        
        print(f"✅ Audio saved to {filename}")
        return filename
    
    def transcribe_with_multiple_configs(self, audio_file):
        """Try different configurations to improve speaker diarization"""
        print(f"🔄 Transcribing {audio_file} with multiple configurations...")
        
        with io.open(audio_file, 'rb') as audio_file_obj:
            content = audio_file_obj.read()
        
        audio = speech.RecognitionAudio(content=content)
        
        # Try different configurations
        configs = [
            {
                'name': 'Configuration 1: Default + Diarization',
                'config': speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.sample_rate,
                    language_code='en-US',
                    enable_automatic_punctuation=True
                )
            },
            {
                'name': 'Configuration 2: Phone Call Model',
                'config': speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.sample_rate,
                    language_code='en-US',
                    enable_automatic_punctuation=True,
                    model='phone_call'
                )
            },
            {
                'name': 'Configuration 3: Latest Long Model',
                'config': speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.sample_rate,
                    language_code='en-US',
                    enable_automatic_punctuation=True,
                    model='latest_long'
                )
            }
        ]
        
        # Add diarization config to each
        for config_info in configs:
            config_info['config'].diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=1,
                max_speaker_count=4
            )
        
        best_result = None
        best_speaker_count = 0
        
        for config_info in configs:
            print(f"\n🧪 Testing {config_info['name']}...")
            
            try:
                response = self.speech_client.recognize(config=config_info['config'], audio=audio)
                
                if response.results:
                    result = response.results[0]
                    alternative = result.alternatives[0]
                    
                    # Count unique speakers
                    speakers = set()
                    for word_info in alternative.words:
                        speakers.add(word_info.speaker_tag)
                    
                    speaker_count = len(speakers)
                    print(f"   📊 Found {speaker_count} speakers: {list(speakers)}")
                    print(f"   📝 Text: {alternative.transcript}")
                    print(f"   🎯 Confidence: {alternative.confidence:.2f}")
                    
                    # Keep the best result (most speakers)
                    if speaker_count > best_speaker_count:
                        best_speaker_count = speaker_count
                        best_result = {
                            'config_name': config_info['name'],
                            'transcript': alternative.transcript,
                            'confidence': alternative.confidence,
                            'words': alternative.words,
                            'speakers': speakers
                        }
                else:
                    print("   ❌ No results")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return best_result
    
    def analyze_best_result(self, result):
        """Analyze the best result and show speaker separation"""
        if not result:
            print("❌ No successful transcription found!")
            return
        
        print(f"\n🏆 BEST RESULT: {result['config_name']}")
        print("=" * 60)
        print(f"📝 Full Text: {result['transcript']}")
        print(f"🎯 Confidence: {result['confidence']:.2f} ({result['confidence']*100:.1f}%)")
        print(f"👥 Speakers Found: {len(result['speakers'])}")
        
        # Group words by speaker
        speaker_texts = {}
        for word_info in result['words']:
            speaker = word_info.speaker_tag
            word = word_info.word
            
            if speaker not in speaker_texts:
                speaker_texts[speaker] = []
            speaker_texts[speaker].append(word)
        
        # Display results
        print(f"\n👥 SPEAKER SEPARATION:")
        print("-" * 40)
        for speaker in sorted(speaker_texts.keys()):
            text = ' '.join(speaker_texts[speaker])
            print(f"👤 Speaker {speaker}: {text}")
        
        # Show word-level timing
        print(f"\n⏰ WORD-LEVEL TIMING:")
        print("-" * 40)
        for word_info in result['words']:
            speaker = word_info.speaker_tag
            word = word_info.word
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()
            print(f"   Speaker {speaker}: '{word}' ({start_time:.1f}s - {end_time:.1f}s)")
    
    def run_test(self):
        """Run the complete improved test"""
        print("👥 IMPROVED Two-Person Voice Test")
        print("=" * 50)
        
        if not self.test_microphone():
            return
        
        frames = self.record_audio(duration=15)
        audio_file = self.save_audio(frames)
        
        result = self.transcribe_with_multiple_configs(audio_file)
        self.analyze_best_result(result)
        
        keep_file = input("\n🗑️ Delete test audio file? (y/n): ").lower()
        if keep_file == 'y':
            os.remove(audio_file)
            print("✅ Audio file deleted")
        else:
            print(f"💾 Audio file kept: {audio_file}")

def main():
    """Main function"""
    try:
        tester = ImprovedSpeakerTest()
        tester.run_test()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


