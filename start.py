#!/usr/bin/env python3
"""
Railway startup script for Jira-Figma Analyzer
Handles errors gracefully and provides better logging
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
    
    # Get port from Railway - handle both PORT and STREAMLIT_SERVER_PORT
    port = os.getenv('PORT') or os.getenv('STREAMLIT_SERVER_PORT', '8501')
    
    print(f"Starting Jira-Figma Analyzer on port {port}")
    print(f"Environment variables: PORT={os.getenv('PORT')}, STREAMLIT_SERVER_PORT={os.getenv('STREAMLIT_SERVER_PORT')}")
    
    # Fix database schema before starting
    print("Fixing database schema...")
    try:
        from fix_database_schema import fix_database_schema
        fix_database_schema()
        print("✅ Database schema fixed")
    except Exception as e:
        print(f"⚠️ Database schema fix failed: {e}")
    
    # Run Streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        'complete_streamlit_app.py',
        '--server.port', str(port),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'true'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
