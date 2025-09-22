#!/usr/bin/env python3
"""
Streamlit Web Interface for Jira Figma Analyzer

A user-friendly web interface to analyze Jira tickets with Figma links
and get suggestions for questions and clarifications.
"""

import streamlit as st
import json
from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket
from implemented_screens_manager import render_implemented_screens_ui

def main():
    st.set_page_config(
        page_title="Jira Figma Analyzer",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎯 Jira Figma Analyzer")
    st.markdown("Analyze Jira tickets with Figma links and get suggestions for questions and clarifications.")
    
    # Main navigation
    main_tab = st.radio("Choose a section:", ["🎯 Analyze Tickets", "🏗️ Manage Implemented Screens"], horizontal=True)
    st.markdown("---")
    
    if main_tab == "🎯 Analyze Tickets":
        analyze_tickets_section()
    else:
        render_implemented_screens_ui()

def analyze_tickets_section():
    """Main ticket analysis section."""
    # Initialize analyzer
    analyzer = JiraFigmaAnalyzer()
    
    # Sidebar for input method
    st.sidebar.header("Input Method")
    input_method = st.sidebar.radio(
        "Choose how to input ticket data:",
        ["Manual Entry", "JSON Import", "Quick Template"]
    )
    
    if input_method == "Manual Entry":
        manual_entry_form(analyzer)
    elif input_method == "JSON Import":
        json_import_form(analyzer)
    else:
        quick_template_form(analyzer)

def manual_entry_form(analyzer):
    """Manual entry form for ticket data."""
    st.header("📝 Manual Ticket Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticket_id = st.text_input("Ticket ID", placeholder="e.g., PROJ-123")
        title = st.text_input("Title", placeholder="e.g., Implement new user dashboard")
        priority = st.selectbox("Priority", ["", "Low", "Medium", "High", "Critical"])
        assignee = st.text_input("Assignee", placeholder="e.g., John Doe")
        reporter = st.text_input("Reporter", placeholder="e.g., Jane Smith")
    
    with col2:
        labels = st.text_input("Labels (comma-separated)", placeholder="e.g., frontend, dashboard, ui")
        components = st.text_input("Components (comma-separated)", placeholder="e.g., User Interface, Backend")
        figma_links = st.text_area("Figma Links (one per line)", placeholder="https://www.figma.com/file/...")
    
    description = st.text_area("Description", height=150, placeholder="Enter the ticket description here...")
    
    if st.button("Analyze Ticket", type="primary"):
        if not title or not description:
            st.error("Please provide at least a title and description.")
            return
        
        # Parse inputs
        labels_list = [label.strip() for label in labels.split(",") if label.strip()]
        components_list = [comp.strip() for comp in components.split(",") if comp.strip()]
        figma_links_list = [link.strip() for link in figma_links.split("\n") if link.strip()]
        
        # Create ticket data
        ticket_data = {
            'key': ticket_id or 'TICKET-001',
            'summary': title,
            'description': description,
            'priority': {'name': priority} if priority else {},
            'assignee': {'displayName': assignee} if assignee else {},
            'reporter': {'displayName': reporter} if reporter else {},
            'labels': labels_list,
            'components': [{'name': comp} for comp in components_list],
            'comments': []
        }
        
        # Add Figma links to description if provided
        if figma_links_list:
            ticket_data['description'] += "\n\nFigma Links:\n" + "\n".join(figma_links_list)
        
        analyze_and_display(analyzer, ticket_data)

def json_import_form(analyzer):
    """JSON import form for ticket data."""
    st.header("📄 JSON Import")
    
    st.markdown("""
    Paste your Jira ticket JSON data below. The JSON should contain the following fields:
    - `key`: Ticket ID
    - `summary`: Ticket title
    - `description`: Ticket description
    - `priority`: Priority object with `name` field
    - `assignee`: Assignee object with `displayName` field
    - `reporter`: Reporter object with `displayName` field
    - `labels`: Array of label strings
    - `components`: Array of component objects with `name` field
    - `comments`: Array of comment objects
    """)
    
    json_data = st.text_area("JSON Data", height=300, placeholder='{"key": "PROJ-123", "summary": "...", ...}')
    
    if st.button("Analyze JSON", type="primary"):
        if not json_data.strip():
            st.error("Please provide JSON data.")
            return
        
        try:
            ticket_data = json.loads(json_data)
            analyze_and_display(analyzer, ticket_data)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {e}")

def quick_template_form(analyzer):
    """Quick template form with predefined examples."""
    st.header("⚡ Quick Template")
    
    template = st.selectbox(
        "Choose a template:",
        [
            "Dashboard Implementation",
            "Mobile App Feature",
            "API Integration",
            "E-commerce Feature",
            "Custom Template"
        ]
    )
    
    if template == "Dashboard Implementation":
        ticket_data = {
            'key': 'DASH-001',
            'summary': 'Implement new user dashboard with responsive design',
            'description': 'Create a new dashboard for users to view their data, charts, and analytics. Should be mobile-friendly and include real-time updates. Figma link: https://www.figma.com/file/abc123/dashboard-design',
            'priority': {'name': 'High'},
            'assignee': {'displayName': 'Frontend Team'},
            'reporter': {'displayName': 'Product Manager'},
            'labels': ['frontend', 'dashboard', 'responsive'],
            'components': [{'name': 'User Interface'}],
            'comments': []
        }
    elif template == "Mobile App Feature":
        ticket_data = {
            'key': 'MOBILE-001',
            'summary': 'Add push notification feature to mobile app',
            'description': 'Implement push notifications for user engagement. Should work on both iOS and Android. Include settings for users to manage notification preferences. Figma link: https://www.figma.com/file/def456/notification-ui',
            'priority': {'name': 'Medium'},
            'assignee': {'displayName': 'Mobile Team'},
            'reporter': {'displayName': 'UX Designer'},
            'labels': ['mobile', 'notifications', 'ios', 'android'],
            'components': [{'name': 'Mobile App'}],
            'comments': []
        }
    elif template == "API Integration":
        ticket_data = {
            'key': 'API-001',
            'summary': 'Integrate third-party payment API',
            'description': 'Integrate Stripe payment API for processing transactions. Include error handling, webhook support, and security measures. Figma link: https://www.figma.com/file/ghi789/payment-flow',
            'priority': {'name': 'Critical'},
            'assignee': {'displayName': 'Backend Team'},
            'reporter': {'displayName': 'Tech Lead'},
            'labels': ['backend', 'api', 'security', 'payments'],
            'components': [{'name': 'Backend Services'}],
            'comments': []
        }
    elif template == "E-commerce Feature":
        ticket_data = {
            'key': 'ECOMM-001',
            'summary': 'Add product search and filtering',
            'description': 'Implement advanced product search with filters for category, price, rating, and availability. Should include autocomplete and search suggestions. Figma link: https://www.figma.com/file/jkl012/search-interface',
            'priority': {'name': 'High'},
            'assignee': {'displayName': 'Full Stack Team'},
            'reporter': {'displayName': 'E-commerce Manager'},
            'labels': ['ecommerce', 'search', 'frontend', 'backend'],
            'components': [{'name': 'Product Catalog'}],
            'comments': []
        }
    else:  # Custom Template
        st.info("Select a template above or use Manual Entry for custom tickets.")
        return
    
    # Display the template data
    st.subheader("Template Data")
    st.json(ticket_data)
    
    if st.button("Analyze Template", type="primary"):
        analyze_and_display(analyzer, ticket_data)

def analyze_and_display(analyzer, ticket_data):
    """Analyze ticket data and display results."""
    try:
        # Parse and analyze
        ticket = analyzer.parse_jira_ticket(ticket_data)
        result = analyzer.analyze_ticket_content(ticket)
        
        # Display results
        st.success("✅ Analysis completed!")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📋 Summary", 
            "❓ Questions", 
            "⚠️ Clarifications", 
            "🔧 Technical", 
            "🧪 Test Cases",
            "📊 Full Report"
        ])
        
        with tab1:
            display_summary(result)
        
        with tab2:
            display_questions(result)
        
        with tab3:
            display_clarifications(result)
        
        with tab4:
            display_technical(result)
        
        with tab5:
            display_test_cases(result)
        
        with tab6:
            display_full_report(analyzer, result)
            
    except Exception as e:
        st.error(f"Error during analysis: {e}")

