#!/usr/bin/env python3
"""
Railway startup script for Jira-Figma Analyzer
"""

import os
import sys
import subprocess

def main():
    # Set environment variables
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    # Get port from Railway
    port = os.getenv('PORT', '8501')
    
    print(f"Starting Jira-Figma Analyzer on port {port}")
    
    # Run Streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        'complete_streamlit_app.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'true'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
