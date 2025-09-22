#!/usr/bin/env python3
"""
Simple test app to debug Railway deployment issues
"""

import os
import sys

def main():
    print("🚀 Starting test app...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Environment variables: {dict(os.environ)}")
    
    try:
        print("Testing imports...")
        from complete_streamlit_app import main as app_main
        print("✅ Complete Streamlit app imported successfully")
        
        from gpt4_vision_integration import VisualAnalysisResult
        print("✅ GPT-4 Vision integration imported successfully")
        
        from ticket_storage_system import TicketStorageSystem
        print("✅ Ticket storage system imported successfully")
        
        print("✅ All imports successful!")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("✅ Test app completed successfully")
    return 0

if __name__ == "__main__":
    exit(main())
