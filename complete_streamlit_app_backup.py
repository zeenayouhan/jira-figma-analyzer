#!/usr/bin/env python3
"""
Enhanced Streamlit Web Interface with Storage Integration

Features:
- Original analysis functionality
- Automatic ticket storage
- Search and browse stored tickets
- Analytics and statistics
- Confluence document integration
- Screen Explorer with natural descriptions
- Export capabilities
"""

import streamlit as st
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
import os
import tempfile
from pathlib import Path
import hashlib
import uuid

# Initialize storage system
@st.cache_resource
def init_storage():
    return TicketStorageSystem()

def main():
    st.set_page_config(
        page_title="Jira Figma Analyzer Pro",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize storage
    storage = init_storage()
    
    st.title("🎯 Jira Figma Analyzer Pro")
    st.markdown("Advanced ticket analysis with intelligent storage and search capabilities")
    
    # Main navigation
    main_tab = st.radio(
        "Choose a section:", 
        ["🎯 Analyze Tickets", "🔍 Search & Browse", "📊 Analytics", "📝 Feedback Analytics", "📚 Confluence Docs", "🔍 Screen Explorer", "🏗️ Manage Screens"],
        horizontal=True
    )
    st.markdown("---")
    
    if main_tab == "🎯 Analyze Tickets":
        analyze_tickets_section(storage)
    elif main_tab == "🔍 Search & Browse":
        search_and_browse_section(storage)
    elif main_tab == "📊 Analytics":
        analytics_section(storage)
    elif main_tab == "📝 Feedback Analytics":
        feedback_analytics_section()
    elif main_tab == "📚 Confluence Docs":
        confluence_docs_section()
    elif main_tab == "🔍 Screen Explorer":
        screen_explorer_section()
    else:
        render_implemented_screens_ui()

def analyze_tickets_section(storage):
    """Enhanced ticket analysis section with storage."""
    # Initialize analyzer
    analyzer = JiraFigmaAnalyzer()
    
    # Sidebar for input method
    st.sidebar.header("Input Method")
    input_method = st.sidebar.radio(
        "Choose how to input ticket data:",
        ["Manual Entry", "JSON Import", "Quick Template"]
    )
    
    # Storage options
    st.sidebar.header("Storage Options")
    auto_store = st.sidebar.checkbox("Auto-store analysis results", value=True)
    store_format = st.sidebar.selectbox("Storage format", ["Full Details", "Summary Only"])
    
    if input_method == "Manual Entry":
        manual_entry_form(analyzer, storage, auto_store, store_format)
    elif input_method == "JSON Import":
        json_import_form(analyzer, storage, auto_store, store_format)
    else:
        quick_template_form(analyzer, storage, auto_store, store_format)

def manual_entry_form(analyzer, storage, auto_store, store_format):
    """Manual entry form for ticket data."""
    st.header("Manual Ticket Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticket_key = st.text_input("Ticket Key", placeholder="e.g., PROJ-123")
        title = st.text_input("Title", placeholder="Brief description of the ticket")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        ticket_type = st.selectbox("Type", ["Story", "Bug", "Task", "Epic"])
    
    with col2:
        status = st.selectbox("Status", ["To Do", "In Progress", "Review", "Done"])
        assignee = st.text_input("Assignee", placeholder="Developer name")
        labels = st.text_input("Labels", placeholder="backend, frontend, urgent")
        components = st.text_input("Components", placeholder="API, UI, Database")
    
    description = st.text_area(
        "Description", 
        placeholder="Detailed description of what needs to be implemented...",
        height=150
    )
    
    # Figma links
    figma_links_text = st.text_area(
        "Figma Links (one per line)",
        placeholder="https://www.figma.com/file/...\nhttps://www.figma.com/design/...",
        help="Enter Figma URLs, one per line"
    )
    
    # PDF design upload
    st.markdown("#### 📄 PDF Design Files")
    uploaded_pdfs = st.file_uploader(
        "Upload PDF design files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload wireframes, mockups, or design documentation as PDF files"
    )
    
    # Media files upload (NEW)
    st.markdown("#### 📸 Media Files (Images & Videos)")
    uploaded_media = st.file_uploader(
        "Upload screenshots, mockups, or demo videos",
        type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'avi', 'mov', 'mkv'],
        accept_multiple_files=True,
        help="Upload images or videos showing UI designs, workflows, or demonstrations"
    )
    
    if st.button("🎯 Analyze Ticket", type="primary"):
        if not title or not description:
            st.warning("Please fill in at least the title and description.")
            return
        
        # Process Figma links
        figma_links_list = []
        if figma_links_text.strip():
            figma_links_list = [url.strip() for url in figma_links_text.strip().split('\n') if url.strip()]
        
        # Handle PDF uploads
        pdf_paths = []
        if uploaded_pdfs:
            temp_dir = tempfile.mkdtemp()
            for pdf_file in uploaded_pdfs:
                pdf_path = os.path.join(temp_dir, pdf_file.name)
                with open(pdf_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                pdf_paths.append(pdf_path)
        
        # Handle media uploads (NEW)
        media_paths = []
        if uploaded_media:
            temp_dir = temp_dir if 'temp_dir' in locals() else tempfile.mkdtemp()
            for media_file in uploaded_media:
                media_path = os.path.join(temp_dir, media_file.name)
                with open(media_path, "wb") as f:
                    f.write(media_file.getbuffer())
                media_paths.append(media_path)
        
        # Create ticket data
        ticket_data = {
            'key': ticket_key or f"MANUAL-{int(time.time())}",
            'title': title,
            'description': description,
            'priority': priority,
            'type': ticket_type,
            'status': status,
            'assignee': assignee,
            'labels': [l.strip() for l in labels.split(',') if l.strip()] if labels else [],
            'components': [c.strip() for c in components.split(',') if c.strip()] if components else [],
            'figma_links_list': figma_links_list,
            'pdf_design_files': pdf_paths,
            'media_files': media_paths
        }
        
        # Analyze ticket
        analyze_ticket_content(analyzer, ticket_data, storage, auto_store, store_format)

def analyze_ticket_content(analyzer, ticket_data, storage, auto_store, store_format):
    """Analyze ticket content and display results."""
    try:
        # Validate ticket_data is a dictionary
        if not isinstance(ticket_data, dict):
            st.error(f"❌ Invalid ticket data type: {type(ticket_data)}. Expected dictionary.")
            return
            
        with st.spinner("🔍 Analyzing ticket..."):
            # Parse ticket with error handling
            try:
                ticket = analyzer.parse_jira_ticket(ticket_data)
            except Exception as e:
                st.error(f"❌ Error parsing ticket: {e}")
                return
            
            # Analyze with context (including media files)
            try:
                if ticket_data.get('media_files'):
                    # Use the enhanced analyzer method for media files
                    result = analyzer.analyze_ticket_with_media(ticket_data, ticket_data['media_files'])
                else:
                    result = analyzer.analyze_ticket_content(ticket)
            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
                import traceback
                st.error(f"Full error: {traceback.format_exc()}")
                return
            
            # Generate report
            try:
                report = analyzer.generate_report(result)
            except Exception as e:
                st.error(f"❌ Error generating report: {e}")
                return
        
        # Store results if enabled
        stored_ticket_id = None
        if auto_store:
            try:
                stored_ticket_id = storage.store_ticket({
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
                        "test_cases": result.test_cases,
                        "figma_designs": getattr(result, "figma_designs", []),
                        "pdf_designs": getattr(result, "pdf_designs", []),
                        "media_files": getattr(result, "media_files", [])
                    },
                    "report": report
                })
            except Exception as e:
                st.warning(f"⚠️ Failed to store analysis: {e}")
        
        # Display results with enhanced context
        display_analysis_results_with_confluence(result, report, stored_ticket_id, storage)
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
        import traceback
        st.error(f"Full traceback: {traceback.format_exc()}")
        if st.checkbox("Show debug info"):
            st.exception(e)

def display_full_analysis_modal(full_ticket):
    """Display full analysis details in a modal-style layout."""
    st.markdown("---")
    st.subheader(f"🔍 Full Analysis: {full_ticket.get('title', 'Unknown Title')}")
    
    # Create tabs for organized display
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Details", "❓ Questions", "🧪 Test Cases", 
        "⚠️ Risks", "📊 Raw Data"
    ])
    
    with tab1:
        st.markdown("### Ticket Details")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Ticket ID:** {full_ticket.get('ticket_id', 'N/A')}")
            st.markdown(f"**Created:** {full_ticket.get('created_at', 'N/A')}")
        with col2:
            st.markdown(f"**Updated:** {full_ticket.get('updated_at', 'N/A')}")
            st.markdown(f"**Key:** {full_ticket.get('ticket_key', 'N/A')}")
        
        st.markdown("**Description:**")
        st.markdown(full_ticket.get('description', 'No description available'))
    
    with tab2:
        st.markdown("### Questions")
        questions = full_ticket.get('questions', [])
        if questions:
            for i, question in enumerate(questions, 1):
                st.markdown(f"{i}. {question}")
        else:
            st.info("No questions found")
    
    with tab3:
        st.markdown("### Test Cases")
        test_cases = full_ticket.get('test_cases', [])
        if test_cases:
            for i, test_case in enumerate(test_cases, 1):
                st.markdown(f"{i}. {test_case}")
        else:
            st.info("No test cases found")
    
    with tab4:
        st.markdown("### Risk Areas")
        risks = full_ticket.get('risks', [])
        if risks:
            for i, risk in enumerate(risks, 1):
                st.markdown(f"{i}. {risk}")
        else:
            st.info("No risks identified")
    
    with tab5:
        st.markdown("### Raw Data")
        st.json(full_ticket)
    
    st.markdown("---")

