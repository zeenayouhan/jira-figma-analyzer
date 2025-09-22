#!/usr/bin/env python3

import streamlit as st
import json
import time
from datetime import datetime
from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket
from ticket_storage_system import TicketStorageSystem
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from confluence_integration import ConfluenceIntegration

def safe_get(obj, key, default=None):
    """Safely get a value from an object, handling all data types."""
    if obj is None:
        return default
    if isinstance(obj, str):
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    if hasattr(obj, 'get'):
        return obj.get(key, default)
    if hasattr(obj, key):
        return getattr(obj, key, default)
    return default

def main():
    st.set_page_config(
        page_title="Jira-Figma Analyzer",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Jira-Figma Analyzer")
    st.markdown("Analyze Jira tickets with Figma designs and generate relevant questions.")
    
    # Initialize components
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = JiraFigmaAnalyzer()
    if 'storage' not in st.session_state:
        st.session_state.storage = TicketStorageSystem()
    
    analyzer = st.session_state.analyzer
    storage = st.session_state.storage
    
    # Main analysis section
    st.header("🎯 Analyze Tickets")
    
    # Manual entry form
    with st.form("ticket_analysis_form"):
        st.subheader("📝 Enter Ticket Details")
        
        col1, col2 = st.columns(2)
        with col1:
            ticket_key = st.text_input("Ticket Key", value="TEST-123", help="Jira ticket key (e.g., PROJ-123)")
            title = st.text_input("Title", value="Enable Editing of Occupation, Country of Residence on User Profile", help="Ticket title")
        
        with col2:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=0)
            status = st.selectbox("Status", ["Open", "In Progress", "Done"], index=0)
        
        description = st.text_area(
            "Description", 
            value="""Acceptance Criteria

Given the user is on the Profile tab,
When they click the Edit button next to Occupation, Country of Residence,
Then a dropdown should appear allowing them to select from a predefined list (same as used in onboarding).

Given the user selects a value from the Occupation, Country of Residence dropdown,
When the selection is made,
Then the new value should be saved to the database in real time.

Given that a user successfully updates either Occupation or Country of Residence,
When the update completes,
Then a Mixpanel event may be fired to track the change (optional / nice to have).""",
            help="Ticket description and acceptance criteria"
        )
        
        figma_url = st.text_input(
            "Figma URL", 
            value="https://www.figma.com/design/fnCxddHpd5tOcjYxzliAxc/Habitto-App-UI--Sprint-Execution?node-id=137944-173127&t=ODpn76sHLlg6eDUQ-0",
            help="Figma design URL"
        )
        
        auto_store = st.checkbox("Auto-store results", value=True, help="Automatically store analysis results")
        
        submitted = st.form_submit_button("🔍 Analyze Ticket", type="primary")
        
        if submitted:
            try:
                # Create ticket data
                ticket_data = {
                    'key': ticket_key,
                    'summary': title,
                    'description': description,
                    'comments': [],
                    'priority': {'name': priority},
                    'assignee': {'displayName': 'Test User'},
                    'reporter': {'displayName': 'Test Reporter'},
                    'status': {'name': status},
                    'labels': [],
                    'components': [],
                    'pdf_design_files': [],
                    'figma_links': [figma_url] if figma_url else []
                }
                
                st.write("🔍 **Debug Info:**")
                st.write(f"- Ticket data type: {type(ticket_data)}")
                st.write(f"- Ticket data keys: {list(ticket_data.keys())}")
                
                with st.spinner("🔍 Analyzing ticket..."):
                    # Parse ticket
                    ticket = analyzer.parse_jira_ticket(ticket_data)
                    st.write(f"- Parsed ticket type: {type(ticket)}")
                    st.write(f"- Parsed ticket title: {ticket.title}")
                    
                    # Analyze with context
                    result = analyzer.analyze_ticket_content(ticket)
                    st.write(f"- Analysis result type: {type(result)}")
                    st.write(f"- Analysis result attributes: {dir(result)}")
                    
                    # Generate report
                    report = analyzer.generate_report(result)
                    st.write(f"- Report generated: {len(report)} characters")
                
                # Store results if enabled
                stored_ticket_id = None
                if auto_store:
                    try:
                        stored_ticket_id = storage.store_ticket(ticket_data)
                        st.success(f"✅ Analysis stored with ID: {stored_ticket_id}")
                    except Exception as e:
                        st.warning(f"⚠️ Failed to store analysis: {e}")
                
                # Display results
                st.success("✅ Analysis completed successfully!")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Questions Generated", len(result.suggested_questions + result.design_questions + result.business_questions))
                with col2:
                    st.metric("Test Cases", len(result.test_cases))
                with col3:
                    st.metric("Risk Areas", len(result.risk_areas))
                with col4:
                    st.metric("Technical Considerations", len(result.technical_considerations))
                
                # Display questions
                st.header("❓ Generated Questions")
                
                if result.suggested_questions:
                    st.subheader("🔹 General Questions")
                    for i, question in enumerate(result.suggested_questions, 1):
                        st.write(f"{i}. {question}")
                
                if result.design_questions:
                    st.subheader("🎨 Design Questions")
                    for i, question in enumerate(result.design_questions, 1):
                        st.write(f"{i}. {question}")
                
                if result.business_questions:
                    st.subheader("💼 Business Questions")
                    for i, question in enumerate(result.business_questions, 1):
                        st.write(f"{i}. {question}")
                
                # Display test cases
                if result.test_cases:
                    st.header("🧪 Test Cases")
                    for i, test_case in enumerate(result.test_cases, 1):
                        st.write(f"{i}. {test_case}")
                
                # Display risk areas
                if result.risk_areas:
                    st.header("⚠️ Risk Areas")
                    for i, risk in enumerate(result.risk_areas, 1):
                        st.write(f"{i}. {risk}")
                
                # Display technical considerations
                if result.technical_considerations:
                    st.header("🔧 Technical Considerations")
                    for i, consideration in enumerate(result.technical_considerations, 1):
                        st.write(f"{i}. {consideration}")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
                st.write("**Full traceback:**")
                import traceback
                st.code(traceback.format_exc())
                
                if st.checkbox("Show debug info"):
                    st.write("**Debug Information:**")
                    st.write(f"- Error type: {type(e)}")
                    st.write(f"- Error message: {str(e)}")
                    st.write(f"- Ticket data: {ticket_data}")

if __name__ == "__main__":
    main()
