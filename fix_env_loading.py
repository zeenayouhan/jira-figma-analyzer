#!/usr/bin/env python3
"""
Add dotenv loading to the Streamlit app
"""

def fix_env_loading():
    # Read the current file
    with open('complete_streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Add dotenv loading after the imports
    old_imports = '''import streamlit as st
import json
import time
from datetime import datetime
from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket
from ticket_storage_system import TicketStorageSystem
from implemented_screens_manager import render_implemented_screens_ui
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from confluence_integration import ConfluenceIntegration
from feedback_system import FeedbackSystem
from media_analyzer import MediaAnalyzer
from persistent_feedback import PersistentFeedbackForm
import os
import tempfile
from pathlib import Path
import hashlib
import uuid'''
    
    new_imports = '''import streamlit as st
import json
import time
from datetime import datetime
from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket
from ticket_storage_system import TicketStorageSystem
from implemented_screens_manager import render_implemented_screens_ui
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from confluence_integration import ConfluenceIntegration
from feedback_system import FeedbackSystem
from media_analyzer import MediaAnalyzer
from persistent_feedback import PersistentFeedbackForm
import os
import tempfile
from pathlib import Path
import hashlib
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()'''
    
    content = content.replace(old_imports, new_imports)
    
    # Write the updated content
    with open('complete_streamlit_app.py', 'w') as f:
        f.write(content)
    
    print("✅ Added dotenv loading to Streamlit app")

if __name__ == "__main__":
    fix_env_loading()