def display_summary(result):
    """Display summary information."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ticket Info")
        st.write(f"**ID:** {result.ticket.ticket_id}")
        st.write(f"**Title:** {result.ticket.title}")
        st.write(f"**Priority:** {result.ticket.priority or 'Not specified'}")
        st.write(f"**Figma Links:** {len(result.ticket.figma_links)}")
    
    with col2:
        st.subheader("Quick Stats")
        st.metric("Questions Generated", len(result.suggested_questions))
        st.metric("Clarifications Needed", len(result.clarifications_needed))
        st.metric("Risk Areas", len(result.risk_areas))
        st.metric("Technical Considerations", len(result.technical_considerations))

def display_questions(result):
    """Display suggested questions."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Design Questions")
        for i, question in enumerate(result.design_questions, 1):
            st.write(f"{i}. {question}")
    
    with col2:
        st.subheader("💼 Business Questions")
        for i, question in enumerate(result.business_questions, 1):
            st.write(f"{i}. {question}")
    
    st.subheader("❓ General Questions")
    for i, question in enumerate(result.suggested_questions, 1):
        st.write(f"{i}. {question}")

def display_clarifications(result):
    """Display areas needing clarification."""
    st.subheader("⚠️ Areas Needing Clarification")
    
    if result.clarifications_needed:
        for i, clarification in enumerate(result.clarifications_needed, 1):
            st.warning(f"{i}. {clarification}")
    else:
        st.success("✅ No major clarifications needed!")

