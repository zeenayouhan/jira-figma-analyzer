#!/usr/bin/env python3
"""
Test script to verify Streamlit can start and respond
"""

import os
import sys
import time
import threading
import requests
from urllib.parse import urljoin

# Set environment variables for testing
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['FIGMA_ACCESS_TOKEN'] = 'test-token'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'

def test_streamlit_startup():
    try:
        print("Testing Streamlit startup...")
        
        # Import streamlit
        import streamlit.web.cli as stcli
        
        # Set up args
        sys.argv = [
            'streamlit', 'run', 
            'complete_streamlit_app.py',
            '--server.port', '8502',
            '--server.address', '0.0.0.0',
            '--server.headless', 'true',
            '--server.enableCORS', 'true'
        ]
        
        print("Starting Streamlit in background...")
        
        # Start Streamlit in a thread
        def run_streamlit():
            stcli.main()
        
        thread = threading.Thread(target=run_streamlit, daemon=True)
        thread.start()
        
        # Wait for startup
        print("Waiting for Streamlit to start...")
        time.sleep(10)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:8502/_stcore/health', timeout=5)
            if response.status_code == 200:
                print("✅ Health check passed!")
                return True
            else:
                print(f"❌ Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Streamlit startup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_streamlit_startup()
    if success:
        print("\n🎉 Streamlit test passed!")
    else:
        print("\n❌ Streamlit test failed!")
        sys.exit(1)
