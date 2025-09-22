#!/usr/bin/env python3
"""
Startup script for Jira-Figma Analyzer
Handles errors gracefully and provides better logging
"""

import os
import sys
import traceback
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/app.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        # Ensure required directories exist
        os.makedirs('/app/logs', exist_ok=True)
        os.makedirs('/app/analysis_outputs', exist_ok=True)
        
        logger.info("Starting Jira-Figma Analyzer...")
        
        # Check environment variables
        openai_key = os.getenv('OPENAI_API_KEY')
        figma_token = os.getenv('FIGMA_ACCESS_TOKEN')
        
        if not openai_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            sys.exit(1)
        
        if not figma_token:
            logger.warning("FIGMA_ACCESS_TOKEN not found in environment variables")
        
        logger.info("Environment variables loaded successfully")
        
        # Test imports first
        logger.info("Testing imports...")
        try:
            import streamlit as st
            logger.info("✅ Streamlit imported successfully")
            
            # Test importing the main app
            import complete_streamlit_app
            logger.info("✅ complete_streamlit_app imported successfully")
            
        except Exception as e:
            logger.error(f"❌ Import failed: {str(e)}")
            traceback.print_exc()
            sys.exit(1)
        
        # Get port from environment
        port = int(os.getenv('PORT', 8501))
        logger.info(f"Starting Streamlit on port {port}")
        
        # Set Streamlit configuration
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
        os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
        
        # Import and run Streamlit
        import streamlit.web.cli as stcli
        
        # Run Streamlit
        sys.argv = [
            'streamlit', 'run', 
            'complete_streamlit_app.py',
            '--server.port', str(port),
            '--server.address', '0.0.0.0',
            '--server.headless', 'true',
            '--server.enableCORS', 'true',
            '--server.enableXsrfProtection', 'false'
        ]
        
        logger.info("Starting Streamlit with args: " + " ".join(sys.argv))
        stcli.main()
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
