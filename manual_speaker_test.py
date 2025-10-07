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

class ManualSpeakerTest:
    def __init__(self):
        """Initialize manual speaker test"""
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './google-credentials.json')
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")
        
        print(f"✅ Using credentials file: {creds_path}")
        self.speech_client = speech.SpeechClient()
        self.sample_rate = 16000
        self.channels = 1
        
    def record_separate_segments(self):
        """Record separate segments for each speaker"""
        print("🎙️ Recording separate segments for better speaker separation...")
        print("⚠️  IMPORTANT: You need TWO DIFFERENT PEOPLE to speak!")
        print("   If you're testing alone, this won't work properly.")
        
        segments = []
        
        # Record Person 1
        print("\n👤 PERSON 1: Speak now for 5 seconds...")
        print("   Say: 'Hello, this is Person 1 speaking'")
        print("   ⚠️  Make sure Person 1 is actually speaking!")
        
        recording1 = sd.rec(int(5 * self.sample_rate), 
                           samplerate=self.sample_rate, 
                           channels=self.channels, 
                           dtype=np.float32)
        
        for i in range(5):
            print(f"\r⏱️ Person 1... {i+1}/5 seconds", end="", flush=True)
            time.sleep(1)
        
        print("\n✅ Person 1 recording complete!")
        sd.wait()
        
        # Check if Person 1 actually spoke
        max_level1 = np.max(np.abs(recording1))
        print(f"📊 Person 1 audio level: {max_level1:.4f}")
        
        if max_level1 < 0.01:
            print("⚠️  WARNING: Person 1 audio level is very low!")
            print("   Make sure Person 1 is actually speaking!")
        
        segments.append(("Person 1", recording1))
        
        # Wait between recordings
        print("\n⏸️  Waiting 3 seconds...")
        time.sleep(3)
        
        # Record Person 2
        print("\n👤 PERSON 2: Speak now for 5 seconds...")
        print("   Say: 'Hi, this is Person 2 responding'")
        print("   ⚠️  Make sure Person 2 is actually speaking!")
        
        recording2 = sd.rec(int(5 * self.sample_rate), 
                           samplerate=self.sample_rate, 
                           channels=self.channels, 
                           dtype=np.float32)
        
        for i in range(5):
            print(f"\r⏱️ Person 2... {i+1}/5 seconds", end="", flush=True)
            time.sleep(1)
        
        print("\n✅ Person 2 recording complete!")
        sd.wait()
        
        # Check if Person 2 actually spoke
        max_level2 = np.max(np.abs(recording2))
        print(f"📊 Person 2 audio level: {max_level2:.4f}")
        
        if max_level2 < 0.01:
            print("⚠️  WARNING: Person 2 audio level is very low!")
            print("   Make sure Person 2 is actually speaking!")
        
        segments.append(("Person 2", recording2))
        
        return segments
    
    def combine_segments(self, segments):
        """Combine segments with silence between them"""
        print("🔗 Combining segments with silence...")
        
        # Create silence (0.5 seconds)
        silence_duration = 0.5
        silence = np.zeros(int(silence_duration * self.sample_rate), dtype=np.float32)
        
        # Ensure all arrays have the same shape
        segment1 = segments[0][1].flatten()  # Flatten to 1D
        segment2 = segments[1][1].flatten()  # Flatten to 1D
        
        # Combine segments
        combined = np.concatenate([segment1, silence, segment2])
        
        return combined
    
    def save_combined_audio(self, combined_audio, filename="combined_test.wav"):
        """Save combined audio to file"""
        print(f"💾 Saving combined audio to {filename}...")
        
        # Convert to int16 for WAV file
        audio_data = (combined_audio * 32767).astype(np.int16)
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(audio_data.tobytes())
        wf.close()
        
        print(f"✅ Combined audio saved to {filename}")
        return filename
    
    def transcribe_with_timing(self, audio_file):
        """Transcribe with detailed timing analysis"""
        print(f"🔄 Transcribing {audio_file} with timing analysis...")
        
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
                
                print(f"✅ Transcription results:")
                print(f"   Text: {alternative.transcript}")
                print(f"   Confidence: {alternative.confidence:.2f}")
                
                # Analyze timing to manually separate speakers
                print(f"\n⏰ TIMING ANALYSIS:")
                print("-" * 50)
                
                words = alternative.words
                speakers = set()
                
                for word_info in words:
                    speakers.add(word_info.speaker_tag)
                
                print(f"📊 Speakers detected by AI: {len(speakers)} - {list(speakers)}")
                
                # Manual separation based on timing
                print(f"\n👥 MANUAL SPEAKER SEPARATION:")
                print("-" * 50)
                
                # Group words by time periods
                first_half_words = []
                second_half_words = []
                
                total_duration = words[-1].end_time.total_seconds() if words else 0
                mid_point = total_duration / 2
                
                for word_info in words:
                    start_time = word_info.start_time.total_seconds()
                    if start_time < mid_point:
                        first_half_words.append(word_info.word)
                    else:
                        second_half_words.append(word_info.word)
                
                print(f"👤 Person 1 (0-{mid_point:.1f}s): {' '.join(first_half_words)}")
                print(f"👤 Person 2 ({mid_point:.1f}s-{total_duration:.1f}s): {' '.join(second_half_words)}")
                
                # Show word-level timing
                print(f"\n📝 WORD-LEVEL TIMING:")
                print("-" * 50)
                for word_info in words:
                    speaker = word_info.speaker_tag
                    word = word_info.word
                    start_time = word_info.start_time.total_seconds()
                    end_time = word_info.end_time.total_seconds()
                    print(f"   {start_time:.1f}s-{end_time:.1f}s: '{word}' (AI says Speaker {speaker})")
                
                return True
            else:
                print("❌ No transcription results found!")
                return False
                
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return False
    
    def run_test(self):
        """Run the manual speaker test"""
        print("👥 MANUAL Speaker Separation Test")
        print("=" * 50)
        print("💡 This test records each person separately, then combines them")
        print("   This should help with speaker diarization.")
        
        # Record separate segments
        segments = self.record_separate_segments()
        
        # Combine segments
        combined_audio = self.combine_segments(segments)
        
        # Save combined audio
        audio_file = self.save_combined_audio(combined_audio)
        
        # Transcribe with timing analysis
        self.transcribe_with_timing(audio_file)
        
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
        tester = ManualSpeakerTest()
        tester.run_test()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