def display_analysis_results_with_confluence(result, report, stored_ticket_id, storage, confluence_context=None):
    """Display analysis results with Confluence context information."""
    
    # Success message with context info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Questions Generated", len(result.suggested_questions + result.design_questions + result.business_questions))
    with col2:
        st.metric("Test Cases", len(result.test_cases))
    with col3:
        st.metric("Risk Areas", len(result.risk_areas))
    
    if stored_ticket_id:
        st.success(f"✅ Analysis completed and stored! Ticket ID: `{stored_ticket_id}`")
    
    # Enhanced tabbed results
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary", "❓ Questions", "🧪 Test Cases", 
        "⚠️ Risks", "📄 Full Report"
    ])
    
    with tab1:
        st.subheader("Analysis Summary")
        
        # Analysis metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("General Questions", len(result.suggested_questions))
        with col2:
            st.metric("Design Questions", len(result.design_questions))
        with col3:
            st.metric("Business Questions", len(result.business_questions))
        with col4:
            st.metric("Risk Areas", len(result.risk_areas))
        
        # Design analysis with enhanced screen details
        if hasattr(result.ticket, 'figma_links') and result.ticket.figma_links:
            st.markdown("### 🎨 Design Analysis")
            st.markdown(f"- **Figma Links Found**: {len(result.ticket.figma_links)}")
            
            # Show screen details with natural descriptions
            analysis_ctx = getattr(result.ticket, 'analysis_context', {}) if hasattr(result.ticket, 'analysis_context') else {}
            figma_designs = analysis_ctx.get('figma_designs') or analysis_ctx.get('figma_context') or []
            screen_details = []
            for d in figma_designs:
                if isinstance(d, dict) and d.get('screen_details'):
                    screen_details.extend(d['screen_details'])
            
            if screen_details:
                st.markdown("#### 📱 Design Screens")
                
                # Show aggregate metrics (with type checking)
                total_fields = 0
                total_ctas = 0
                total_nav = 0
                
                for sd in screen_details:
                    if isinstance(sd, dict):
                        total_fields += sd.get('field_count', 0)
                        total_ctas += sd.get('cta_count', 0)
                        total_nav += sd.get('nav_count', 0)
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Form Fields", total_fields)
                with col_b:
                    st.metric("Total CTAs", total_ctas)
                with col_c:
                    st.metric("Navigation Elements", total_nav)
                
                # Show natural descriptions
                with st.expander("🔍 View Screen Details", expanded=False):
                    for sd in screen_details[:12]:
                        # Type check - handle both dict and string cases
                        if isinstance(sd, dict):
                            screen_name = sd.get('screen', 'Unknown Screen')
                            st.markdown(f"**🖼️ {screen_name}**")
                            
                            # Show natural description prominently
                            if sd.get('description'):
                                st.markdown(f"📝 **{screen_name}**: {sd.get('description')}")
                            else:
                                st.markdown(f"📝 {sd.get('summary', 'No summary available')}")
                        elif isinstance(sd, str):
                            # Handle case where screen_details contains strings
                            st.markdown(f"**🖼️ {sd}**")
                            st.markdown(f"📝 Screen: {sd}")
                        else:
                            st.markdown(f"**🖼️ Unknown Screen**")
                            st.markdown(f"📝 Screen data: {sd}")
                        
                        st.markdown("---")
                    
                    if len(screen_details) > 12:
                        st.caption(f"... and {len(screen_details) - 12} more screens")
        
        # Show key insights
        if result.clarifications_needed:
            st.markdown("### 🔍 Key Clarifications Needed")
            for clarification in result.clarifications_needed[:3]:
                st.markdown(f"- {clarification}")

    with tab2:
        st.subheader("Clarifying Questions")
        
        # General Questions
        if result.suggested_questions:
            st.markdown("#### 🔹 General Questions")
            for i, question in enumerate(result.suggested_questions, 1):
                st.markdown(f"{i}. {question}")
        
        # Design Questions
        if result.design_questions:
            st.markdown("#### 🎨 Design Questions")
            for i, question in enumerate(result.design_questions, 1):
                st.markdown(f"{i}. {question}")
        
        # Business Questions
        if result.business_questions:
            st.markdown("#### 💼 Business Questions")
            for i, question in enumerate(result.business_questions, 1):
                st.markdown(f"{i}. {question}")

    with tab3:
        st.subheader("Test Cases")
        if result.test_cases:
            for i, test_case in enumerate(result.test_cases, 1):
                st.markdown(f"**Test Case {i}:** {test_case}")
        else:
            st.info("No specific test cases generated.")

    with tab4:
        st.subheader("Risk Areas")
        if result.risk_areas:
            for i, risk in enumerate(result.risk_areas, 1):
                st.markdown(f"**Risk {i}:** {risk}")
        else:
            st.info("No specific risks identified.")

    with tab5:
        st.subheader("Full Analysis Report")
        st.markdown(report)
        
        # Download button
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"analysis_report_{result.ticket.ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    # FEEDBACK COLLECTION SECTION (NEW)
    st.markdown("---")
    st.subheader("📝 Feedback")
    st.markdown("Help us improve by rating the quality of the generated analysis!")
    
    # Initialize feedback system
    try:
        feedback_system = FeedbackSystem()
        
        # Feedback form
        feedback_col1, feedback_col2 = st.columns(2)
        
        with feedback_col1:
            st.markdown("**Rate the overall analysis quality:**")
            overall_rating = st.radio(
                "Overall Rating",
                [1, 2, 3, 4, 5],
                format_func=lambda x: f"{x} {'⭐' * x}",
                horizontal=True,
                key=f"overall_{result.ticket.ticket_id}"
            )
            
            feedback_comment = st.text_area(
                "Additional comments (optional)",
                placeholder="What was good? What could be improved?",
                key=f"comment_{result.ticket.ticket_id}"
            )
        
        with feedback_col2:
            st.markdown("**Rate specific aspects:**")
            
            questions_rating = st.selectbox(
                "Questions Quality",
                [1, 2, 3, 4, 5],
                format_func=lambda x: f"{x} ⭐",
                key=f"questions_{result.ticket.ticket_id}"
            )
            
            test_cases_rating = st.selectbox(
                "Test Cases Quality", 
                [1, 2, 3, 4, 5],
                format_func=lambda x: f"{x} ⭐",
                key=f"testcases_{result.ticket.ticket_id}"
            )
            
            risks_rating = st.selectbox(
                "Risk Analysis Quality",
                [1, 2, 3, 4, 5], 
                format_func=lambda x: f"{x} ⭐",
                key=f"risks_{result.ticket.ticket_id}"
            )
        
        if st.button("📤 Submit Feedback", key=f"submit_feedback_{result.ticket.ticket_id}"):
            try:
                # Collect feedback for overall analysis
                feedback_id = feedback_system.collect_feedback(
                    ticket_id=result.ticket.ticket_id,
                    analysis_type="overall",
                    rating=overall_rating,
                    comment=feedback_comment,
                    ticket_title=result.ticket.title,
                    ticket_description=result.ticket.description
                )
                
                # Collect specific feedback for each aspect
                feedback_system.collect_feedback(
                    ticket_id=result.ticket.ticket_id,
                    analysis_type="questions",
                    rating=questions_rating,
                    ticket_title=result.ticket.title,
                    ticket_description=result.ticket.description
                )
                
                feedback_system.collect_feedback(
                    ticket_id=result.ticket.ticket_id,
                    analysis_type="test_cases",
                    rating=test_cases_rating,
                    ticket_title=result.ticket.title,
                    ticket_description=result.ticket.description
                )
                
                feedback_system.collect_feedback(
                    ticket_id=result.ticket.ticket_id,
                    analysis_type="risks",
                    rating=risks_rating,
                    ticket_title=result.ticket.title,
                    ticket_description=result.ticket.description
                )
                
                st.success("🎉 Thank you for your feedback! This helps us improve the analysis quality.")
                
            except Exception as e:
                st.error(f"❌ Error submitting feedback: {e}")
    
    except Exception as e:
        st.warning(f"⚠️ Feedback system not available: {e}")

