#!/usr/bin/env python3
"""
Package installation script to fix transformers/huggingface_hub compatibility
"""

import subprocess
import sys

def install_packages():
    """Install packages with correct versions"""
    print("🔧 Fixing package compatibility issues...")
    
    # Uninstall conflicting packages
    packages_to_uninstall = [
        "transformers",
        "huggingface_hub", 
        "accelerate",
        "torch",
        "torchaudio"
    ]
    
    print("🗑️ Uninstalling conflicting packages...")
    for package in packages_to_uninstall:
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", package, "-y"], 
                         check=False, capture_output=True)
            print(f"   ✅ Uninstalled {package}")
        except:
            print(f"   ⚠️ Could not uninstall {package}")
    
    # Install compatible versions
    print("\n📦 Installing compatible versions...")
    
    packages_to_install = [
        "torch==2.1.0",
        "torchaudio==2.1.0", 
        "huggingface_hub>=0.19.0",
        "accelerate>=0.24.0",
        "transformers==4.35.0",
        "librosa==0.10.1",
        "soundfile==0.12.1"
    ]
    
    for package in packages_to_install:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"   ✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
    
    print("\n🎯 Package installation complete!")
    print("💡 Try running: python api_server.py")

if __name__ == "__main__":
    install_packages()
