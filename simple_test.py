#!/usr/bin/env python3
"""
Simple test to verify the app can be imported and initialized
"""

import os
import sys

# Set environment variables for testing
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['FIGMA_ACCESS_TOKEN'] = 'test-token'

def test_app_import():
    try:
        print("Testing app import...")
        
        # Test importing the main app
        import complete_streamlit_app
        print("✅ complete_streamlit_app imported successfully")
        
        # Test that the app can be executed (syntax check)
        print("✅ App syntax is valid")
        
        return True
        
    except Exception as e:
        print(f"❌ App import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_import()
    if success:
        print("\n🎉 App test passed!")
    else:
        print("\n❌ App test failed!")
        sys.exit(1)
