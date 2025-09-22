# Force rebuild: 2025-09-22T13:40:20.029292
#!/usr/bin/env python3
"""
Railway startup script for Jira-Figma Analyzer
Handles errors gracefully and provides better logging
"""

import os
import sys
import subprocess
import traceback

def main():
    print("🚀 Starting Jira-Figma Analyzer...")
    
    # Set environment variables
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    # Get port from Railway
    port = os.getenv('PORT', '8501')
    print(f"Using port: {port}")
    
    # Fix database schema before starting
    print("Fixing database schema...")
    try:
        from fix_database_schema import fix_database_schema
        fix_database_schema()
        print("✅ Database schema fixed")
    except Exception as e:
        print(f"⚠️ Database schema fix failed: {e}")
        traceback.print_exc()
    
    # Test imports
    print("Testing imports...")
    try:
        from complete_streamlit_app import main as app_main
        print("✅ Complete Streamlit app imported successfully")
    except Exception as e:
        print(f"❌ Error importing complete_streamlit_app: {e}")
        traceback.print_exc()
        return 1
    
    # Run Streamlit
    print("Starting Streamlit...")
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        'complete_streamlit_app.py',
        '--server.port', str(port),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'true'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit failed with exit code {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