def feedback_analytics_section():
    """Display feedback analytics and insights."""
    st.header("📝 Feedback Analytics")
    st.markdown("Insights from user feedback to improve analysis quality")
    
    try:
        feedback_system = FeedbackSystem()
        
        # Get feedback statistics
        stats = feedback_system.get_feedback_stats()
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Feedback", stats['total_feedback'])
        with col2:
            st.metric("Average Rating", f"{stats['average_rating']}/5")
        with col3:
            st.metric("Recent Feedback (7d)", stats['recent_feedback_count'])
        with col4:
            st.metric("Recent Avg Rating", f"{stats['recent_average_rating']}/5")
        
        if stats['total_feedback'] > 0:
            # Feedback breakdown
            st.subheader("📊 Feedback Breakdown by Type")
            feedback_df = pd.DataFrame(stats['feedback_by_type'])
            
            if not feedback_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Rating distribution chart
                    fig_ratings = px.bar(
                        feedback_df, 
                        x='type', 
                        y='avg_rating',
                        title="Average Rating by Analysis Type",
                        color='avg_rating',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_ratings.update_layout(showlegend=False)
                    st.plotly_chart(fig_ratings, use_container_width=True)
                
                with col2:
                    # Feedback count chart
                    fig_count = px.pie(
                        feedback_df,
                        values='count',
                        names='type',
                        title="Feedback Distribution by Type"
                    )
                    st.plotly_chart(fig_count, use_container_width=True)
            
            # Detailed feedback analysis
            st.subheader("🔍 Detailed Feedback Analysis")
            
            # Get feedback summary
            summary = feedback_system.get_feedback_summary()
            
            if summary.total_feedback > 0:
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📈 Rating Distribution", 
                    "👍 Positive Feedback", 
                    "👎 Areas for Improvement", 
                    "🔧 Improvement Opportunities"
                ])
                
                with tab1:
                    st.markdown("**Rating Distribution:**")
                    rating_data = []
                    for rating, count in summary.rating_distribution.items():
                        rating_data.append({"Rating": f"{rating} ⭐", "Count": count})
                    
                    if rating_data:
                        rating_df = pd.DataFrame(rating_data)
                        fig = px.bar(rating_df, x='Rating', y='Count', title="Rating Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    st.markdown("**Common Praises:**")
                    if summary.common_praises:
                        for i, praise in enumerate(summary.common_praises, 1):
                            st.markdown(f"{i}. {praise}")
                    else:
                        st.info("No specific praises found yet.")
                
                with tab3:
                    st.markdown("**Common Complaints:**")
                    if summary.common_complaints:
                        for i, complaint in enumerate(summary.common_complaints, 1):
                            st.markdown(f"{i}. {complaint}")
                    else:
                        st.info("No specific complaints found yet.")
                    
                    # Low-rated items
                    st.markdown("**Low-Rated Analysis Items:**")
                    low_rated = feedback_system.get_low_rated_items()
                    if low_rated:
                        for item in low_rated[:5]:  # Show top 5 low-rated items
                            with st.expander(f"⚠️ {item['analysis_type'].title()} (Rating: {item['rating']}/5)"):
                                st.markdown(f"**Ticket:** {item['ticket_id']}")
                                st.markdown(f"**Comment:** {item['comment']}")
                                if item['unhelpful_items']:
                                    st.markdown(f"**Unhelpful Items:** {', '.join(item['unhelpful_items'])}")
                    else:
                        st.info("No low-rated items found.")
                
                with tab4:
                    st.markdown("**Improvement Opportunities:**")
                    opportunities = feedback_system.get_improvement_opportunities()
                    
                    if opportunities['priority_areas']:
                        st.markdown("**🔴 Priority Areas:**")
                        for area in opportunities['priority_areas']:
                            st.error(f"**{area['area']}** (Rating: {area['current_rating']:.1f}/5)")
                            st.markdown(f"- Issue: {area['issue']}")
                            st.markdown(f"- Action: {area['action']}")
                    
                    if opportunities['quick_fixes']:
                        st.markdown("**🟡 Quick Fixes:**")
                        for fix in opportunities['quick_fixes']:
                            st.warning(f"**Issue:** {fix['issue']}")
                            st.markdown(f"- Action: {fix['action']}")
                    
                    if opportunities['topic_specific_issues']:
                        st.markdown("**📚 Topic-Specific Issues:**")
                        for topic, issue in opportunities['topic_specific_issues'].items():
                            st.info(f"**{topic.title()}** (Rating: {issue['rating']:.1f}/5)")
                            st.markdown(f"- {issue['action']}")
                    
                    if opportunities['long_term_improvements']:
                        st.markdown("**🔵 Long-term Improvements:**")
                        for suggestion in opportunities['long_term_improvements']:
                            st.markdown(f"- {suggestion}")
            
            # Export functionality
            st.subheader("📤 Export Feedback Data")
            if st.button("Download Feedback Data (JSON)"):
                export_file = feedback_system.export_feedback_data('json')
                st.success(f"✅ Feedback data exported to: {export_file}")
        
        else:
            st.info("No feedback data available yet. Start analyzing tickets and collecting feedback!")
    
    except Exception as e:
        st.error(f"❌ Error loading feedback analytics: {e}")

def search_and_browse_section(storage):
    """Search and browse stored tickets."""
    st.header("🔍 Search & Browse Tickets")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search tickets", placeholder="Enter keywords, ticket ID, or description...")
    with col2:
        search_type = st.selectbox("Type", ["All", "Questions", "Risks", "Content"])
    
    if search_query:
        with st.spinner("Searching..."):
            if search_type == "All":
                results = storage.search_tickets(search_query)
            elif search_type == "Questions":
                results = storage.search_questions(search_query)
            elif search_type == "Risks":
                results = storage.search_risks(search_query)
            else:
                results = storage.search_ticket_content(search_query)
        
        if results:
            st.success(f"Found {len(results)} results")
            for idx, result in enumerate(results[:10]):  # Show first 10 results
                with st.expander(f"🎫 {result.get('ticket_key', 'Unknown')} - {result.get('title', 'No title')[:50]}..."):
                    st.markdown(f"**Description:** {result.get('description', 'No description')[:200]}...")
                    st.markdown(f"**Stored:** {result.get('created_at', 'Unknown date')}")
                    # Use ticket_id or index to ensure unique keys
                    unique_key = result.get('ticket_id') or result.get('id') or f"search_{idx}"
                    if st.button(f"🔍 View Full Analysis", key=f"view_search_{unique_key}"):
                        # Load and display full analysis
                        ticket_id = result.get('ticket_id') or result.get('id')
                        if ticket_id:
                            full_ticket = storage.get_ticket(ticket_id)
                            if full_ticket:
                                display_full_analysis_modal(full_ticket)
                            else:
                                st.error("Could not load ticket details")
                        else:
                            st.error("Invalid ticket ID")
        else:
            st.info("No results found. Try different keywords.")
    
    # Recent tickets
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📅 Stored Tickets")
    with col2:
        show_all = st.checkbox("Show All Tickets", value=False)
    
    # Get tickets based on user preference
    if show_all:
        all_tickets = storage.get_all_tickets()
        tickets_to_show = all_tickets[:50]  # Limit to 50 for performance
        if len(all_tickets) > 50:
            st.info(f"Showing first 50 of {len(all_tickets)} tickets")
    else:
        tickets_to_show = storage.get_recent_tickets(limit=10)
    
    if not tickets_to_show:
        st.info("No tickets found. Analyze some tickets first!")
    else:
        for idx, ticket in enumerate(tickets_to_show):
            with st.expander(f"🎫 {ticket.get('ticket_key', 'Unknown')} - {ticket.get('title', 'No title')[:50]}..."):
                st.markdown(f"**Created:** {ticket.get('created_at', 'Unknown')}")
                st.markdown(f"**Questions:** {ticket.get('question_count', 0)}")
                st.markdown(f"**Test Cases:** {ticket.get('test_case_count', 0)}")
                st.markdown(f"**Risks:** {ticket.get('risk_count', 0)}")
                
                # Unique key for view button
                ticket_unique_id = ticket.get('ticket_id') or ticket.get('id') or f"ticket_{idx}"
                if st.button(f"🔍 View Full Analysis", key=f"view_full_{ticket_unique_id}"):
                    # Load and display full analysis
                    ticket_id = ticket.get('ticket_id') or ticket.get('id')
                    if ticket_id:
                        full_ticket = storage.get_ticket(ticket_id)
                        if full_ticket:
                            display_full_analysis_modal(full_ticket)
                        else:
                            st.error("Could not load ticket details")
                    else:
                        st.error("Invalid ticket ID")

def analytics_section(storage):
    """Analytics and statistics dashboard."""
    st.header("📊 Analytics Dashboard")
    
    # Get statistics
    stats = storage.get_statistics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tickets", stats['total_tickets'])
    with col2:
        st.metric("Total Questions", stats['total_questions'])
    with col3:
        st.metric("Total Test Cases", stats['total_test_cases'])
    with col4:
        st.metric("Total Risks", stats['total_risks'])
    
    # Charts
    if stats['total_tickets'] > 0:
        # Tickets over time
        st.subheader("📈 Tickets Over Time")
        timeline_data = storage.get_tickets_timeline()
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            fig = px.line(df, x='date', y='count', title='Tickets Analyzed Per Day')
            st.plotly_chart(fig, use_container_width=True)
        
        # Priority distribution
        st.subheader("⚡ Priority Distribution")
        priority_data = storage.get_priority_distribution()
        if priority_data:
            fig = px.pie(
                values=[item["count"] for item in priority_data],
                names=[item["priority"] for item in priority_data],
                title="Ticket Priority Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

def confluence_docs_section():
    """Confluence document management and knowledge base."""
    st.header("📚 Confluence Document Integration")
    
    # Initialize Confluence integration
    @st.cache_resource
    def init_confluence():
        return ConfluenceIntegration()
    
    confluence = init_confluence()
    
    # Tabbed interface
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📚 Library", "🧠 Knowledge Base", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Upload Confluence Documents")
        st.markdown("Upload Confluence exports or documentation files to build the knowledge base.")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['html', 'md', 'xml', 'txt', 'pdf'],
            accept_multiple_files=True,
            help="Upload HTML exports, Markdown files, XML, plain text, or PDF documents"
        )
        
        if uploaded_files:
            process_uploaded_files(confluence, uploaded_files)
    
    with tab2:
        display_document_library(confluence)
    
    with tab3:
        display_knowledge_base_overview(confluence)
    
    with tab4:
        display_confluence_settings(confluence)

