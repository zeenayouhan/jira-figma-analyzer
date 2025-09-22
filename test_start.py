#!/usr/bin/env python3
"""
Test startup script for Railway
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting minimal test app...")
    
    # Get port from Railway
    port = os.getenv('PORT', '8501')
    print(f"Using port: {port}")
    
    # Run minimal Streamlit app
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        'minimal_app.py',
        '--server.port', str(port),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
