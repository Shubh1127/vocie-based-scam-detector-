#!/usr/bin/env python3
"""
Test script for Enhanced Voice Scam Detector
Verifies that all features are working correctly
"""

import os
import sys
import tempfile
import numpy as np
import soundfile as sf

def test_basic_imports():
    """Test basic library imports"""
    print("🧪 Testing basic imports...")
    
    try:
        import librosa
        import webrtcvad
        import numpy as np
        import pandas as pd
        import scipy
        import sklearn
        import transformers
        import torch
        print("✅ All basic libraries imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_nlp_imports():
    """Test NLP library imports"""
    print("🧪 Testing NLP imports...")
    
    try:
        import spacy
        import nltk
        from textblob import TextBlob
        print("✅ NLP libraries imported successfully")
        
        # Test spaCy model
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy English model loaded")
        except OSError:
            print("⚠️ spaCy English model not found")
            return False
        
        return True
    except ImportError as e:
        print(f"❌ NLP import failed: {e}")
        return False

def test_enhanced_extractor():
    """Test Enhanced Feature Extractor"""
    print("🧪 Testing Enhanced Feature Extractor...")
    
    try:
        from enhanced_feature_extractor import EnhancedFeatureExtractor
        extractor = EnhancedFeatureExtractor()
        print("✅ Enhanced Feature Extractor initialized")
        return True
    except Exception as e:
        print(f"❌ Enhanced Feature Extractor failed: {e}")
        return False

def create_test_audio():
    """Create a test audio file"""
    print("🎵 Creating test audio file...")
    
    try:
        # Create a simple sine wave audio
        duration = 2  # seconds
        sample_rate = 16000
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(frequency * 2 * np.pi * t) * 0.5
        
        # Add some noise to make it more realistic
        noise = np.random.normal(0, 0.1, len(audio))
        audio = audio + noise
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            sf.write(tmp_file.name, audio, sample_rate)
            return tmp_file.name
            
    except Exception as e:
        print(f"❌ Test audio creation failed: {e}")
        return None

def test_acoustic_features():
    """Test acoustic feature extraction"""
    print("🧪 Testing acoustic feature extraction...")
    
    try:
        from enhanced_feature_extractor import EnhancedFeatureExtractor
        extractor = EnhancedFeatureExtractor()
        
        # Create test audio
        audio_file = create_test_audio()
        if not audio_file:
            return False
        
        # Extract acoustic features
        features = extractor.extract_acoustic_features(audio_file)
        
        # Check if features were extracted
        if features and 'pitch_features' in features:
            print("✅ Acoustic features extracted successfully")
            print(f"   Pitch features: {len(features['pitch_features'])} items")
            print(f"   Speech rate: {features.get('speech_rate', 0)}")
            return True
        else:
            print("❌ No acoustic features extracted")
            return False
            
    except Exception as e:
        print(f"❌ Acoustic feature test failed: {e}")
        return False
    finally:
        # Clean up test file
        if 'audio_file' in locals() and os.path.exists(audio_file):
            os.unlink(audio_file)

def test_linguistic_features():
    """Test linguistic feature extraction"""
    print("🧪 Testing linguistic feature extraction...")
    
    try:
        from enhanced_feature_extractor import EnhancedFeatureExtractor
        extractor = EnhancedFeatureExtractor()
        
        # Test text
        test_text = "Hello, I am calling from SBI bank. Your account has been blocked due to suspicious activity. Please share your OTP immediately to unblock it."
        
        # Extract linguistic features
        features = extractor.extract_linguistic_features(test_text)
        
        # Check if features were extracted
        if features and 'ner_entities' in features:
            print("✅ Linguistic features extracted successfully")
            print(f"   NER entities: {len(features['ner_entities'])} categories")
            print(f"   Intent scores: {len(features['intent_scores'])} intents")
            print(f"   Sentiment analysis: {len(features['sentiment_analysis'])} models")
            return True
        else:
            print("❌ No linguistic features extracted")
            return False
            
    except Exception as e:
        print(f"❌ Linguistic feature test failed: {e}")
        return False

def test_integration():
    """Test integration with main detector"""
    print("🧪 Testing integration with main detector...")
    
    try:
        from complete_scam_detector import CompleteScamDetector
        
        # Initialize detector
        detector = CompleteScamDetector()
        print("✅ Complete Scam Detector initialized with enhanced features")
        
        # Check if feature extractor is available
        if hasattr(detector, 'feature_extractor') and detector.feature_extractor:
            print("✅ Enhanced Feature Extractor integrated successfully")
            return True
        else:
            print("⚠️ Enhanced Feature Extractor not integrated")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Voice Scam Detector - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("NLP Imports", test_nlp_imports),
        ("Enhanced Extractor", test_enhanced_extractor),
        ("Acoustic Features", test_acoustic_features),
        ("Linguistic Features", test_linguistic_features),
        ("Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features are ready to use.")
        print("\n📋 Next steps:")
        print("1. Run: python api_server.py")
        print("2. Test with real audio files")
        print("3. Check the dashboard for enhanced features")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
        print("You may need to:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Download models: python setup_enhanced.py")
        print("3. Check your environment setup")

if __name__ == "__main__":
    main()