def process_uploaded_files(confluence, uploaded_files):
    """Process uploaded Confluence files."""
    if st.button("🚀 Process Files", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save file temporarily
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process file
            try:
                result = confluence.process_confluence_file(temp_path, uploaded_file.name)
                results.append({
                    'filename': uploaded_file.name,
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                results.append({
                    'filename': uploaded_file.name,
                    'status': 'error',
                    'error': str(e)
                })
            
            # Clean up
            os.remove(temp_path)
            os.rmdir(temp_dir)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Display results
        status_text.text("Processing complete!")
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = len(results) - success_count
        
        if success_count > 0:
            st.success(f"✅ Successfully processed {success_count} files")
        
        if error_count > 0:
            st.error(f"❌ Failed to process {error_count} files")
            
        for result in results:
            if result['status'] == 'error':
                st.error(f"Error processing {result['filename']}: {result['error']}")

def display_document_library(confluence):
    """Display the document library."""
    st.subheader("📚 Document Library")
    
    try:
        documents = confluence.get_all_documents()
        if documents:
            st.markdown(f"**Total documents:** {len(documents)}")
            
            for doc in documents:
                with st.expander(f"📄 {doc.get('title', 'Untitled')}"):
                    st.markdown(f"**Type:** {doc.get('type', 'Unknown')}")
                    st.markdown(f"**Size:** {len(doc.get('content', ''))} characters")
                    st.markdown(f"**Processed:** {doc.get('processed_at', 'Unknown')}")
                    
                    # Note: delete functionality would need to be implemented in ConfluenceIntegration
                    st.caption("💡 Delete functionality can be added to ConfluenceIntegration if needed")
        else:
            st.info("No documents uploaded yet. Use the Upload tab to add documents.")
    except Exception as e:
        st.error(f"Error loading documents: {e}")
        st.info("No documents uploaded yet. Use the Upload tab to add documents.")

def display_knowledge_base_overview(confluence):
    """Display knowledge base overview."""
    st.subheader("🧠 Knowledge Base Overview")
    
    try:
        stats = confluence.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Documents", stats.get("total_documents", 0))
        with col2:
            st.metric("Technologies", stats.get("unique_technologies", 0))
        with col3:
            st.metric("Components", stats['total_components'])
        with col4:
            st.metric("Features", stats.get("total_components", 0))
        
        # Knowledge categories - simplified version using available methods
        st.markdown("### 📊 Knowledge Categories")
        
        try:
            # Load the knowledge base to display some sample content
            confluence.load_knowledge_base()
            
            # Get sample documents to show categories
            documents = confluence.get_all_documents()
            
            if documents:
                st.markdown("#### 📄 Sample Document Titles")
                for doc in documents[:5]:
                    st.markdown(f"- {doc.get('title', 'Untitled')}")
                
                # Show basic document types
                doc_types = set(doc.get('type', 'Unknown') for doc in documents)
                st.markdown("#### 📂 Document Types")
                for doc_type in doc_types:
                    count = sum(1 for d in documents if d.get('type') == doc_type)
                    st.markdown(f"- {doc_type}: {count} documents")
            else:
                st.info("No documents processed yet. Upload some Confluence documents to see knowledge categories.")
                
        except Exception as e:
            st.error(f"Error loading knowledge categories: {e}")
            st.info("Upload some Confluence documents to build the knowledge base.")
            
    except Exception as e:
        st.error(f"Error loading knowledge base: {e}")

def display_confluence_settings(confluence):
    """Display Confluence integration settings."""
    st.subheader("⚙️ Settings")
    
    st.markdown("#### 🔧 Processing Options")
    
    # Available actions with current ConfluenceIntegration
    st.markdown("#### Available Actions")
    
    # Show knowledge base statistics
    if st.button("📊 Refresh Statistics"):
        st.rerun()
    
    # Note about additional features
    st.info("💡 Additional features like clearing knowledge base and export can be added to ConfluenceIntegration class as needed.")
    
    # Show current storage location
    try:
        confluence.load_knowledge_base()
        st.markdown("#### 📁 Storage Info")
        st.markdown(f"**Storage Directory:** `confluence_knowledge/`")
        st.markdown(f"**Database:** SQLite with processed documents")
    except Exception as e:
        st.warning(f"Storage info unavailable: {e}")

def screen_explorer_section():
    """Screen Explorer - analyze any Figma design to see detailed screen information."""
    st.header("🔍 Screen Explorer")
    st.markdown("Enter any Figma URL to explore screens and their components with natural descriptions.")
    
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
            # Initialize Figma integration
            from figma_integration import FigmaIntegration
            figma = FigmaIntegration()
            
            if not figma.figma_token:
                st.error("❌ Figma access token not configured. Please set FIGMA_ACCESS_TOKEN environment variable.")
                return
            
            with st.spinner("Analyzing Figma design..."):
                # Analyze the design
                design = figma.analyze_figma_design(figma_url)
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
                total_fields = sum(screen.get('field_count', 0) for screen in design.screen_details if isinstance(screen, dict))
                st.metric("Total Form Fields", total_fields)
            with col4:
                total_ctas = sum(screen.get('cta_count', 0) for screen in design.screen_details if isinstance(screen, dict))
                st.metric("Total CTAs", total_ctas)
            
            # Display design overview
            with st.expander("📋 Design Overview", expanded=True):
                st.write(f"**Design Name:** {design.name}")
                st.write(f"**Complexity Score:** {design.complexity_score:.1f}/10")
                st.write(f"**Pages:** {len(design.pages)}")
            
            # Screen-by-screen analysis with natural descriptions
            if design.screen_details:
                st.header("📱 Screen Analysis")
                
                for i, screen in enumerate(design.screen_details):
                    # Type check for screen data
                    if isinstance(screen, dict):
                        screen_name = screen.get('screen', f'Screen {i+1}')
                        
                        with st.expander(f"🖼️ {screen_name}", expanded=i < 3):
                            # Show natural description prominently
                            if screen.get('description'):
                                st.markdown(f"**📝 {screen_name}**: {screen.get('description')}")
                                st.markdown("---")
                            
                            # Show technical summary
                            st.markdown(f"**Summary:** {screen.get('summary', 'No summary available')}")
                            
                            # Show field and CTA counts
                            if screen.get('field_count', 0) > 0 or screen.get('cta_count', 0) > 0:
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("Form Fields", screen.get('field_count', 0))
                                with col_b:
                                    st.metric("CTAs", screen.get('cta_count', 0))
                    elif isinstance(screen, str):
                        # Handle string screen names
                        with st.expander(f"🖼️ {screen}", expanded=i < 3):
                            st.markdown(f"**📝 {screen}**: Screen identified from Figma design")
                    else:
                        # Handle unexpected data types
                        with st.expander(f"🖼️ Screen {i+1}", expanded=i < 3):
                            st.markdown(f"**📝 Screen {i+1}**: {str(screen)}")
            else:
                st.info("No detailed screen information available")
                
        except Exception as e:
            st.error(f"❌ Error analyzing Figma design: {e}")

def json_import_form(analyzer, storage, auto_store, store_format):
    """JSON import form for ticket data."""
    st.header("JSON Import")
    
    # Sample JSON
    sample_json = {
        "key": "PROJ-123",
        "title": "Implement user authentication",
        "description": "Add login/logout functionality with OAuth integration",
        "priority": "High",
        "type": "Story",
        "status": "In Progress",
        "assignee": "developer@company.com",
        "labels": ["backend", "security"],
        "components": ["Authentication", "API"],
        "figma_links": ["https://www.figma.com/file/example"]
    }
    
    with st.expander("📋 Sample JSON Format"):
        st.json(sample_json)
    
    # JSON input
    json_input = st.text_area(
        "Paste your JSON data:",
        placeholder=json.dumps(sample_json, indent=2),
        height=300
    )
    
    if st.button("🎯 Analyze from JSON", type="primary"):
        try:
            ticket_data = json.loads(json_input)
            analyze_ticket_content(analyzer, ticket_data, storage, auto_store, store_format)
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {e}")

def quick_template_form(analyzer, storage, auto_store, store_format):
    """Quick template form for common ticket types."""
    st.header("Quick Templates")
    
    template_type = st.selectbox(
        "Choose a template:",
        ["Bug Fix", "New Feature", "API Integration", "UI Enhancement", "Database Migration"]
    )
    
    templates = {
        "Bug Fix": {
            "type": "Bug",
            "priority": "High",
            "description": "Fix for reported issue:\n\n**Steps to reproduce:**\n1. \n2. \n3. \n\n**Expected behavior:**\n\n**Actual behavior:**\n\n**Environment:**"
        },
        "New Feature": {
            "type": "Story", 
            "priority": "Medium",
            "description": "Implementation of new feature:\n\n**User Story:**\nAs a [user type], I want [goal] so that [benefit]\n\n**Acceptance Criteria:**\n- [ ] \n- [ ] \n- [ ] \n\n**Technical Requirements:**"
        },
        "API Integration": {
            "type": "Task",
            "priority": "Medium", 
            "description": "Integration with external API:\n\n**API Details:**\n- Endpoint: \n- Authentication: \n- Rate limits: \n\n**Implementation Notes:**\n\n**Error Handling:**"
        },
        "UI Enhancement": {
            "type": "Story",
            "priority": "Low",
            "description": "UI/UX improvement:\n\n**Current State:**\n\n**Proposed Changes:**\n\n**Design References:**\n\n**Accessibility Considerations:**"
        },
        "Database Migration": {
            "type": "Task",
            "priority": "High",
            "description": "Database schema changes:\n\n**Changes Required:**\n\n**Migration Steps:**\n1. \n2. \n3. \n\n**Rollback Plan:**\n\n**Testing Strategy:**"
        }
    }
    
    template = templates[template_type]
    
    col1, col2 = st.columns(2)
    with col1:
        ticket_key = st.text_input("Ticket Key", placeholder="PROJ-123")
        title = st.text_input("Title", placeholder=f"{template_type} - Brief description")
    
    with col2:
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], 
                               index=["Low", "Medium", "High", "Critical"].index(template["priority"]))
        assignee = st.text_input("Assignee", placeholder="developer@company.com")
    
    description = st.text_area(
        "Description",
        value=template["description"],
        height=300
    )
    
    if st.button("🎯 Analyze Template", type="primary"):
        if not title:
            st.warning("Please provide a title.")
            return
        
        ticket_data = {
            'key': ticket_key or f"TEMPLATE-{int(time.time())}",
            'title': title,
            'description': description,
            'priority': priority,
            'type': template["type"],
            'status': "To Do",
            'assignee': assignee,
            'labels': [],
            'components': [],
            'figma_links_list': [],
            'pdf_design_files': []
        }
        
        analyze_ticket_content(analyzer, ticket_data, storage, auto_store, store_format)

if __name__ == "__main__":
    main()
