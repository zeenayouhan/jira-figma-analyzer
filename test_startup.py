#!/usr/bin/env python3
"""
Test script to verify the app can start without errors
"""

import os
import sys

# Set environment variables for testing
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['FIGMA_ACCESS_TOKEN'] = 'test-token'

try:
    print("Testing imports...")
    
    # Test basic imports
    import streamlit as st
    print("✅ Streamlit imported successfully")
    
    # Test our modules
    from jira_figma_analyzer import JiraFigmaAnalyzer
    print("✅ JiraFigmaAnalyzer imported successfully")
    
    from ticket_storage_system import TicketStorageSystem
    print("✅ TicketStorageSystem imported successfully")
    
    # Test storage initialization
    storage = TicketStorageSystem()
    print("✅ Storage system initialized successfully")
    
    # Test analyzer initialization
    analyzer = JiraFigmaAnalyzer()
    print("✅ Analyzer initialized successfully")
    
    print("\n🎉 All tests passed! The app should start successfully.")
    
except Exception as e:
    print(f"❌ Error during testing: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
