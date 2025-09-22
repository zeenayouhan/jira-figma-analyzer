#!/usr/bin/env python3
"""
Add session state initialization to prevent data loss when switching tabs
"""

def add_session_state():
    # Read the current file
    with open('complete_streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Add session state initialization after the imports
    old_main = '''def main():
    """Main application function."""
    st.set_page_config(
        page_title="Jira-Figma Analyzer",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )'''
    
    new_main = '''def main():
    """Main application function."""
    st.set_page_config(
        page_title="Jira-Figma Analyzer",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state to prevent data loss
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'current_ticket' not in st.session_state:
        st.session_state.current_ticket = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'figma_url' not in st.session_state:
        st.session_state.figma_url = ""
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'show_all_tickets' not in st.session_state:
        st.session_state.show_all_tickets = False
    if 'confirm_delete_all' not in st.session_state:
        st.session_state.confirm_delete_all = False'''
    
    content = content.replace(old_main, new_main)
    
    # Write the updated content
    with open('complete_streamlit_app.py', 'w') as f:
        f.write(content)
    
    print("✅ Added session state initialization to prevent data loss")

if __name__ == "__main__":
    add_session_state()
