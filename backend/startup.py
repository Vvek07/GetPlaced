#!/usr/bin/env python3
"""
Startup script for Railway deployment to handle spaCy model download.
"""
import subprocess
import sys
import os

def download_spacy_model():
    """Download spaCy model if not already available."""
    try:
        import spacy
        # Try to load the model
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model 'en_core_web_sm' is already available")
            return True
        except OSError:
            print("⚠ spaCy model 'en_core_web_sm' not found, downloading...")
            # Download the model
            result = subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ spaCy model downloaded successfully")
                return True
            else:
                print(f"✗ Failed to download spaCy model: {result.stderr}")
                return False
    except ImportError:
        print("✗ spaCy not installed")
        return False

def main():
    """Main startup function."""
    print("🚀 Starting GetPlaced API...")
    
    # Download spaCy model
    model_ok = download_spacy_model()
    if not model_ok:
        print("⚠ Warning: spaCy model not available, some features may not work")
    
    # Start the application
    port = int(os.environ.get("PORT", 8000))
    print(f"🌐 Starting server on port {port}")
    
    # Import and run the main application
    from main import app
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()