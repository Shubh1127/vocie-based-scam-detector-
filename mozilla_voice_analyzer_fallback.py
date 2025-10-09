import os
import librosa
import numpy as np
import tempfile
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings("ignore")

class MozillaVoiceAnalyzerFallback:
    """
    Fallback Mozilla Voice Analyzer using only librosa (no transformers dependency)
    This provides basic voice analysis without pre-trained models
    """
    
    def __init__(self):
        """Initialize the fallback analyzer"""
        print("⚠️ Using fallback Mozilla Voice analyzer (no transformers)")
        print("💡 For full functionality, install transformers with compatible versions")
        
        # Voice characteristics thresholds
        self.voice_thresholds = {
            'pitch_range': {'low': 80, 'high': 300},  # Hz
            'speaking_rate': {'slow': 2.0, 'fast': 4.0},  # words per second
            'energy_level': {'low': 0.1, 'high': 0.8},  # normalized
            'voice_quality': {'clear': 0.7, 'distorted': 0.3}  # clarity score
        }
    
    def extract_audio_features(self, audio_path: str) -> Dict:
        """Extract comprehensive audio features using librosa only"""
        try:
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Basic audio features
            features = {
                'duration': len(audio) / sr,
                'sample_rate': sr,
                'audio_length': len(audio)
            }
            
            # MFCC features
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfcc, axis=1).tolist()
            features['mfcc_std'] = np.std(mfcc, axis=1).tolist()
            
            # Spectral features
            features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)))
            features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr)))
            features['spectral_bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=sr)))
            
            # Zero crossing rate
            features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
            
            # Energy features
            features['rms_energy'] = float(np.mean(librosa.feature.rms(y=audio)))
            features['energy_entropy'] = float(np.mean(librosa.feature.spectral_contrast(y=audio, sr=sr)))
            
            # Pitch features
            try:
                pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
                pitch_values = []
                for t in range(pitches.shape[1]):
                    index = magnitudes[:, t].argmax()
                    pitch = pitches[index, t]
                    if pitch > 0:
                        pitch_values.append(pitch)
                
                if pitch_values:
                    features['pitch_mean'] = float(np.mean(pitch_values))
                    features['pitch_std'] = float(np.std(pitch_values))
                    features['pitch_range'] = float(np.max(pitch_values) - np.min(pitch_values))
                else:
                    features['pitch_mean'] = 0.0
                    features['pitch_std'] = 0.0
                    features['pitch_range'] = 0.0
            except:
                features['pitch_mean'] = 0.0
                features['pitch_std'] = 0.0
                features['pitch_range'] = 0.0
            
            return features
            
        except Exception as e:
            print(f"❌ Error extracting audio features: {e}")
            return {}
    
    def analyze_voice_characteristics(self, audio_path: str) -> Dict:
        """Analyze voice characteristics using librosa features only"""
        try:
            features = self.extract_audio_features(audio_path)
            
            # Simple voice analysis based on features
            voice_analysis = {
                'scam_probability': self.calculate_scam_probability(features),
                'confidence': 0.7,  # Fixed confidence for fallback
                'voice_embedding': [],  # Empty for fallback
                'voice_characteristics': self.analyze_voice_quality_from_features(features)
            }
            
            return voice_analysis
            
        except Exception as e:
            print(f"❌ Error in voice analysis: {e}")
            return {"error": str(e)}
    
    def calculate_scam_probability(self, features: Dict) -> float:
        """Calculate scam probability based on audio features"""
        try:
            score = 0.0
            
            # Check for suspicious pitch patterns
            pitch_std = features.get('pitch_std', 0)
            if pitch_std > 100:  # High pitch variation
                score += 0.3
            
            # Check for unnatural rhythm
            zcr = features.get('zero_crossing_rate', 0)
            if zcr > 0.1:  # High zero crossing rate
                score += 0.2
            
            # Check for low quality
            spectral_centroid = features.get('spectral_centroid', 0)
            if spectral_centroid < 1000:  # Low spectral centroid
                score += 0.2
            
            # Check for artificial sounding
            rms_energy = features.get('rms_energy', 0)
            if rms_energy < 0.01:  # Very low energy
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            print(f"❌ Error calculating scam probability: {e}")
            return 0.5
    
    def analyze_voice_quality_from_features(self, features: Dict) -> Dict:
        """Analyze voice quality from extracted features"""
        try:
            # Calculate speaking rate (simplified)
            duration = features.get('duration', 1)
            speaking_rate = 3.0  # Default estimate
            
            # Calculate energy level
            energy_level = features.get('rms_energy', 0.5)
            
            # Calculate voice clarity
            spectral_centroid = features.get('spectral_centroid', 1000)
            clarity_score = min(1.0, spectral_centroid / 2000)
            
            # Determine voice characteristics
            characteristics = {
                'speaking_rate': speaking_rate,
                'energy_level': energy_level,
                'clarity_score': clarity_score,
                'voice_type': self.classify_voice_type(speaking_rate, energy_level, clarity_score),
                'quality_assessment': self.assess_voice_quality(speaking_rate, energy_level, clarity_score)
            }
            
            return characteristics
            
        except Exception as e:
            print(f"❌ Error analyzing voice quality: {e}")
            return {}
    
    def classify_voice_type(self, speaking_rate: float, energy_level: float, clarity_score: float) -> str:
        """Classify voice type based on characteristics"""
        if speaking_rate < self.voice_thresholds['speaking_rate']['slow']:
            rate_type = "slow"
        elif speaking_rate > self.voice_thresholds['speaking_rate']['fast']:
            rate_type = "fast"
        else:
            rate_type = "normal"
        
        if energy_level < self.voice_thresholds['energy_level']['low']:
            energy_type = "low"
        elif energy_level > self.voice_thresholds['energy_level']['high']:
            energy_type = "high"
        else:
            energy_type = "normal"
        
        if clarity_score < self.voice_thresholds['voice_quality']['distorted']:
            clarity_type = "distorted"
        elif clarity_score > self.voice_thresholds['voice_quality']['clear']:
            clarity_type = "clear"
        else:
            clarity_type = "moderate"
        
        return f"{rate_type}_{energy_type}_{clarity_type}"
    
    def assess_voice_quality(self, speaking_rate: float, energy_level: float, clarity_score: float) -> Dict:
        """Assess overall voice quality"""
        quality_score = (clarity_score + min(1.0, energy_level) + 
                        min(1.0, abs(speaking_rate - 3.0) / 3.0)) / 3.0
        
        if quality_score > 0.7:
            quality_level = "high"
            assessment = "Clear, natural voice"
        elif quality_score > 0.4:
            quality_level = "medium"
            assessment = "Moderate voice quality"
        else:
            quality_level = "low"
            assessment = "Poor voice quality or potential distortion"
        
        return {
            'quality_score': quality_score,
            'quality_level': quality_level,
            'assessment': assessment
        }
    
    def detect_voice_anomalies(self, audio_path: str) -> Dict:
        """Detect potential voice anomalies"""
        try:
            features = self.extract_audio_features(audio_path)
            
            anomalies = {
                'suspicious_pitch': False,
                'unnatural_rhythm': False,
                'low_quality': False,
                'artificial_sounding': False,
                'anomaly_score': 0.0
            }
            
            # Check for suspicious pitch patterns
            if features.get('pitch_std', 0) > 100:
                anomalies['suspicious_pitch'] = True
                anomalies['anomaly_score'] += 0.3
            
            # Check for unnatural rhythm
            if features.get('zero_crossing_rate', 0) > 0.1:
                anomalies['unnatural_rhythm'] = True
                anomalies['anomaly_score'] += 0.2
            
            # Check for low quality
            if features.get('spectral_centroid', 0) < 1000:
                anomalies['low_quality'] = True
                anomalies['anomaly_score'] += 0.2
            
            # Check for artificial sounding
            if features.get('rms_energy', 0) < 0.01:
                anomalies['artificial_sounding'] = True
                anomalies['anomaly_score'] += 0.3
            
            return anomalies
            
        except Exception as e:
            print(f"❌ Error detecting voice anomalies: {e}")
            return {"error": str(e)}
    
    def generate_voice_insights(self, audio_path: str) -> Dict:
        """Generate comprehensive voice insights"""
        try:
            # Extract features
            features = self.extract_audio_features(audio_path)
            
            # Analyze voice characteristics
            voice_analysis = self.analyze_voice_characteristics(audio_path)
            
            # Detect anomalies
            anomalies = self.detect_voice_anomalies(audio_path)
            
            # Combine insights
            insights = {
                'audio_features': features,
                'voice_analysis': voice_analysis,
                'anomalies': anomalies,
                'overall_assessment': self.generate_overall_assessment(voice_analysis, anomalies),
                'recommendations': self.generate_recommendations(voice_analysis, anomalies)
            }
            
            return insights
            
        except Exception as e:
            print(f"❌ Error generating voice insights: {e}")
            return {"error": str(e)}
    
    def generate_overall_assessment(self, voice_analysis: Dict, anomalies: Dict) -> Dict:
        """Generate overall voice assessment"""
        scam_prob = voice_analysis.get('scam_probability', 0.5)
        anomaly_score = anomalies.get('anomaly_score', 0.0)
        
        # Calculate overall risk
        overall_risk = (scam_prob + anomaly_score) / 2.0
        
        if overall_risk > 0.7:
            risk_level = "high"
            assessment = "High risk of scam - multiple suspicious voice characteristics detected"
        elif overall_risk > 0.4:
            risk_level = "medium"
            assessment = "Medium risk - some suspicious characteristics detected"
        else:
            risk_level = "low"
            assessment = "Low risk - voice appears natural"
        
        return {
            'overall_risk_score': overall_risk,
            'risk_level': risk_level,
            'assessment': assessment,
            'confidence': voice_analysis.get('confidence', 0.5)
        }
    
    def generate_recommendations(self, voice_analysis: Dict, anomalies: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if anomalies.get('suspicious_pitch'):
            recommendations.append("⚠️ Unusual pitch patterns detected - be cautious")
        
        if anomalies.get('unnatural_rhythm'):
            recommendations.append("⚠️ Unnatural speech rhythm - possible artificial voice")
        
        if anomalies.get('low_quality'):
            recommendations.append("⚠️ Poor audio quality - verify caller identity")
        
        if anomalies.get('artificial_sounding'):
            recommendations.append("⚠️ Voice sounds artificial - high scam risk")
        
        if voice_analysis.get('scam_probability', 0) > 0.6:
            recommendations.append("🚨 High scam probability - end call immediately")
        
        if not recommendations:
            recommendations.append("✅ Voice characteristics appear normal")
        
        return recommendations

# Use fallback analyzer (no transformers dependency)
print("🔄 Using fallback Mozilla Voice analyzer (no transformers)")
mozilla_voice_analyzer = MozillaVoiceAnalyzerFallback()
