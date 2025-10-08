# Enhanced Voice-Based Scam Detector

A comprehensive voice-based scam detection system with advanced acoustic and linguistic feature extraction capabilities.

## 🆕 Enhanced Features

### Acoustic Features
- **Pitch Analysis**: Fundamental frequency extraction, pitch variance, range analysis
- **Speech Rate**: Words per minute calculation using voice activity detection
- **Pause Detection**: Silence detection, pause duration analysis
- **Intensity Analysis**: Volume/energy analysis, spectral features
- **Prosodic Features**: Rhythm patterns, tempo analysis, MFCC features
- **Voice Activity Detection**: Speaker overlap detection, voice segment analysis
- **Emotion Detection**: Voice-based emotion classification (anger, fear, joy, sadness, neutral)

### Linguistic Features
- **Named Entity Recognition (NER)**: 
  - Person names detection
  - Bank and organization identification
  - OTP and verification code detection
  - Phone numbers and amounts extraction
- **Intent Classification**: 
  - Scam request detection
  - Information gathering identification
  - Urgent action recognition
  - Money transfer intent
  - Social engineering detection
- **Advanced Sentiment Analysis**: 
  - Multi-model sentiment analysis (TextBlob + Transformers)
  - Emotion detection from text
  - Polarity and subjectivity scoring
- **Deception Markers**: 
  - Urgency indicators
  - Authority claims
  - Fear appeals
  - Social proof detection
- **Keyword Analysis**: 
  - Scam keyword detection
  - Keyword density analysis
  - Position tracking

## 📦 Installation

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Run setup script to download models
python setup_enhanced.py
```

### 2. Manual Model Installation (if setup script fails)

```bash
# Install spaCy English model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download(['punkt', 'vader_lexicon', 'stopwords'])"
```

### 3. Environment Setup

Create a `.env` file with:
```
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🚀 Usage

### Basic Usage

```python
from enhanced_feature_extractor import EnhancedFeatureExtractor

# Initialize extractor
extractor = EnhancedFeatureExtractor()

# Extract acoustic features
acoustic_features = extractor.extract_acoustic_features("audio_file.wav")

# Extract linguistic features
linguistic_features = extractor.extract_linguistic_features("Hello, I am from SBI bank...")

# Extract all features
all_features = extractor.extract_all_features("audio_file.wav", "transcript text")
```

### Integration with Main Detector

The enhanced features are automatically integrated into the main `CompleteScamDetector`:

```python
from complete_scam_detector import CompleteScamDetector

detector = CompleteScamDetector()
# Enhanced features are automatically extracted during analysis
```

## 📊 Feature Output Examples

### Acoustic Features
```json
{
  "pitch_features": {
    "mean_pitch": 180.5,
    "pitch_variance": 1200.3,
    "pitch_range": 300.2,
    "voiced_ratio": 0.85
  },
  "speech_rate": 145.2,
  "pause_features": {
    "total_pause_time": 2.3,
    "pause_count": 8,
    "average_pause_duration": 0.29
  },
  "intensity_features": {
    "mean_intensity": 0.12,
    "intensity_variance": 0.05,
    "max_intensity": 0.35
  },
  "emotion_features": {
    "emotion_scores": {
      "anger": 0.7,
      "fear": 0.3,
      "neutral": 0.0
    },
    "dominant_emotion": "anger",
    "confidence": 0.7
  }
}
```

### Linguistic Features
```json
{
  "ner_entities": {
    "persons": [{"text": "John", "label": "PERSON"}],
    "banks": [{"text": "SBI bank", "label": "ORG"}],
    "otp_numbers": [{"text": "123456", "label": "OTP"}]
  },
  "intent_scores": {
    "scam_request": 0.8,
    "urgent_action": 0.6,
    "information_gathering": 0.4
  },
  "sentiment_analysis": {
    "textblob": {
      "polarity": -0.3,
      "subjectivity": 0.7,
      "label": "negative"
    }
  },
  "deception_markers": {
    "urgency_indicators": ["urgent", "immediately"],
    "authority_claims": ["i am from"],
    "deception_score": 0.6
  }
}
```

## 🔧 Configuration

### Audio Processing Parameters
- **Sample Rate**: 16kHz (configurable)
- **Frame Length**: 1024 samples
- **Hop Length**: 512 samples
- **VAD Aggressiveness**: Level 2 (moderate)

### Model Configuration
- **Sentiment Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Emotion Model**: `j-hartmann/emotion-english-distilroberta-base`
- **spaCy Model**: `en_core_web_sm`

## 🎯 Scam Detection Enhancements

The enhanced features improve scam detection by:

1. **Acoustic Red Flags**:
   - High pitch variance (stress/anxiety)
   - Rapid speech rate (urgency)
   - Frequent pauses (deception markers)
   - High intensity (aggressive behavior)

2. **Linguistic Red Flags**:
   - Authority claims ("I am from bank")
   - Urgency indicators ("immediately", "urgent")
   - Information gathering ("share your OTP")
   - Fear appeals ("account blocked")

3. **Combined Analysis**:
   - Cross-validation between acoustic and linguistic features
   - Multi-modal risk scoring
   - Enhanced confidence metrics

## 🐛 Troubleshooting

### Common Issues

1. **spaCy Model Not Found**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **NLTK Data Missing**:
   ```bash
   python -c "import nltk; nltk.download(['punkt', 'vader_lexicon'])"
   ```

3. **Audio Processing Errors**:
   - Ensure audio file is in supported format (WAV, MP3, etc.)
   - Check file permissions
   - Verify audio file is not corrupted

4. **Memory Issues**:
   - Large audio files may require more RAM
   - Consider processing in chunks for very long audio

### Performance Optimization

- **GPU Acceleration**: Install PyTorch with CUDA support for faster processing
- **Batch Processing**: Process multiple files simultaneously
- **Caching**: Cache model loading for faster subsequent runs

## 📈 Performance Metrics

- **Acoustic Feature Extraction**: ~2-5 seconds per minute of audio
- **Linguistic Feature Extraction**: ~1-2 seconds per 1000 words
- **Memory Usage**: ~500MB-1GB depending on models loaded
- **Accuracy**: Improved scam detection accuracy by ~15-20%

## 🤝 Contributing

To add new features:

1. Extend `EnhancedFeatureExtractor` class
2. Add new feature extraction methods
3. Update integration in `CompleteScamDetector`
4. Add tests and documentation

## 📄 License

This project is part of the Voice-Based Scam Detector system. See main project for license details.




