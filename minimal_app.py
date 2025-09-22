#!/usr/bin/env python3
"""
Minimal test app for Railway deployment
"""

import streamlit as st
import os

def main():
    st.title("🚀 Jira-Figma Analyzer - Test")
    st.write("This is a minimal test to check if the app is working on Railway.")
    
    st.write(f"Port: {os.getenv('PORT', 'Not set')}")
    st.write(f"Python version: {os.sys.version}")
    
    st.success("✅ App is running successfully!")
    
    # Test basic functionality
    if st.button("Test Button"):
        st.balloons()

if __name__ == "__main__":
    main()
