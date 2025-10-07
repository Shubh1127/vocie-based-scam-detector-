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

class TwoPersonVoiceTest:
    def __init__(self):
        """Initialize the two-person voice test with speaker diarization"""
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
        print("📢 Two people should speak now!")
        print("💡 Tips for Better Speaker Separation:")
        print("   - Speak one by one, minimal overlap")
        print("   - Different voice tones or pitches")
        print("   - Speak clearly and distinctly")
        
        recording = sd.rec(int(duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=self.channels, 
                          dtype=np.float32)
        
        for i in range(duration):
            print(f"\r⏱️ Recording... {i+1}/{duration} seconds", end="", flush=True)
            time.sleep(1)
        
        print("\n✅ Recording complete!")
        sd.wait()
        return recording
    
    def save_audio(self, recording, filename="two_person_test.wav"):
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
    
    def transcribe_with_diarization(self, audio_file):
        """Transcribe audio file with speaker diarization"""
        print(f"🔄 Transcribing {audio_file} with speaker diarization...")
        
        with io.open(audio_file, 'rb') as audio_file_obj:
            content = audio_file_obj.read()
        
        audio = speech.RecognitionAudio(content=content)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code='en-US',
            enable_automatic_punctuation=True,
            model='phone_call',
            diarization_config=speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=2,
                max_speaker_count=2
            )
        )
        
        response = self.speech_client.recognize(config=config, audio=audio)
        
        if not response.results:
            print("❌ No transcription results found!")
            return None
        
        # Combine all words across results
        words_info = []
        for result in response.results:
            words_info.extend(result.alternatives[0].words)
        
        # Group words by speaker
        speaker_text = {}
        for word_info in words_info:
            speaker_tag = word_info.speaker_tag
            word = word_info.word
            if speaker_tag not in speaker_text:
                speaker_text[speaker_tag] = []
            speaker_text[speaker_tag].append(word)
        
        # Print transcription per speaker
        print(f"\n👥 SPEAKER DIARIZATION RESULT:")
        print("=" * 50)
        for speaker_tag in sorted(speaker_text.keys()):
            text = ' '.join(speaker_text[speaker_tag])
            print(f"👤 Person {speaker_tag}: {text}")
        
        # Word-level timing
        print(f"\n⏰ WORD-LEVEL TIMING:")
        print("-" * 50)
        for word_info in words_info:
            print(f"Speaker {word_info.speaker_tag}: '{word_info.word}' "
                  f"({word_info.start_time.total_seconds():.1f}s - {word_info.end_time.total_seconds():.1f}s)")
        
        full_text = ' '.join([w.word for w in words_info])
        return {
            'full_text': full_text,
            'speaker_text': speaker_text,
            'words': words_info
        }
    
    def run_test(self):
        """Run the complete two-person test"""
        print("👥 Two-Person Voice Test with Speaker Diarization")
        print("=" * 60)
        
        if not self.test_microphone():
            return
        
        frames = self.record_audio(duration=15)
        audio_file = self.save_audio(frames)
        result = self.transcribe_with_diarization(audio_file)
        
        if result:
            print(f"\n🎯 SUCCESS! Speaker diarization completed!")
        else:
            print("\n❌ Speaker diarization failed!")
        
        keep_file = input("\n🗑️ Delete test audio file? (y/n): ").lower()
        if keep_file == 'y':
            os.remove(audio_file)
            print("✅ Audio file deleted")
        else:
            print(f"💾 Audio file kept: {audio_file}")

def main():
    try:
        tester = TwoPersonVoiceTest()
        tester.run_test()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Google Cloud credentials set up")
        print("   2. Required Python packages installed")
        print("   3. Microphone access enabled")

if __name__ == "__main__":
    main()
