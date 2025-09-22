#!/usr/bin/env python3
"""
Minimal Streamlit app for testing
"""

import streamlit as st
import os

st.title("Minimal Test App")
st.write("This is a minimal test app to verify Streamlit works.")

# Add a simple health check endpoint
if st.button("Test Health Check"):
    st.success("Health check passed!")

st.write(f"Port: {os.getenv('PORT', '8501')}")
st.write(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
