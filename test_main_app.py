#!/usr/bin/env python3
"""
Test main app startup without GPT-4 Vision integration
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting main app test...")
    
    # Get port from Railway
    port = os.getenv('PORT', '8501')
    print(f"Using port: {port}")
    
    # Test imports step by step
    print("Testing basic imports...")
    try:
        import streamlit as st
        print("✅ Streamlit imported")
        
        from ticket_storage_system import TicketStorageSystem
        print("✅ Ticket storage imported")
        
        from jira_figma_analyzer import JiraFigmaAnalyzer
        print("✅ Main analyzer imported")
        
        # Test if we can create instances
        storage = TicketStorageSystem()
        print("✅ Storage system created")
        
        analyzer = JiraFigmaAnalyzer()
        print("✅ Analyzer created")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("✅ All basic imports successful!")
    
    # Run Streamlit with main app
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        'complete_streamlit_app.py',
        '--server.port', str(port),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
