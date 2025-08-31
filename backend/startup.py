#!/usr/bin/env python3
"""
Lightweight startup script for Railway deployment.
Installs ML dependencies at runtime to avoid build timeouts.
"""
import subprocess
import sys
import os

def install_ml_packages():
    """Install ML packages at runtime if not available."""
    ml_packages = [
        "spacy>=3.4.0",
        "scikit-learn>=1.0.0", 
        "numpy>=1.21.0",
        "pandas>=1.3.0"
    ]
    
    for package in ml_packages:
        try:
            # Try to import the base package name
            pkg_name = package.split(">=")[0].replace("-", "_")
            if pkg_name == "scikit_learn":
                pkg_name = "sklearn"
            
            __import__(pkg_name)
            print(f"✓ {package.split('>=' )[0]} already available")
        except ImportError:
            print(f"⚠ Installing {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True, text=True)
                print(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {package}: {e}")

def download_spacy_model():
    """Download spaCy model if available."""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model 'en_core_web_sm' is available")
            return True
        except OSError:
            print("⚠ Downloading spaCy model...")
            try:
                subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                             check=True, capture_output=True, text=True, timeout=60)
                print("✓ spaCy model downloaded successfully")
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print("⚠ Could not download spaCy model, will use fallback")
                return False
    except ImportError:
        print("⚠ spaCy not available, will use fallback parsing")
        return False

def main():
    """Main startup function."""
    print("🚀 Starting GetPlaced API...")
    
    # Install ML packages at runtime
    install_ml_packages()
    
    # Try to download spaCy model (non-blocking)
    download_spacy_model()
    
    # Start the application
    port = int(os.environ.get("PORT", 8000))
    print(f"🌐 Starting server on port {port}")
    
    # Import and run uvicorn directly
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()