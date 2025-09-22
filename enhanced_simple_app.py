#!/usr/bin/env python3

import streamlit as st
import json
import time
from datetime import datetime
from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket
from ticket_storage_system import TicketStorageSystem
from confluence_integration import ConfluenceIntegration
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    if 'confluence' not in st.session_state:
        st.session_state.confluence = ConfluenceIntegration()
    
    analyzer = st.session_state.analyzer
    storage = st.session_state.storage
    confluence = st.session_state.confluence
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🎯 Analyze Tickets", "🔍 Search & Browse", "📊 Analytics", "📚 Confluence Docs", "🔍 Screen Explorer"]
    )
    
    if page == "🎯 Analyze Tickets":
        analyze_tickets_page(analyzer, storage)
    elif page == "🔍 Search & Browse":
        search_browse_page(storage)
    elif page == "📊 Analytics":
        analytics_page(storage)
    elif page == "📚 Confluence Docs":
        confluence_docs_page(confluence)
    elif page == "🔍 Screen Explorer":
        screen_explorer_page(analyzer)

def analyze_tickets_page(analyzer, storage):
    """Main ticket analysis page."""
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
            analyze_ticket(analyzer, storage, ticket_key, title, description, figma_url, auto_store)

def analyze_ticket(analyzer, storage, ticket_key, title, description, figma_url, auto_store):
    """Analyze a single ticket."""
    try:
        # Create ticket data
        ticket_data = {
            'key': ticket_key,
            'summary': title,
            'description': description,
            'comments': [],
            'priority': {'name': 'High'},
            'assignee': {'displayName': 'Test User'},
            'reporter': {'displayName': 'Test Reporter'},
            'status': {'name': 'Open'},
            'labels': [],
            'components': [],
            'pdf_design_files': [],
            'figma_links': [figma_url] if figma_url else []
        }
        
        with st.spinner("🔍 Analyzing ticket..."):
            # Parse ticket
            ticket = analyzer.parse_jira_ticket(ticket_data)
            
            # Analyze with context
            result = analyzer.analyze_ticket_content(ticket)
            
            # Generate report
            report = analyzer.generate_report(result)
        
        # Store results if enabled
        stored_ticket_id = None
        if auto_store:
            try:
                # Include analysis results in storage
                storage_data = {
                    "id": ticket.ticket_id,
                    "ticket_key": ticket.ticket_id,
                    "title": ticket.title,
                    "description": ticket.description,
                    "analysis": {
                        "suggested_questions": result.suggested_questions,
                        "design_questions": result.design_questions,
                        "business_questions": result.business_questions,
                        "technical_considerations": result.technical_considerations,
                        "risk_areas": result.risk_areas,
                        "test_cases": result.test_cases
                    }
                }
                stored_ticket_id = storage.store_ticket(storage_data)
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
        if st.checkbox("Show debug info"):
            import traceback
            st.code(traceback.format_exc())

def search_browse_page(storage):
    """Search and browse stored tickets."""
    st.header("🔍 Search & Browse")
    
    # Search functionality
    search_query = st.text_input("🔍 Search tickets", placeholder="Enter keywords to search...")
    search_type = st.selectbox("Type", ["All", "Questions", "Risks", "Content"])
    
    if st.button("Search"):
        if search_query:
            try:
                if search_type == "All":
                    results = storage.search_tickets(search_query)
                elif search_type == "Questions":
                    results = storage.search_tickets(search_query)  # Simplified for now
                else:
                    results = storage.search_tickets(search_query)
                
                if results:
                    st.success(f"Found {len(results)} results")
                    for result in results:
                        with st.expander(f"🎫 {safe_get(result, 'ticket_key', 'Unknown')} - {safe_get(result, 'title', 'No title')[:50]}..."):
                            st.markdown(f"**Description:** {safe_get(result, 'description', 'No description')[:200]}...")
                            st.markdown(f"**Stored:** {safe_get(result, 'created_at', 'Unknown date')}")
                else:
                    st.info("No results found")
            except Exception as e:
                st.error(f"Search error: {e}")
    
    # Browse all tickets
    st.subheader("📋 All Stored Tickets")
    try:
        all_tickets = storage.get_all_tickets(limit=20)
        if all_tickets:
            for ticket in all_tickets:
                with st.expander(f"🎫 {safe_get(ticket, 'ticket_key', 'Unknown')} - {safe_get(ticket, 'title', 'No title')[:50]}..."):
                    st.markdown(f"**Created:** {safe_get(ticket, 'created_at', 'Unknown')}")
                    st.markdown(f"**Description:** {safe_get(ticket, 'description', 'No description')[:200]}...")
        else:
            st.info("No tickets stored yet")
    except Exception as e:
        st.error(f"Error loading tickets: {e}")

