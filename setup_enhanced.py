#!/usr/bin/env python3
"""
Setup script for Enhanced Voice Scam Detector
Installs required models and dependencies
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_python_packages():
    """Install Python packages from requirements.txt"""
    print("📦 Installing Python packages...")
    
    # Install main requirements
    if not run_command("pip install -r requirements.txt", "Installing main requirements"):
        return False
    
    # Install additional packages that might be needed
    additional_packages = [
        "librosa[display]",  # librosa with display support
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",  # CPU-only PyTorch
    ]
    
    for package in additional_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️ Failed to install {package}, continuing...")
    
    return True

def download_spacy_model():
    """Download spaCy English model"""
    print("📚 Downloading spaCy English model...")
    
    try:
        import spacy
        # Try to load the model first
        try:
            spacy.load("en_core_web_sm")
            print("✅ spaCy English model already installed")
            return True
        except OSError:
            # Model not found, download it
            if run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
                return True
            else:
                print("⚠️ spaCy model download failed, but continuing...")
                return False
    except ImportError:
        print("⚠️ spaCy not installed, skipping model download")
        return False

def download_nltk_data():
    """Download NLTK data"""
    print("📚 Downloading NLTK data...")
    
    try:
        import nltk
        nltk_data = [
            'punkt',
            'vader_lexicon',
            'stopwords',
            'averaged_perceptron_tagger',
            'maxent_ne_chunker',
            'words'
        ]
        
        for data in nltk_data:
            try:
                nltk.download(data, quiet=True)
                print(f"✅ Downloaded NLTK {data}")
            except Exception as e:
                print(f"⚠️ Failed to download NLTK {data}: {e}")
        
        return True
    except ImportError:
        print("⚠️ NLTK not installed, skipping data download")
        return False

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    
    try:
        # Test basic imports
        import librosa
        import webrtcvad
        import numpy as np
        import pandas as pd
        import scipy
        import sklearn
        print("✅ Basic libraries imported successfully")
        
        # Test enhanced feature extractor
        from enhanced_feature_extractor import EnhancedFeatureExtractor
        extractor = EnhancedFeatureExtractor()
        print("✅ Enhanced Feature Extractor initialized successfully")
        
        # Test with sample data
        sample_text = "Hello, I am calling from SBI bank. Your account has been blocked."
        linguistic_features = extractor.extract_linguistic_features(sample_text)
        print("✅ Linguistic feature extraction test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Enhanced Voice Scam Detector")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install packages
    if not install_python_packages():
        print("❌ Package installation failed")
        sys.exit(1)
    
    # Download models
    download_spacy_model()
    download_nltk_data()
    
    # Test installation
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Make sure you have Google Cloud credentials set up")
        print("2. Set your GEMINI_API_KEY in .env file")
        print("3. Run: python api_server.py")
        print("4. Run: npm run dev (in voice-scam-dashboard folder)")
    else:
        print("\n❌ Setup completed with errors")
        print("Some features may not work properly")
        print("Check the error messages above for details")

if __name__ == "__main__":
    main()