def display_technical(result):
    """Display technical considerations."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Technical Considerations")
        if result.technical_considerations:
            for consideration in result.technical_considerations:
                st.info(f"• {consideration}")
        else:
            st.success("✅ No specific technical considerations identified.")
    
    with col2:
        st.subheader("🚨 Risk Areas")
        if result.risk_areas:
            for risk in result.risk_areas:
                st.error(f"• {risk}")
        else:
            st.success("✅ No major risks identified.")

def display_test_cases(result):
    """Display suggested test cases."""
    st.subheader("🧪 Suggested Test Cases")
    
    if result.test_cases:
        # Group test cases by category
        current_category = ""
        for test_case in result.test_cases:
            if test_case.startswith("**") and test_case.endswith("**"):
                # This is a category header
                if current_category:
                    st.markdown("---")
                current_category = test_case.strip("**")
                st.markdown(f"**{current_category}**")
            elif test_case.strip() == "":
                # Empty line for spacing
                st.markdown("")
            else:
                # This is a test case
                st.markdown(f"• {test_case.strip('- ')}")
    else:
        st.success("✅ No specific test cases identified.")
    
    # Add download button for test cases
    if result.test_cases:
        test_cases_text = "\n".join(result.test_cases)
        st.download_button(
            label="📥 Download Test Cases as Text",
            data=test_cases_text,
            file_name=f"test_cases_{result.ticket.ticket_id}.txt",
            mime="text/plain"
        )

def display_full_report(analyzer, result):
    """Display the full analysis report."""
    st.subheader("📊 Full Analysis Report")
    
    report = analyzer.generate_report(result)
    st.markdown(report)
    
    # Download button
    st.download_button(
        label="📥 Download Report as Markdown",
        data=report,
        file_name=f"jira_analysis_{result.ticket.ticket_id}.md",
        mime="text/markdown"
    )

if __name__ == "__main__":
    main()