def analytics_page(storage):
    """Analytics and statistics page."""
    st.header("📊 Analytics")
    
    try:
        stats = storage.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets", stats.get('total_tickets', 0))
        with col2:
            st.metric("Total Questions", stats.get('total_questions', 0))
        with col3:
            st.metric("Total Test Cases", stats.get('total_test_cases', 0))
        with col4:
            st.metric("Storage Size", f"{stats.get('storage_size', 0) / 1024:.1f} KB")
        
        # Simple charts
        if stats.get('total_tickets', 0) > 0:
            st.subheader("📈 Ticket Analysis Trends")
            
            # Mock data for demonstration
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
            ticket_counts = [stats.get('total_tickets', 0) // 12] * 12
            
            df = pd.DataFrame({
                'Month': dates.strftime('%Y-%m'),
                'Tickets': ticket_counts
            })
            
            fig = px.line(df, x='Month', y='Tickets', title='Tickets Analyzed Over Time')
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Analytics error: {e}")

def confluence_docs_page(confluence):
    """Confluence documents page."""
    st.header("📚 Confluence Documents")
    
    st.info("Confluence integration is available. Upload documents to build knowledge base.")
    
    # Document upload
    uploaded_files = st.file_uploader(
        "Upload Confluence Documents",
        type=['html', 'md', 'txt', 'pdf'],
        accept_multiple_files=True,
        help="Upload HTML, Markdown, TXT, or PDF files from Confluence"
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} files")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size} bytes)")
    
    # Show existing documents
    try:
        documents = confluence.get_all_documents()
        if documents:
            st.subheader("📄 Processed Documents")
            for doc in documents[:10]:  # Show first 10
                with st.expander(f"📄 {safe_get(doc, 'title', 'Untitled')}"):
                    st.markdown(f"**Type:** {safe_get(doc, 'type', 'Unknown')}")
                    st.markdown(f"**Size:** {len(safe_get(doc, 'content', ''))} characters")
        else:
            st.info("No documents processed yet")
    except Exception as e:
        st.error(f"Error loading documents: {e}")

def screen_explorer_page(analyzer):
    """Screen explorer for Figma designs."""
    st.header("🔍 Screen Explorer")
    st.markdown("Enter any Figma URL to explore screens and their components.")
    
    # Figma URL input
    figma_url = st.text_input(
        "Figma URL", 
        placeholder="https://www.figma.com/design/YOUR_FILE_KEY/Your-Design-Name",
        help="Enter a Figma design URL to analyze all screens and their components"
    )
    
    if st.button("🔍 Analyze Figma Design", type="primary"):
        if not figma_url:
            st.warning("Please enter a Figma URL")
            return
            
        try:
            with st.spinner("Analyzing Figma design..."):
                # Analyze the design
                design = analyzer.figma_integration.analyze_figma_design(figma_url)
                if not design:
                    st.error("❌ Failed to analyze Figma design")
                    return
            
            # Display overall design info
            st.success("✅ Design analyzed successfully!")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Screens", len(design.screens))
            with col2:
                st.metric("Total Components", len(design.ui_components))
            with col3:
                total_fields = sum(safe_get(screen, 'field_count', 0) for screen in design.screen_details if isinstance(screen, dict))
                st.metric("Total Form Fields", total_fields)
            with col4:
                total_ctas = sum(safe_get(screen, 'cta_count', 0) for screen in design.screen_details if isinstance(screen, dict))
                st.metric("Total CTAs", total_ctas)
            
            # Display design overview
            with st.expander("📋 Design Overview", expanded=True):
                st.write(f"**Design Name:** {design.name}")
                st.write(f"**Complexity Score:** {design.complexity_score:.1f}/10")
                st.write(f"**Pages:** {len(design.pages)}")
            
            # Screen-by-screen analysis
            if design.screen_details:
                st.header("📱 Screen Analysis")
                
                for i, screen in enumerate(design.screen_details):
                    if isinstance(screen, dict):
                        screen_name = safe_get(screen, 'screen', f'Screen {i+1}')
                        
                        with st.expander(f"🖼️ {screen_name}", expanded=i < 3):
                            # Show natural description if available
                            if safe_get(screen, 'description'):
                                st.markdown(f"**📝 {screen_name}**: {safe_get(screen, 'description')}")
                                st.markdown("---")
                            
                            # Show technical summary
                            st.markdown(f"**Summary:** {safe_get(screen, 'summary', 'No summary available')}")
                            
                            # Show field and CTA counts
                            if safe_get(screen, 'field_count', 0) > 0 or safe_get(screen, 'cta_count', 0) > 0:
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("Form Fields", safe_get(screen, 'field_count', 0))
                                with col_b:
                                    st.metric("CTAs", safe_get(screen, 'cta_count', 0))
                    else:
                        # Handle string screen names
                        with st.expander(f"🖼️ {screen}", expanded=i < 3):
                            st.markdown(f"**📝 {screen}**: Screen identified from Figma design")
            else:
                st.info("No detailed screen information available")
                
        except Exception as e:
            st.error(f"❌ Error analyzing Figma design: {e}")

if __name__ == "__main__":
    main()
