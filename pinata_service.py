#!/usr/bin/env python3
"""
Pinata IPFS service for storing audio files
"""
import os
import json
import base64
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PinataService:
    def __init__(self):
        """Initialize Pinata service with API credentials"""
        self.api_key = os.getenv('PINATA_API_KEY')
        self.api_secret = os.getenv('PINATA_API_SECRET')
        self.jwt_token = os.getenv('PINATA_JWT')
        
        if not self.jwt_token:
            raise ValueError("PINATA_JWT environment variable is required")
        
        self.base_url = "https://api.pinata.cloud"
        self.headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        print("✅ Pinata service initialized")
    
    def test_connection(self) -> bool:
        """Test Pinata API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/data/testAuthentication",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Pinata API connection successful")
                return True
            else:
                print(f"❌ Pinata API connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Pinata connection error: {e}")
            return False
    
    def upload_audio_file(self, audio_data: bytes, filename: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Upload audio file to Pinata IPFS
        
        Args:
            audio_data: Raw audio bytes
            filename: Name for the file
            metadata: Optional metadata to attach
            
        Returns:
            Dict with IPFS hash and other info, or None if failed
        """
        try:
            print(f"📤 Uploading audio file to Pinata: {filename}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Prepare files for upload
                files = {
                    'file': (filename, open(temp_file_path, 'rb'), 'audio/wav')
                }
                
                # Prepare metadata
                pinata_metadata = {
                    "name": filename,
                    "keyvalues": {
                        "type": "audio_analysis",
                        "uploaded_at": datetime.utcnow().isoformat(),
                        "file_size": len(audio_data)
                    }
                }
                
                # Add custom metadata if provided
                if metadata:
                    pinata_metadata["keyvalues"].update(metadata)
                
                # Prepare data
                data = {
                    'pinataMetadata': json.dumps(pinata_metadata),
                    'pinataOptions': json.dumps({
                        'cidVersion': 1,
                        'wrapWithDirectory': False
                    })
                }
                
                # Upload headers (different for file upload)
                upload_headers = {
                    "Authorization": f"Bearer {self.jwt_token}"
                }
                
                # Make upload request
                response = requests.post(
                    f"{self.base_url}/pinning/pinFileToIPFS",
                    files=files,
                    data=data,
                    headers=upload_headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ipfs_hash = result.get('IpfsHash')
                    
                    print(f"✅ Audio uploaded successfully to IPFS")
                    print(f"🔗 IPFS Hash: {ipfs_hash}")
                    print(f"🌐 IPFS URL: https://gateway.pinata.cloud/ipfs/{ipfs_hash}")
                    
                    return {
                        'success': True,
                        'ipfs_hash': ipfs_hash,
                        'ipfs_url': f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
                        'pinata_url': f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
                        'file_size': len(audio_data),
                        'filename': filename,
                        'upload_timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    print(f"❌ Pinata upload failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error uploading to Pinata: {e}")
            return None
    
    def upload_base64_audio(self, base64_audio: str, filename: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Upload base64 encoded audio to Pinata
        
        Args:
            base64_audio: Base64 encoded audio string
            filename: Name for the file
            metadata: Optional metadata
            
        Returns:
            Dict with IPFS hash and other info, or None if failed
        """
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(base64_audio)
            return self.upload_audio_file(audio_data, filename, metadata)
            
        except Exception as e:
            print(f"❌ Error decoding base64 audio: {e}")
            return None
    
    def get_file_info(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """Get information about a pinned file"""
        try:
            response = requests.get(
                f"{self.base_url}/data/pinList?hashContains={ipfs_hash}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('rows'):
                    return data['rows'][0]
                return None
            else:
                print(f"❌ Failed to get file info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting file info: {e}")
            return None
    
    def unpin_file(self, ipfs_hash: str) -> bool:
        """Unpin a file from Pinata"""
        try:
            response = requests.delete(
                f"{self.base_url}/pinning/unpin/{ipfs_hash}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ File unpinned successfully: {ipfs_hash}")
                return True
            else:
                print(f"❌ Failed to unpin file: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error unpinning file: {e}")
            return False

# Global instance
pinata_service = None

def get_pinata_service() -> PinataService:
    """Get or create Pinata service instance"""
    global pinata_service
    if pinata_service is None:
        pinata_service = PinataService()
    return pinata_service

def test_pinata_connection():
    """Test Pinata connection"""
    try:
        service = get_pinata_service()
        return service.test_connection()
    except Exception as e:
        print(f"❌ Pinata service initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Pinata service...")
    success = test_pinata_connection()
    if success:
        print("🎉 Pinata service is working!")
    else:
        print("💡 Check your PINATA_JWT in .env file")
