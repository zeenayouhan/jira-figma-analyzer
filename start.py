#!/usr/bin/env python3
"""
Startup script for Railway deployment
"""
import os
import subprocess
import sys

def main():
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Get port from Railway
    port = os.environ.get('PORT', '8501')
    
    # Start Streamlit
    cmd = [
        'streamlit', 'run', 'complete_streamlit_app.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ]
    
    print(f"🚀 Starting Jira-Figma Analyzer on port {port}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
