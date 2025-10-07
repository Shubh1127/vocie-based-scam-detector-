import os
import io
import wave
import sounddevice as sd
import numpy as np
import time
from google.cloud import speech
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class CompleteScamDetector:
    def __init__(self):
        """Initialize the complete scam detector"""
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './google-credentials.json')
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")
        
        print(f"✅ Using credentials file: {creds_path}")
        self.speech_client = speech.SpeechClient()
        self.sample_rate = 16000  # Use 16kHz like working two_person_test.py
        self.channels = 1
        
        # Initialize Gemini AI
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI initialized successfully")
        else:
            self.gemini_model = None
            print("⚠️ Gemini API key not found - AI suggestions disabled")
        
        # Scam detection keywords (expanded and improved) - Multi-language support
        self.scam_keywords = [
            # English keywords
            'otp', 'password', 'pin', 'account', 'blocked', 'suspended',
            'urgent', 'immediately', 'verify', 'confirm', 'share', 'send',
            'bank', 'rbi', 'government', 'tax', 'refund', 'win', 'prize',
            'suspicious', 'fraud', 'security', 'update', 'reactivate',
            'debit', 'credit', 'card', 'number', 'cvv', 'expiry',
            'say', 'tell', 'give', 'provide', 'enter', 'input', 'type',
            'code', 'verification', 'authenticate', 'unlock', 'unblock',
            'reactivate', 'restore', 'access', 'login', 'credentials',
            'pay', 'payment', 'money', 'transfer', 'deposit', 'send',
            'fees', 'charges', 'penalty', 'fine', 'amount', 'cost',
            'reactivate', 'activate', 'restore', 'unlock', 'unblock',
            
            # Hindi keywords
            'ओटीपी', 'पासवर्ड', 'पिन', 'खाता', 'ब्लॉक', 'रोका', 'तत्काल',
            'जल्दी', 'सत्यापन', 'पुष्टि', 'साझा', 'भेजें', 'बैंक', 'सरकार',
            'कर', 'रिफंड', 'जीत', 'पुरस्कार', 'संदिग्ध', 'धोखाधड़ी', 'सुरक्षा',
            'अपडेट', 'पुनः सक्रिय', 'डेबिट', 'क्रेडिट', 'कार्ड', 'नंबर',
            'कहें', 'बताएं', 'दें', 'प्रदान', 'दर्ज', 'इनपुट', 'टाइप',
            'कोड', 'सत्यापन', 'प्रमाणीकरण', 'अनलॉक', 'अनब्लॉक',
            'पुनः सक्रिय', 'पुनर्स्थापित', 'पहुंच', 'लॉगिन', 'क्रेडेंशियल'
        ]
        
        # High-risk phrases that indicate immediate danger - Multi-language
        self.high_risk_phrases = [
            # English phrases
            'say your otp', 'tell your otp', 'give your otp', 'share your otp',
            'provide your otp', 'enter your otp', 'type your otp', 'your otp',
            'say your password', 'tell your password', 'give your password',
            'share your pin', 'tell your pin', 'give your pin',
            'bank account blocked', 'account suspended', 'urgent verification',
            'immediate action', 'suspicious activity', 'fraud detected',
            
            # Payment/Unblocking Scams
            'pay us money to unblock', 'pay money to unblock account',
            'send money to unblock', 'transfer money to unblock',
            'deposit money to unblock', 'pay fees to unblock',
            'pay charges to unblock', 'pay penalty to unblock',
            'pay fine to unblock', 'pay amount to unblock',
            'send payment to unblock', 'make payment to unblock',
            'pay to reactivate', 'pay to restore', 'pay to unlock',
            'pay to activate', 'pay to verify', 'pay to confirm',
            
            # Bank Impersonation Scams
            'i am from the bank', 'we are from the bank', 'bank calling',
            'bank representative', 'bank official', 'bank employee',
            'give us money', 'send us money', 'transfer money to us',
            'deposit money to us', 'pay us', 'send payment to us',
            'bank asking for money', 'bank wants money', 'bank needs money',
            
            # Hindi phrases
            'अपना ओटीपी बताएं', 'ओटीपी साझा करें', 'ओटीपी दें', 'ओटीपी कहें',
            'अपना पासवर्ड बताएं', 'पासवर्ड साझा करें', 'पासवर्ड दें',
            'अपना पिन बताएं', 'पिन साझा करें', 'पिन दें',
            'बैंक खाता ब्लॉक', 'खाता रोका गया', 'तत्काल सत्यापन',
            'तत्काल कार्रवाई', 'संदिग्ध गतिविधि', 'धोखाधड़ी का पता चला',
            
            # Hindi Payment Scams
            'पैसे भेजकर अनब्लॉक करें', 'रुपए भेजकर खाता खोलें',
            'पैसे देकर अनब्लॉक करें', 'रुपए देकर खाता सक्रिय करें',
            'पैसे ट्रांसफर करके अनब्लॉक करें', 'रुपए भेजकर सक्रिय करें',
            
            # Hindi Bank Impersonation
            'मैं बैंक से हूं', 'हम बैंक से हैं', 'बैंक का कॉल',
            'बैंक प्रतिनिधि', 'बैंक अधिकारी', 'बैंक कर्मचारी',
            'हमें पैसे दें', 'हमें रुपए भेजें', 'हमें पैसे ट्रांसफर करें'
        ]
        
    def test_microphone(self):
        """Test microphone access"""
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
    
    def record_conversation(self, duration=15):
        """Record a conversation for analysis"""
        print(f"🎙️ Recording conversation for {duration} seconds...")
        print("📢 Multiple people should speak now!")
        print("💡 Tips for better detection:")
        print("   - Speak clearly and distinctly")
        print("   - Take turns speaking")
        print("   - Include scam-related words if testing scam detection")
        
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
        
        return recording
    
    def save_audio(self, recording, filename="conversation.wav"):
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
        """Transcribe audio file with speaker diarization (using working code from two_person_test.py)"""
        print(f"🔄 Transcribing {audio_file} with speaker diarization...")
        
        with io.open(audio_file, 'rb') as audio_file_obj:
            content = audio_file_obj.read()
        
        audio = speech.RecognitionAudio(content=content)
        
        # Try multiple configurations for better mixed language support and long audio handling
        configs = [
            # English primary with diarization - using LINEAR16 like working two_person_test.py
            speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,  # Use 16kHz like working version
                language_code='en-US',
                enable_automatic_punctuation=True,
                model='phone_call',
                diarization_config=speech.SpeakerDiarizationConfig(
                    enable_speaker_diarization=True,
                    min_speaker_count=2,
                    max_speaker_count=2
                )
            )
        ]
        
        best_response = None
        best_confidence = 0
        
        # Try both configurations and pick the best one
        for i, config in enumerate(configs):
            try:
                print(f"🔄 Trying configuration {i+1}: {config.language_code} primary...")
                print(f"📊 Audio file size: {len(content)} bytes")
                print(f"⏱️  Estimated duration: {len(content) / (self.sample_rate * 2):.2f} seconds")
                
                response = self.speech_client.recognize(config=config, audio=audio)
                
                if response.results:
                    # Calculate average confidence
                    total_confidence = 0
                    total_alternatives = 0
                    for result in response.results:
                        for alternative in result.alternatives:
                            total_confidence += alternative.confidence
                            total_alternatives += 1
                    
                    avg_confidence = total_confidence / total_alternatives if total_alternatives > 0 else 0
                    print(f"📊 Configuration {i+1} confidence: {avg_confidence:.2f}")
                    
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_response = response
                        print(f"✅ Configuration {i+1} selected!")
                        
            except Exception as e:
                print(f"❌ Configuration {i+1} failed: {e}")
                continue
        
        if not best_response:
            print("❌ All transcription configurations failed!")
            return None
            
        print(f"✅ Best configuration selected with confidence: {best_confidence:.2f}")
        response = best_response
        
        try:
            if not response.results:
                print("❌ No transcription results found!")
                return None
            
            # Combine all words across results (from two_person_test.py)
            words_info = []
            for result in response.results:
                words_info.extend(result.alternatives[0].words)
            
            # Convert Google Cloud objects to serializable dictionaries
            serializable_words = []
            for word_info in words_info:
                serializable_words.append({
                    'word': word_info.word,
                    'speaker_tag': word_info.speaker_tag,
                    'start_time': word_info.start_time.total_seconds(),
                    'end_time': word_info.end_time.total_seconds()
                })
            
            # Group words by speaker (from two_person_test.py)
            speaker_text = {}
            for word_info in words_info:
                speaker_tag = word_info.speaker_tag
                word = word_info.word
                if speaker_tag not in speaker_text:
                    speaker_text[speaker_tag] = []
                speaker_text[speaker_tag].append(word)
            
            # Print transcription per speaker (from two_person_test.py)
            print(f"\n👥 SPEAKER DIARIZATION RESULT:")
            print("=" * 50)
            for speaker_tag in sorted(speaker_text.keys()):
                text = ' '.join(speaker_text[speaker_tag])
                print(f"👤 Person {speaker_tag}: {text}")
            
            # Word-level timing (from two_person_test.py)
            print(f"\n⏰ WORD-LEVEL TIMING:")
            print("-" * 50)
            for word_info in words_info:
                print(f"Speaker {word_info.speaker_tag}: '{word_info.word}' "
                      f"({word_info.start_time.total_seconds():.1f}s - {word_info.end_time.total_seconds():.1f}s)")
            
            # Build full text
            full_text = ' '.join([w.word for w in words_info])
            
            # Post-process to improve mixed language handling
            full_text = self.improve_mixed_language_text(full_text)
            
            # Update speaker text with improved text
            for speaker_tag in speaker_text:
                speaker_text[speaker_tag] = self.improve_mixed_language_text(' '.join(speaker_text[speaker_tag])).split()
            
            print(f"\n✅ Transcription successful!")
            print(f"   Full Text: {full_text}")
            print(f"   Speakers Detected: {len(speaker_text)}")
            
            return {
                'full_text': full_text,
                'speaker_text': speaker_text,
                'words': serializable_words
            }
                
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def improve_mixed_language_text(self, text):
        """Improve mixed language text by converting common Hindi-transcribed English words back to English"""
        # Common English words that get transcribed in Hindi script
        hindi_to_english = {
            'आई': 'I',
            'एम': 'am',
            'गोइंग': 'going',
            'टू': 'to',
            'एमिटी': 'Amity',
            'नोएडा': 'Noida',
            'है': 'is',
            'और': 'and',
            'मेरा': 'my',
            'नाम': 'name',
            'रोहन': 'Rohan',
            'हैं': 'are',
            'हूं': 'am',
            'हैं': 'are',
            'है': 'is',
            'का': 'of',
            'की': 'of',
            'के': 'of',
            'को': 'to',
            'से': 'from',
            'में': 'in',
            'पर': 'on',
            'तक': 'until',
            'तो': 'so',
            'लेकिन': 'but',
            'या': 'or',
            'अगर': 'if',
            'जब': 'when',
            'कहां': 'where',
            'कैसे': 'how',
            'क्यों': 'why',
            'क्या': 'what',
            'कौन': 'who',
            'कितना': 'how much',
            'कितने': 'how many'
        }
        
        # Split text into words and convert
        words = text.split()
        improved_words = []
        
        for word in words:
            # Remove punctuation for comparison
            clean_word = word.strip('.,!?;:')
            
            # Check if it's a Hindi-transcribed English word
            if clean_word in hindi_to_english:
                # Replace with English, keeping original punctuation
                english_word = hindi_to_english[clean_word]
                if word != clean_word:  # Has punctuation
                    english_word += word[len(clean_word):]
                improved_words.append(english_word)
            else:
                improved_words.append(word)
        
        return ' '.join(improved_words)
    
    def analyze_conversation_logic(self, transcription_text):
        """Enhanced logic-based scam detection"""
        text_lower = transcription_text.lower()
        
        # Critical scam patterns that override everything else
        critical_scam_patterns = [
            # Money transfer scams
            'send us money', 'transfer money to us', 'pay us money',
            'send payment to us', 'give us money', 'deposit money to us',
            'send us rupees', 'transfer rupees to us', 'pay us rupees',
            'send us lakh', 'transfer lakh to us', 'pay us lakh',
            
            # Bank impersonation with money demands
            'bank asking for money', 'bank wants money', 'bank needs money',
            'we are from bank and need money', 'bank requesting money',
            'send money to bank', 'transfer money to bank',
            
            # Account unblocking scams
            'pay money to unblock', 'send money to unblock',
            'transfer money to unblock', 'deposit money to unblock',
            'pay to unblock account', 'send to unblock account',
            'money to unblock', 'payment to unblock',
            
            # Urgent payment demands
            'immediate payment', 'urgent payment', 'send immediately',
            'transfer immediately', 'pay now', 'send now',
            'immediate transfer', 'urgent transfer'
        ]
        
        # Check for critical scam patterns
        for pattern in critical_scam_patterns:
            if pattern in text_lower:
                return True, f"CRITICAL SCAM PATTERN DETECTED: '{pattern}'"
        
        # Check for bank impersonation + money combination
        bank_impersonation = any(phrase in text_lower for phrase in [
            'i am from bank', 'we are from bank', 'bank calling',
            'bank representative', 'bank official', 'bank employee'
        ])
        
        money_demand = any(phrase in text_lower for phrase in [
            'send money', 'transfer money', 'pay money', 'give money',
            'send rupees', 'transfer rupees', 'pay rupees', 'give rupees',
            'send payment', 'transfer payment', 'pay payment'
        ])
        
        if bank_impersonation and money_demand:
            return True, "BANK IMPERSONATION + MONEY DEMAND SCAM"
        
        return False, "No critical scam patterns detected"
    
    def get_gemini_suggestion(self, transcription_text, scam_detected, risk_level):
        """Get AI-powered suggestions from Gemini"""
        if not self.gemini_model:
            return "AI suggestions not available - Gemini API key not configured"
        
        try:
            # Run logic-based analysis to get more accurate scam detection
            logic_scam_detected, logic_reason = self.analyze_conversation_logic(transcription_text)
            
            # Use logic-based detection if it found a scam, otherwise use the provided scam_detected
            final_scam_detected = logic_scam_detected or scam_detected
            
            prompt = f"""
            Analyze this phone conversation transcript for scam detection:

            CONVERSATION: "{transcription_text}"

            SCAM STATUS: {"SCAM DETECTED" if final_scam_detected else "SAFE"}
            RISK LEVEL: {risk_level.upper()}
            LOGIC ANALYSIS: {logic_reason if logic_scam_detected else "No critical patterns detected"}

            Please provide:
            1. A brief analysis of why this is/isn't a scam
            2. Specific red flags or safe indicators
            3. Actionable advice for the person receiving the call
            4. What they should do next

            Keep response concise (under 200 words) and practical.
            """
            
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Gemini AI error: {e}")
            return "AI analysis temporarily unavailable"
    
    def analyze_speakers(self, transcription_result):
        """Analyze each speaker for scam indicators (using data from working diarization)"""
        print(f"\n🔍 ANALYZING SPEAKERS FOR SCAM INDICATORS:")
        print("=" * 60)
        
        # Extract data from transcription result
        speaker_text = transcription_result['speaker_text']
        words_info = transcription_result['words']
        full_text = transcription_result['full_text']
        
        # First, run enhanced logic-based analysis on the full conversation
        print("🧠 Running enhanced logic-based scam detection...")
        logic_scam_detected, logic_reason = self.analyze_conversation_logic(full_text)
        
        if logic_scam_detected:
            print(f"🚨 CRITICAL SCAM DETECTED BY LOGIC: {logic_reason}")
        
        # Check if we have speaker diarization data
        has_diarization = any(word.get('speaker_tag') is not None for word in words_info)
        
        if not has_diarization:
            print("⚠️  No speaker diarization data available - treating as single speaker")
            # Create a single speaker entry
            speaker_text = {'0': [word['word'] for word in words_info]}
            # Update words_info to have speaker_tag
            for word in words_info:
                word['speaker_tag'] = 0
        
        # Group words by speaker for analysis
        speaker_data = {}
        
        for word_info in words_info:
            speaker = word_info['speaker_tag']
            word = word_info['word'].lower()
            start_time = word_info['start_time']
            
            if speaker not in speaker_data:
                speaker_data[speaker] = {
                    'words': [],
                    'timestamps': [],
                    'scam_keywords': [],
                    'text': ''
                }
            
            speaker_data[speaker]['words'].append(word)
            speaker_data[speaker]['timestamps'].append(start_time)
            
            # Check for scam keywords
            if word in self.scam_keywords:
                speaker_data[speaker]['scam_keywords'].append(word)
        
        # Check for high-risk phrases (more comprehensive detection)
        for speaker in speaker_data:
            text_lower = ' '.join(speaker_data[speaker]['words']).lower()
            for phrase in self.high_risk_phrases:
                if phrase in text_lower:
                    speaker_data[speaker]['scam_keywords'].append(f"[PHRASE: {phrase}]")
        
        # Build text for each speaker
        for speaker in speaker_data:
            speaker_data[speaker]['text'] = ' '.join(speaker_data[speaker]['words'])
        
        # Analyze each speaker
        analysis_results = {}
        
        for speaker, data in speaker_data.items():
            text = data['text']
            scam_keywords_found = data['scam_keywords']
            
            # Calculate risk score
            unique_scam_keywords = len(set(scam_keywords_found))
            risk_score = unique_scam_keywords / len(self.scam_keywords)
            
            # Override risk score if logic-based detection found a scam
            if logic_scam_detected:
                risk_score = max(risk_score, 0.9)  # Ensure high risk score
            
            # Determine if speaker is potential scammer (improved logic)
            is_potential_scammer = False
            
            # First check logic-based detection
            if logic_scam_detected:
                is_potential_scammer = True
                print(f"🚨 Speaker {speaker} marked as SCAMMER due to logic detection: {logic_reason}")
            
            # Check for high-risk phrases first
            text_lower = text.lower()
            for phrase in self.high_risk_phrases:
                if phrase in text_lower:
                    is_potential_scammer = True
                    break
            
            # Also check individual keywords
            if not is_potential_scammer:
                is_potential_scammer = risk_score > 0.1  # 10% threshold
            
            # Determine vulnerability level (improved)
            vulnerability_level = 'low'
            if any(keyword in scam_keywords_found for keyword in ['otp', 'password', 'pin']):
                vulnerability_level = 'high'
            elif any(keyword in scam_keywords_found for keyword in ['share', 'send', 'give', 'tell', 'say']):
                vulnerability_level = 'medium'
            
            analysis_results[speaker] = {
                'text': text,
                'scam_keywords': scam_keywords_found,
                'unique_scam_keywords': unique_scam_keywords,
                'risk_score': risk_score,
                'is_potential_scammer': is_potential_scammer,
                'vulnerability_level': vulnerability_level,
                'word_count': len(data['words'])
            }
        
        return analysis_results
    
    def display_analysis_results(self, analysis_results):
        """Display the analysis results"""
        print(f"\n📊 SCAM DETECTION ANALYSIS RESULTS:")
        print("=" * 60)
        
        total_speakers = len(analysis_results)
        potential_scammers = sum(1 for result in analysis_results.values() if result['is_potential_scammer'])
        
        print(f"👥 Total Speakers: {total_speakers}")
        print(f"🚨 Potential Scammers: {potential_scammers}")
        
        # Analyze each speaker
        for speaker, result in analysis_results.items():
            print(f"\n👤 SPEAKER {speaker} ANALYSIS:")
            print(f"   Text: {result['text']}")
            print(f"   Word Count: {result['word_count']}")
            print(f"   Scam Keywords Found: {', '.join(result['scam_keywords']) if result['scam_keywords'] else 'None'}")
            print(f"   Unique Scam Keywords: {result['unique_scam_keywords']}")
            print(f"   Risk Score: {result['risk_score']:.2f} ({result['risk_score']*100:.1f}%)")
            
            # Status indicators
            if result['is_potential_scammer']:
                print(f"   Status: 🚨 POTENTIAL SCAMMER")
            else:
                print(f"   Status: ✅ SAFE")
            
            print(f"   Vulnerability: {result['vulnerability_level'].upper()}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print("-" * 40)
        
        if potential_scammers > 0:
            print(f"🚨 ALERT: Potential scam detected!")
            print(f"   {potential_scammers} out of {total_speakers} speakers show scam indicators")
            print(f"   Recommendation: Be cautious and verify caller identity")
        else:
            print(f"✅ SAFE: No significant scam indicators detected")
            print(f"   All speakers appear to be legitimate")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        
        for speaker, result in analysis_results.items():
            if result['is_potential_scammer']:
                print(f"   Speaker {speaker}: 🚨 High risk - Consider ending call")
            elif result['vulnerability_level'] == 'high':
                print(f"   Speaker {speaker}: ⚠️ High vulnerability - Don't share sensitive info")
            elif result['vulnerability_level'] == 'medium':
                print(f"   Speaker {speaker}: ⚠️ Medium vulnerability - Be cautious")
            else:
                print(f"   Speaker {speaker}: ✅ Safe - Normal conversation")
    
    def run_complete_analysis(self):
        """Run the complete scam detection analysis"""
        print("🎯 COMPLETE SCAM DETECTION SYSTEM")
        print("=" * 50)
        print("💡 This system will:")
        print("   1. Record a conversation")
        print("   2. Separate speakers using AI")
        print("   3. Analyze each speaker for scam indicators")
        print("   4. Provide risk assessment and recommendations")
        
        # Test microphone
        if not self.test_microphone():
            return
        
        # Record conversation
        recording = self.record_conversation(duration=15)
        
        # Save audio
        audio_file = self.save_audio(recording)
        
        # Transcribe with diarization
        transcription_result = self.transcribe_with_diarization(audio_file)
        
        if transcription_result:
            # Analyze speakers
            analysis_results = self.analyze_speakers(transcription_result)
            
            # Display results
            self.display_analysis_results(analysis_results)
        else:
            print("❌ Analysis failed - no transcription available")
        
        # Cleanup
        keep_file = input("\n🗑️ Delete audio file? (y/n): ").lower()
        if keep_file == 'y':
            os.remove(audio_file)
            print("✅ Audio file deleted")
        else:
            print(f"💾 Audio file kept: {audio_file}")

def main():
    """Main function"""
    try:
        detector = CompleteScamDetector()
        detector.run_complete_analysis()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
