import os
import io
import wave
import numpy as np
import librosa
import webrtcvad
import soundfile as sf
from scipy import signal
from scipy.stats import skew, kurtosis
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# NLP Libraries
import spacy
import nltk
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

class EnhancedFeatureExtractor:
    """
    Enhanced feature extractor for voice-based scam detection
    Implements both acoustic and linguistic features
    """
    
    def __init__(self):
        """Initialize the enhanced feature extractor"""
        print("🔧 Initializing Enhanced Feature Extractor...")
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.frame_length = 1024
        self.hop_length = 512
        
        # Initialize VAD (Voice Activity Detection)
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2 (moderate)
        
        # Initialize NLP models
        self._init_nlp_models()
        
        # Initialize emotion detection
        self._init_emotion_detection()
        
        print("✅ Enhanced Feature Extractor initialized successfully!")
    
    def _init_nlp_models(self):
        """Initialize NLP models for text analysis"""
        try:
            # Load spaCy model for NER
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("✅ spaCy English model loaded")
            except OSError:
                print("⚠️ spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
            
            # Initialize sentiment analysis pipeline
            try:
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                print("✅ Advanced sentiment analysis model loaded")
            except Exception as e:
                print(f"⚠️ Advanced sentiment model failed: {e}")
                self.sentiment_pipeline = None
            
            # Download NLTK data
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
                print("✅ NLTK data downloaded")
            except Exception as e:
                print(f"⚠️ NLTK download failed: {e}")
                
        except Exception as e:
            print(f"❌ NLP initialization error: {e}")
            self.nlp = None
            self.sentiment_pipeline = None
    
    def _init_emotion_detection(self):
        """Initialize emotion detection from text"""
        try:
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            print("✅ Emotion detection model loaded")
        except Exception as e:
            print(f"⚠️ Emotion detection failed: {e}")
            self.emotion_pipeline = None
    
    def extract_acoustic_features(self, audio_file_path: str) -> Dict:
        """
        Extract comprehensive acoustic features from audio file
        
        Features:
        - Pitch (fundamental frequency)
        - Speech rate (words per minute)
        - Pauses and silence detection
        - Intensity/Energy
        - Speaker overlap detection
        - Emotion from voice (prosodic features)
        """
        print(f"🎵 Extracting acoustic features from: {audio_file_path}")
        
        try:
            # Load audio file
            audio_data, sr = librosa.load(audio_file_path, sr=self.sample_rate)
            
            # Initialize features dictionary
            features = {
                'pitch_features': {},
                'speech_rate': 0,
                'pause_features': {},
                'intensity_features': {},
                'prosodic_features': {},
                'voice_activity': {},
                'emotion_features': {}
            }
            
            # 1. Pitch Analysis (Fundamental Frequency)
            features['pitch_features'] = self._extract_pitch_features(audio_data, sr)
            
            # 2. Speech Rate Analysis
            features['speech_rate'] = self._calculate_speech_rate(audio_data, sr)
            
            # 3. Pause and Silence Detection
            features['pause_features'] = self._detect_pauses(audio_data, sr)
            
            # 4. Intensity/Energy Analysis
            features['intensity_features'] = self._extract_intensity_features(audio_data, sr)
            
            # 5. Prosodic Features (rhythm, stress patterns)
            features['prosodic_features'] = self._extract_prosodic_features(audio_data, sr)
            
            # 6. Voice Activity Detection
            features['voice_activity'] = self._analyze_voice_activity(audio_data, sr)
            
            # 7. Emotion from Voice (prosodic-based)
            features['emotion_features'] = self._extract_emotion_from_voice(audio_data, sr)
            
            print("✅ Acoustic features extracted successfully")
            return features
            
        except Exception as e:
            print(f"❌ Acoustic feature extraction failed: {e}")
            return {}
    
    def _extract_pitch_features(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Extract pitch-related features"""
        try:
            # Extract fundamental frequency using librosa
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_data, 
                fmin=librosa.note_to_hz('C2'), 
                fmax=librosa.note_to_hz('C7'),
                sr=sr
            )
            
            # Remove NaN values
            f0_clean = f0[~np.isnan(f0)]
            
            if len(f0_clean) == 0:
                return {'mean_pitch': 0, 'pitch_variance': 0, 'pitch_range': 0}
            
            return {
                'mean_pitch': float(np.mean(f0_clean)),
                'pitch_variance': float(np.var(f0_clean)),
                'pitch_range': float(np.max(f0_clean) - np.min(f0_clean)),
                'pitch_skewness': float(skew(f0_clean)),
                'pitch_kurtosis': float(kurtosis(f0_clean)),
                'voiced_ratio': float(np.mean(voiced_flag))
            }
        except Exception as e:
            print(f"⚠️ Pitch extraction failed: {e}")
            return {'mean_pitch': 0, 'pitch_variance': 0, 'pitch_range': 0}
    
    def _calculate_speech_rate(self, audio_data: np.ndarray, sr: int) -> float:
        """Calculate speech rate (words per minute approximation)"""
        try:
            # Use voice activity detection to estimate speech segments
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)   # 10ms hop
            
            # Convert to 16-bit PCM for VAD
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Detect voice activity
            voice_frames = 0
            total_frames = 0
            
            for i in range(0, len(audio_int16) - frame_length, hop_length):
                frame = audio_int16[i:i + frame_length]
                if len(frame) == frame_length:
                    try:
                        if self.vad.is_speech(frame.tobytes(), sr):
                            voice_frames += 1
                        total_frames += 1
                    except:
                        pass
            
            if total_frames == 0:
                return 0.0
            
            # Estimate speech rate (rough approximation)
            voice_ratio = voice_frames / total_frames
            duration_minutes = len(audio_data) / (sr * 60)
            
            # Rough estimate: assume average speaking rate of 150 WPM
            estimated_wpm = voice_ratio * 150
            
            return float(estimated_wpm)
            
        except Exception as e:
            print(f"⚠️ Speech rate calculation failed: {e}")
            return 0.0
    
    def _detect_pauses(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Detect pauses and silence in audio"""
        try:
            # Calculate RMS energy
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)   # 10ms hop
            
            rms_energy = librosa.feature.rms(
                y=audio_data, 
                frame_length=frame_length, 
                hop_length=hop_length
            )[0]
            
            # Define silence threshold (adaptive)
            silence_threshold = np.percentile(rms_energy, 20)  # Bottom 20%
            
            # Detect silence frames
            silence_frames = rms_energy < silence_threshold
            
            # Find pause segments
            pause_segments = []
            in_pause = False
            pause_start = 0
            
            for i, is_silent in enumerate(silence_frames):
                if is_silent and not in_pause:
                    pause_start = i
                    in_pause = True
                elif not is_silent and in_pause:
                    pause_duration = (i - pause_start) * hop_length / sr
                    if pause_duration > 0.1:  # Pauses longer than 100ms
                        pause_segments.append({
                            'start': pause_start * hop_length / sr,
                            'duration': pause_duration
                        })
                    in_pause = False
            
            return {
                'total_pause_time': sum(seg['duration'] for seg in pause_segments),
                'pause_count': len(pause_segments),
                'average_pause_duration': np.mean([seg['duration'] for seg in pause_segments]) if pause_segments else 0,
                'pause_segments': pause_segments,
                'silence_ratio': float(np.mean(silence_frames))
            }
            
        except Exception as e:
            print(f"⚠️ Pause detection failed: {e}")
            return {'total_pause_time': 0, 'pause_count': 0, 'average_pause_duration': 0}
    
    def _extract_intensity_features(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Extract intensity/energy features"""
        try:
            # Calculate RMS energy
            rms_energy = librosa.feature.rms(y=audio_data)[0]
            
            # Calculate spectral centroid (brightness)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
            
            # Calculate zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            return {
                'mean_intensity': float(np.mean(rms_energy)),
                'intensity_variance': float(np.var(rms_energy)),
                'max_intensity': float(np.max(rms_energy)),
                'min_intensity': float(np.min(rms_energy)),
                'intensity_range': float(np.max(rms_energy) - np.min(rms_energy)),
                'spectral_centroid_mean': float(np.mean(spectral_centroid)),
                'zero_crossing_rate_mean': float(np.mean(zcr))
            }
            
        except Exception as e:
            print(f"⚠️ Intensity extraction failed: {e}")
            return {'mean_intensity': 0, 'intensity_variance': 0}
    
    def _extract_prosodic_features(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Extract prosodic features (rhythm, stress patterns)"""
        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            
            # Calculate tempo
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sr)
            
            # Calculate spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)[0]
            
            return {
                'tempo': float(tempo),
                'mfcc_mean': [float(np.mean(mfcc)) for mfcc in mfccs],
                'mfcc_variance': [float(np.var(mfcc)) for mfcc in mfccs],
                'spectral_rolloff_mean': float(np.mean(rolloff)),
                'beat_count': len(beats)
            }
            
        except Exception as e:
            print(f"⚠️ Prosodic extraction failed: {e}")
            return {'tempo': 0, 'mfcc_mean': [], 'mfcc_variance': []}
    
    def _analyze_voice_activity(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Analyze voice activity patterns"""
        try:
            # Convert to 16-bit PCM for VAD
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)   # 10ms hop
            
            voice_segments = []
            in_voice = False
            voice_start = 0
            
            for i in range(0, len(audio_int16) - frame_length, hop_length):
                frame = audio_int16[i:i + frame_length]
                if len(frame) == frame_length:
                    try:
                        is_speech = self.vad.is_speech(frame.tobytes(), sr)
                        
                        if is_speech and not in_voice:
                            voice_start = i
                            in_voice = True
                        elif not is_speech and in_voice:
                            voice_duration = (i - voice_start) * hop_length / sr
                            voice_segments.append({
                                'start': voice_start * hop_length / sr,
                                'duration': voice_duration
                            })
                            in_voice = False
                    except:
                        pass
            
            total_voice_time = sum(seg['duration'] for seg in voice_segments)
            total_duration = len(audio_data) / sr
            
            return {
                'voice_segments': voice_segments,
                'total_voice_time': total_voice_time,
                'voice_ratio': total_voice_time / total_duration if total_duration > 0 else 0,
                'segment_count': len(voice_segments),
                'average_segment_duration': np.mean([seg['duration'] for seg in voice_segments]) if voice_segments else 0
            }
            
        except Exception as e:
            print(f"⚠️ Voice activity analysis failed: {e}")
            return {'voice_ratio': 0, 'segment_count': 0}
    
    def _extract_emotion_from_voice(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Extract emotion-related features from voice prosody"""
        try:
            # Extract features that correlate with emotions
            pitch_features = self._extract_pitch_features(audio_data, sr)
            intensity_features = self._extract_intensity_features(audio_data, sr)
            
            # Simple emotion classification based on prosodic features
            emotion_scores = {
                'anger': 0.0,
                'fear': 0.0,
                'joy': 0.0,
                'sadness': 0.0,
                'neutral': 0.0
            }
            
            # Rule-based emotion detection (can be replaced with ML model)
            mean_pitch = pitch_features.get('mean_pitch', 0)
            pitch_variance = pitch_features.get('pitch_variance', 0)
            mean_intensity = intensity_features.get('mean_intensity', 0)
            
            # High pitch + high variance + high intensity = Anger/Fear
            if mean_pitch > 200 and pitch_variance > 1000 and mean_intensity > 0.1:
                emotion_scores['anger'] = 0.7
                emotion_scores['fear'] = 0.3
            
            # Low pitch + low variance + low intensity = Sadness
            elif mean_pitch < 150 and pitch_variance < 500 and mean_intensity < 0.05:
                emotion_scores['sadness'] = 0.8
            
            # Medium pitch + medium variance + medium intensity = Neutral
            elif 150 <= mean_pitch <= 200 and 500 <= pitch_variance <= 1000:
                emotion_scores['neutral'] = 0.6
            
            # High pitch + low variance = Joy
            elif mean_pitch > 200 and pitch_variance < 500:
                emotion_scores['joy'] = 0.6
            
            return {
                'emotion_scores': emotion_scores,
                'dominant_emotion': max(emotion_scores, key=emotion_scores.get),
                'confidence': max(emotion_scores.values())
            }
            
        except Exception as e:
            print(f"⚠️ Emotion extraction failed: {e}")
            return {'emotion_scores': {}, 'dominant_emotion': 'neutral', 'confidence': 0}
    
    def extract_linguistic_features(self, text: str) -> Dict:
        """
        Extract comprehensive linguistic features from text
        
        Features:
        - Named Entity Recognition (names, banks, OTP)
        - Intent scores
        - Sentiment analysis
        - Deception markers
        - Keyword analysis
        """
        print(f"📝 Extracting linguistic features from text: {text[:100]}...")
        
        features = {
            'ner_entities': {},
            'intent_scores': {},
            'sentiment_analysis': {},
            'deception_markers': {},
            'keyword_analysis': {},
            'text_statistics': {}
        }
        
        try:
            # 1. Named Entity Recognition
            features['ner_entities'] = self._extract_ner_entities(text)
            
            # 2. Intent Classification
            features['intent_scores'] = self._classify_intent(text)
            
            # 3. Sentiment Analysis
            features['sentiment_analysis'] = self._analyze_sentiment(text)
            
            # 4. Deception Markers
            features['deception_markers'] = self._detect_deception_markers(text)
            
            # 5. Keyword Analysis
            features['keyword_analysis'] = self._analyze_keywords(text)
            
            # 6. Text Statistics
            features['text_statistics'] = self._calculate_text_statistics(text)
            
            print("✅ Linguistic features extracted successfully")
            return features
            
        except Exception as e:
            print(f"❌ Linguistic feature extraction failed: {e}")
            return features
    
    def _extract_ner_entities(self, text: str) -> Dict:
        """Extract named entities using spaCy"""
        try:
            if not self.nlp:
                return {'error': 'spaCy model not available'}
            
            doc = self.nlp(text)
            
            entities = {
                'persons': [],
                'organizations': [],
                'banks': [],
                'otp_numbers': [],
                'phone_numbers': [],
                'amounts': [],
                'all_entities': []
            }
            
            # Bank names and financial institutions
            bank_keywords = ['bank', 'rbi', 'sbi', 'hdfc', 'icici', 'axis', 'kotak', 'pnb', 'bob', 'union']
            
            for ent in doc.ents:
                entity_info = {
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 1.0  # spaCy doesn't provide confidence scores
                }
                
                entities['all_entities'].append(entity_info)
                
                # Categorize entities
                if ent.label_ == 'PERSON':
                    entities['persons'].append(entity_info)
                elif ent.label_ == 'ORG':
                    entities['organizations'].append(entity_info)
                    # Check if it's a bank
                    if any(bank in ent.text.lower() for bank in bank_keywords):
                        entities['banks'].append(entity_info)
                elif ent.label_ == 'MONEY':
                    entities['amounts'].append(entity_info)
                elif ent.label_ == 'CARDINAL' and len(ent.text) == 6 and ent.text.isdigit():
                    # Potential OTP (6-digit number)
                    entities['otp_numbers'].append(entity_info)
            
            # Additional OTP detection using regex patterns
            import re
            otp_patterns = [
                r'\b\d{6}\b',  # 6-digit numbers
                r'\b\d{4}\b',  # 4-digit numbers
                r'otp[:\s]*(\d+)',  # OTP: 123456
                r'code[:\s]*(\d+)'   # Code: 123456
            ]
            
            for pattern in otp_patterns:
                matches = re.finditer(pattern, text.lower())
                for match in matches:
                    entities['otp_numbers'].append({
                        'text': match.group(),
                        'label': 'OTP',
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8
                    })
            
            return entities
            
        except Exception as e:
            print(f"⚠️ NER extraction failed: {e}")
            return {'error': str(e)}
    
    def _classify_intent(self, text: str) -> Dict:
        """Classify intent of the conversation"""
        try:
            text_lower = text.lower()
            
            intent_scores = {
                'scam_request': 0.0,
                'information_gathering': 0.0,
                'urgent_action': 0.0,
                'money_transfer': 0.0,
                'verification': 0.0,
                'social_engineering': 0.0,
                'legitimate': 0.0
            }
            
            # Scam request indicators
            scam_phrases = [
                'send money', 'transfer money', 'pay money', 'give money',
                'share otp', 'tell otp', 'say otp', 'provide otp',
                'bank asking for money', 'urgent payment'
            ]
            
            for phrase in scam_phrases:
                if phrase in text_lower:
                    intent_scores['scam_request'] += 0.3
            
            # Information gathering
            info_phrases = [
                'what is your', 'tell me your', 'share your', 'give me your',
                'account number', 'card number', 'pin number'
            ]
            
            for phrase in info_phrases:
                if phrase in text_lower:
                    intent_scores['information_gathering'] += 0.2
            
            # Urgent action
            urgent_phrases = [
                'immediately', 'urgent', 'now', 'right now', 'asap',
                'blocked', 'suspended', 'expired'
            ]
            
            for phrase in urgent_phrases:
                if phrase in text_lower:
                    intent_scores['urgent_action'] += 0.2
            
            # Money transfer
            money_phrases = [
                'transfer', 'send', 'pay', 'deposit', 'lakh', 'rupees'
            ]
            
            for phrase in money_phrases:
                if phrase in text_lower:
                    intent_scores['money_transfer'] += 0.2
            
            # Verification
            verify_phrases = [
                'verify', 'confirm', 'authenticate', 'validate'
            ]
            
            for phrase in verify_phrases:
                if phrase in text_lower:
                    intent_scores['verification'] += 0.2
            
            # Social engineering
            social_phrases = [
                'i am from', 'we are from', 'bank calling', 'government',
                'representative', 'official', 'employee'
            ]
            
            for phrase in social_phrases:
                if phrase in text_lower:
                    intent_scores['social_engineering'] += 0.2
            
            # Normalize scores
            total_score = sum(intent_scores.values())
            if total_score > 0:
                for intent in intent_scores:
                    intent_scores[intent] = min(intent_scores[intent] / total_score, 1.0)
            
            # If no specific intent detected, mark as legitimate
            if total_score == 0:
                intent_scores['legitimate'] = 1.0
            
            return intent_scores
            
        except Exception as e:
            print(f"⚠️ Intent classification failed: {e}")
            return {'error': str(e)}
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using multiple approaches"""
        try:
            sentiment_results = {}
            
            # 1. TextBlob sentiment
            blob = TextBlob(text)
            sentiment_results['textblob'] = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'label': 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
            }
            
            # 2. Advanced sentiment analysis (if available)
            if self.sentiment_pipeline:
                try:
                    sentiment_scores = self.sentiment_pipeline(text)
                    sentiment_results['advanced'] = sentiment_scores[0]
                except Exception as e:
                    print(f"⚠️ Advanced sentiment failed: {e}")
            
            # 3. Emotion detection (if available)
            if self.emotion_pipeline:
                try:
                    emotion_scores = self.emotion_pipeline(text)
                    sentiment_results['emotions'] = emotion_scores[0]
                except Exception as e:
                    print(f"⚠️ Emotion detection failed: {e}")
            
            return sentiment_results
            
        except Exception as e:
            print(f"⚠️ Sentiment analysis failed: {e}")
            return {'error': str(e)}
    
    def _detect_deception_markers(self, text: str) -> Dict:
        """Detect linguistic deception markers"""
        try:
            text_lower = text.lower()
            
            deception_markers = {
                'urgency_indicators': [],
                'authority_claims': [],
                'fear_appeals': [],
                'social_proof': [],
                'inconsistencies': [],
                'deception_score': 0.0
            }
            
            # Urgency indicators
            urgency_words = [
                'urgent', 'immediately', 'now', 'right now', 'asap',
                'expires', 'deadline', 'last chance', 'final notice'
            ]
            
            for word in urgency_words:
                if word in text_lower:
                    deception_markers['urgency_indicators'].append(word)
            
            # Authority claims
            authority_phrases = [
                'i am from', 'we are from', 'bank calling', 'government',
                'rbi', 'official', 'representative', 'authorized'
            ]
            
            for phrase in authority_phrases:
                if phrase in text_lower:
                    deception_markers['authority_claims'].append(phrase)
            
            # Fear appeals
            fear_words = [
                'blocked', 'suspended', 'fraud', 'hacked', 'compromised',
                'penalty', 'fine', 'legal action', 'police'
            ]
            
            for word in fear_words:
                if word in text_lower:
                    deception_markers['fear_appeals'].append(word)
            
            # Social proof
            social_proof_phrases = [
                'everyone is doing', 'many people', 'thousands of',
                'popular', 'recommended', 'trusted by'
            ]
            
            for phrase in social_proof_phrases:
                if phrase in text_lower:
                    deception_markers['social_proof'].append(phrase)
            
            # Calculate deception score
            total_markers = (
                len(deception_markers['urgency_indicators']) +
                len(deception_markers['authority_claims']) +
                len(deception_markers['fear_appeals']) +
                len(deception_markers['social_proof'])
            )
            
            deception_markers['deception_score'] = min(total_markers / 10.0, 1.0)
            
            return deception_markers
            
        except Exception as e:
            print(f"⚠️ Deception marker detection failed: {e}")
            return {'error': str(e)}
    
    def _analyze_keywords(self, text: str) -> Dict:
        """Analyze keywords and their significance"""
        try:
            text_lower = text.lower()
            
            # Scam-related keywords (from original implementation)
            scam_keywords = [
                'otp', 'password', 'pin', 'account', 'blocked', 'suspended',
                'urgent', 'immediately', 'verify', 'confirm', 'share', 'send',
                'bank', 'rbi', 'government', 'tax', 'refund', 'win', 'prize',
                'suspicious', 'fraud', 'security', 'update', 'reactivate',
                'debit', 'credit', 'card', 'number', 'cvv', 'expiry',
                'say', 'tell', 'give', 'provide', 'enter', 'input', 'type',
                'code', 'verification', 'authenticate', 'unlock', 'unblock',
                'pay', 'payment', 'money', 'transfer', 'deposit', 'send',
                'fees', 'charges', 'penalty', 'fine', 'amount', 'cost'
            ]
            
            found_keywords = []
            keyword_positions = {}
            
            for keyword in scam_keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
                    # Find positions
                    start = text_lower.find(keyword)
                    keyword_positions[keyword] = start
            
            return {
                'found_keywords': found_keywords,
                'keyword_count': len(found_keywords),
                'keyword_positions': keyword_positions,
                'keyword_density': len(found_keywords) / len(text.split()) if text.split() else 0
            }
            
        except Exception as e:
            print(f"⚠️ Keyword analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_text_statistics(self, text: str) -> Dict:
        """Calculate basic text statistics"""
        try:
            words = text.split()
            sentences = text.split('.')
            
            return {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'average_words_per_sentence': len(words) / len(sentences) if sentences else 0,
                'character_count': len(text),
                'unique_words': len(set(words)),
                'lexical_diversity': len(set(words)) / len(words) if words else 0
            }
            
        except Exception as e:
            print(f"⚠️ Text statistics calculation failed: {e}")
            return {'error': str(e)}
    
    def extract_all_features(self, audio_file_path: str, text: str) -> Dict:
        """Extract both acoustic and linguistic features"""
        print("🔍 Extracting all features...")
        
        features = {
            'acoustic_features': self.extract_acoustic_features(audio_file_path),
            'linguistic_features': self.extract_linguistic_features(text),
            'extraction_timestamp': pd.Timestamp.now().isoformat()
        }
        
        print("✅ All features extracted successfully")
        return features

def main():
    """Test the enhanced feature extractor"""
    print("🧪 Testing Enhanced Feature Extractor...")
    
    extractor = EnhancedFeatureExtector()
    
    # Test with sample text
    sample_text = "Hello, I am calling from SBI bank. Your account has been blocked due to suspicious activity. Please share your OTP immediately to unblock it."
    
    print("\n📝 Testing linguistic features...")
    linguistic_features = extractor.extract_linguistic_features(sample_text)
    print(f"NER Entities: {linguistic_features.get('ner_entities', {})}")
    print(f"Intent Scores: {linguistic_features.get('intent_scores', {})}")
    print(f"Sentiment: {linguistic_features.get('sentiment_analysis', {})}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()

