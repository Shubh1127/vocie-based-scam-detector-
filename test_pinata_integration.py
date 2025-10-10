#!/usr/bin/env python3
"""
Test Pinata IPFS integration
"""
import os
import base64
from dotenv import load_dotenv
from pinata_service import get_pinata_service, test_pinata_connection

# Load environment variables
load_dotenv()

def test_pinata_upload():
    """Test uploading a sample audio file to Pinata"""
    print("🧪 Testing Pinata IPFS Integration")
    print("=" * 50)
    
    # Test connection first
    print("1. Testing Pinata connection...")
    if not test_pinata_connection():
        print("❌ Pinata connection failed. Check your PINATA_JWT in .env")
        return False
    
    # Get Pinata service
    try:
        pinata_service = get_pinata_service()
        print("✅ Pinata service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Pinata service: {e}")
        return False
    
    # Create a dummy audio file (WAV format)
    print("\n2. Creating dummy audio data...")
    dummy_audio_data = create_dummy_wav()
    
    if not dummy_audio_data:
        print("❌ Failed to create dummy audio data")
        return False
    
    print(f"✅ Created dummy audio data: {len(dummy_audio_data)} bytes")
    
    # Test upload
    print("\n3. Testing audio upload to Pinata...")
    metadata = {
        "test": "true",
        "purpose": "integration_test",
        "risk_score": 0.75,
        "scam_detected": True
    }
    
    result = pinata_service.upload_audio_file(
        dummy_audio_data, 
        "test_audio_analysis.wav", 
        metadata
    )
    
    if result:
        print("✅ Upload successful!")
        print(f"🔗 IPFS Hash: {result['ipfs_hash']}")
        print(f"🌐 IPFS URL: {result['ipfs_url']}")
        print(f"📊 File Size: {result['file_size']} bytes")
        print(f"📅 Upload Time: {result['upload_timestamp']}")
        
        # Test getting file info
        print("\n4. Testing file info retrieval...")
        file_info = pinata_service.get_file_info(result['ipfs_hash'])
        if file_info:
            print("✅ File info retrieved successfully")
            print(f"📝 File Name: {file_info.get('metadata', {}).get('name', 'N/A')}")
        else:
            print("⚠️ Could not retrieve file info")
        
        return True
    else:
        print("❌ Upload failed")
        return False

def create_dummy_wav():
    """Create a dummy WAV file for testing"""
    try:
        import wave
        import struct
        import math
        
        # WAV file parameters
        sample_rate = 16000
        duration = 2  # 2 seconds
        frequency = 440  # A4 note
        
        # Generate sine wave
        samples = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            samples.append(struct.pack('<h', value))
        
        # Create WAV file in memory
        import io
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(samples))
        
        wav_buffer.seek(0)
        return wav_buffer.read()
        
    except Exception as e:
        print(f"❌ Error creating dummy WAV: {e}")
        return None

def test_base64_upload():
    """Test uploading base64 encoded audio"""
    print("\n5. Testing base64 audio upload...")
    
    # Create dummy audio
    dummy_audio = create_dummy_wav()
    if not dummy_audio:
        return False
    
    # Encode to base64
    base64_audio = base64.b64encode(dummy_audio).decode('utf-8')
    
    # Upload via base64 method
    pinata_service = get_pinata_service()
    result = pinata_service.upload_base64_audio(
        base64_audio,
        "test_base64_audio.wav",
        {"test_type": "base64_upload"}
    )
    
    if result:
        print("✅ Base64 upload successful!")
        print(f"🔗 IPFS Hash: {result['ipfs_hash']}")
        return True
    else:
        print("❌ Base64 upload failed")
        return False

if __name__ == "__main__":
    print("🚀 Starting Pinata Integration Tests")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['PINATA_JWT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Add them to your .env file:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        exit(1)
    
    # Run tests
    success = test_pinata_upload()
    
    if success:
        test_base64_upload()
        print("\n🎉 All Pinata tests completed successfully!")
    else:
        print("\n❌ Pinata tests failed!")
        print("💡 Troubleshooting tips:")
        print("1. Check your PINATA_JWT in .env file")
        print("2. Verify your Pinata API key has upload permissions")
        print("3. Check your internet connection")
        print("4. Try regenerating your JWT token in Pinata dashboard")
