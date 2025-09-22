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
from persistent_feedback import PersistentFeedbackForm
import os
import tempfile
from pathlib import Path
import hashlib
import uuid

# Initialize storage system
@st.cache_resource
def init_storage():
    return TicketStorageSystem()

def display_gpt4_vision_results(result):
    """Display GPT-4 Vision analysis results."""
    if not hasattr(result, 'visual_analysis_results') or not result.visual_analysis_results:
        return
    
    st.header("🤖 GPT-4 Vision Analysis Results")
    
    visual_analyses = result.visual_analysis_results
    
    # Overview metrics
    st.subheader("📊 Visual Analysis Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Images Analyzed", len(visual_analyses))
    with col2:
        avg_quality = sum(va.design_quality_score for va in visual_analyses) / len(visual_analyses)
        st.metric("Avg Design Quality", f"{avg_quality:.1f}/10")
    with col3:
        total_components = sum(len(va.ui_components_identified) for va in visual_analyses)
        st.metric("UI Components Found", total_components)
    with col4:
        japanese_elements = sum(len(va.japanese_elements_detected) for va in visual_analyses)
        st.metric("Japanese Elements", japanese_elements)
    
    # Detailed analysis for each image
    for i, visual_analysis in enumerate(visual_analyses):
        with st.expander(f"🖼️ Image {i+1} Analysis - Quality: {visual_analysis.design_quality_score:.1f}/10", expanded=i == 0):
            
            # Design Quality Assessment
            st.subheader("🎯 Design Quality Assessment")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Design Quality Score", f"{visual_analysis.design_quality_score:.1f}/10")
                st.metric("Implementation Complexity", visual_analysis.implementation_complexity.title())
                st.metric("Confidence Score", f"{visual_analysis.confidence_score:.1%}")
            
            with col2:
                if visual_analysis.processing_time:
                    st.metric("Processing Time", f"{visual_analysis.processing_time:.2f}s")
                st.write("**Analysis Source:**", visual_analysis.image_source.replace('_', ' ').title())
                st.write("**Analysis ID:**", visual_analysis.analysis_id)
            
            # UI Components
            if visual_analysis.ui_components_identified:
                st.subheader("🧩 UI Components Identified")
                components_text = ", ".join(visual_analysis.ui_components_identified[:10])
                if len(visual_analysis.ui_components_identified) > 10:
                    components_text += f" ... and {len(visual_analysis.ui_components_identified) - 10} more"
                st.write(components_text)
            
            # Japanese Content Analysis
            if visual_analysis.japanese_elements_detected:
                st.subheader("🇯🇵 Japanese Content Analysis")
                st.write(f"**Japanese Elements Found:** {len(visual_analysis.japanese_elements_detected)}")
                
                japanese_preview = visual_analysis.japanese_elements_detected[:5]
                st.write("**Japanese Text Examples:**")
                for jp_text in japanese_preview:
                    st.write(f"• {jp_text}")
                
                if len(visual_analysis.japanese_elements_detected) > 5:
                    st.caption(f"... and {len(visual_analysis.japanese_elements_detected) - 5} more Japanese elements")
                
                # Localization recommendations
                if visual_analysis.localization_recommendations:
                    st.write("**Localization Recommendations:**")
                    for rec in visual_analysis.localization_recommendations[:3]:
                        st.write(f"• {rec}")
            
            # Improvement Suggestions
            if visual_analysis.improvement_suggestions:
                st.subheader("💡 Improvement Suggestions")
                for suggestion in visual_analysis.improvement_suggestions[:5]:
                    st.write(f"• {suggestion}")
                if len(visual_analysis.improvement_suggestions) > 5:
                    st.caption(f"... and {len(visual_analysis.improvement_suggestions) - 5} more suggestions")
            
            # User Experience Insights
            if visual_analysis.user_flow_insights:
                st.subheader("👤 User Experience Insights")
                for insight in visual_analysis.user_flow_insights[:3]:
                    st.write(f"• {insight}")
            
            # Development Recommendations
            if visual_analysis.development_recommendations:
                st.subheader("⚡ Development Recommendations")
                for rec in visual_analysis.development_recommendations[:3]:
                    st.write(f"• {rec}")
            
            # Potential Issues
            if visual_analysis.potential_issues:
                st.subheader("⚠️ Potential Issues")
                for issue in visual_analysis.potential_issues[:3]:
                    st.write(f"• {issue}")
            
            # Accessibility Assessment
            if visual_analysis.accessibility_assessment:
                st.subheader("♿ Accessibility Assessment")
                acc_assessment = visual_analysis.accessibility_assessment
                
                if acc_assessment.get('issues'):
                    st.write("**Issues Found:**")
                    for issue in acc_assessment['issues'][:3]:
                        st.write(f"• {issue}")
                
                if acc_assessment.get('score'):
                    st.metric("Accessibility Score", f"{acc_assessment['score']:.1f}/10")
            
            # Technical Analysis
            with st.expander("🔧 Technical Analysis Details", expanded=False):
                st.write("**Layout Assessment:**", visual_analysis.layout_assessment)
                st.write("**Color Scheme Analysis:**", visual_analysis.color_scheme_analysis)
                st.write("**Typography Analysis:**", visual_analysis.typography_analysis)
                st.write("**Navigation Assessment:**", visual_analysis.navigation_assessment)


def database_export_section():
    """Database Export Section for Production Access"""
    st.header("🗄️ Database Export (Production)")
    st.warning("⚠️ This section is for production database access only")
    
    # Database paths
    db_paths = {
        'tickets': 'storage/tickets.db',
        'feedback': 'feedback_storage/feedback.db',
        'confluence': 'confluence_knowledge/database/confluence_docs.db'
    }
    
    # Select database
    selected_db = st.selectbox("Select Database", list(db_paths.keys()))
    db_path = db_paths[selected_db]
    
    if st.button("Check Database Status"):
        try:
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                st.success(f"✅ Database found: {size:,} bytes")
                
                # Show tables
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                st.write("**Tables:**")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    st.write(f"- {table_name}: {count} rows")
                
                conn.close()
            else:
                st.error(f"❌ Database not found: {db_path}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Export options
    st.subheader("Export Data")
    
    if st.button("Export to JSON"):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            export_data = {}
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Convert to list of dictionaries
                table_data = []
                for row in rows:
                    table_data.append(dict(zip(columns, row)))
                
                export_data[table_name] = table_data
            
            conn.close()
            
            # Create download
            json_str = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{selected_db}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
    
    # Query interface
    st.subheader("Custom Query")
    query = st.text_area("Enter SQL Query", height=100)
    
    if st.button("Execute Query"):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results:
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Create DataFrame
                df = pd.DataFrame(results, columns=columns)
                st.dataframe(df)
                
                # Show count
                st.info(f"Found {len(results)} rows")
            else:
                st.info("No results found")
            
            conn.close()
            
        except Exception as e:
            st.error(f"❌ Query failed: {str(e)}")


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
    
    # GPT-4 Vision info banner
    st.info("🚀 **NEW: GPT-4 Vision Integration!** Upload design screenshots in the **📝 Manual Entry** tab for AI-powered visual analysis. Or try the demo in **🔍 Screen Explorer**!")
    
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
    
    # GPT-4 Vision visual analysis upload
    st.markdown("#### 🤖 GPT-4 Vision Analysis")
    st.info("🚀 **NEW!** Upload design screenshots or mockups for advanced AI-powered visual analysis!")
    
    with st.expander("ℹ️ What does GPT-4 Vision analyze?", expanded=False):
        st.markdown("""
        🎯 **Design Quality Assessment** - Overall design score (0-10)  
        🧩 **UI Component Detection** - Buttons, forms, navigation elements  
        🇯🇵 **Japanese Content Analysis** - Text detection & localization recommendations  
        ♿ **Accessibility Evaluation** - WCAG compliance and improvements  
        💡 **Implementation Suggestions** - Technical complexity and recommendations  
        👤 **UX Insights** - User flow and interaction recommendations  
        
        📷 **Supported formats**: JPG, PNG, WebP (Figma screenshots, UI mockups, design images)
        """)
    
    visual_analysis_images = st.file_uploader(
        "Upload images for GPT-4 Vision analysis",
        type=['jpg', 'jpeg', 'png', 'webp'],
        accept_multiple_files=True,
        help="Upload Figma screenshots, UI mockups, or design images for detailed AI visual analysis including design quality assessment, accessibility evaluation, and implementation recommendations",
        key="gpt4_vision_upload"
    )
    
    if visual_analysis_images:
        st.success(f"🤖 {len(visual_analysis_images)} images ready for GPT-4 Vision analysis!")
        st.markdown("*The **🤖 GPT-4 Vision** tab will appear in results after analysis.*")
    
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
        
        # Handle GPT-4 Vision analysis images
        visual_analysis_paths = []
        if visual_analysis_images:
            temp_dir = temp_dir if 'temp_dir' in locals() else tempfile.mkdtemp()
            for img_file in visual_analysis_images:
                img_path = os.path.join(temp_dir, f"vision_{img_file.name}")
                with open(img_path, "wb") as f:
                    f.write(img_file.getbuffer())
                visual_analysis_paths.append(img_path)
            st.success(f"📷 {len(visual_analysis_paths)} images uploaded for GPT-4 Vision analysis!")
        
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
            'media_files': media_paths,
            'visual_analysis_images': visual_analysis_paths
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
            
            # Analyze with context (including media files and visual analysis)
            try:
                # First, do the standard analysis
                if ticket_data.get('media_files'):
                    result = analyzer.analyze_ticket_with_media(ticket_data, ticket_data['media_files'])
                else:
                    result = analyzer.analyze_ticket_content(ticket)
                
                # Add GPT-4 Vision analysis if images were uploaded
                if ticket_data.get('visual_analysis_images') and hasattr(analyzer, 'analyze_ticket_with_visual_content'):
                    st.info("🤖 Running GPT-4 Vision analysis...")
                    enhanced_analysis = analyzer.analyze_ticket_with_visual_content(
                        ticket, 
                        result.to_dict() if hasattr(result, 'to_dict') else vars(result),
                        ticket_data['visual_analysis_images']
                    )
                    # Update the result with visual analysis
                    if enhanced_analysis.get('has_visual_analysis'):
                        result.visual_analysis_results = enhanced_analysis.get('visual_analyses', [])
                        result.visual_design_quality = enhanced_analysis.get('average_design_quality', 0)
                        result.japanese_visual_elements = enhanced_analysis.get('japanese_visual_elements', [])
                        st.success(f"✅ GPT-4 Vision analysis completed! Average design quality: {enhanced_analysis.get('average_design_quality', 0):.1f}/10")
                        
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
    
    # Check if GPT-4 Vision results are available
    has_vision_results = hasattr(result, 'visual_analysis_results') and result.visual_analysis_results
    
    # Enhanced tabbed results
    if has_vision_results:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📋 Summary", "❓ Questions", "🧪 Test Cases", 
            "⚠️ Risks", "🤖 GPT-4 Vision", "📄 Full Report"
        ])
    else:
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

    # GPT-4 Vision tab (only if vision results are available)
    if has_vision_results:
        with tab5:
            display_gpt4_vision_results(result)
        
        with tab6:
            st.subheader("Full Analysis Report")
            st.markdown(report)
            
            # Download button
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"analysis_report_{result.ticket.ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    else:
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
    
    # FEEDBACK COLLECTION SECTION (PERSISTENT)
    st.markdown("---")
    
    # Initialize feedback system
    try:
        feedback_system = FeedbackSystem()
        
        # Use the new persistent feedback form
        persistent_feedback = PersistentFeedbackForm(result.ticket.ticket_id, feedback_system)
        persistent_feedback.render()

    
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
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📈 Rating Distribution", 
                    "👍 Positive Feedback", 
                    "👎 Areas for Improvement", 
                    "🔧 Improvement Opportunities",
                    "🧠 AI Learning"
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
                
                with tab5:
                    st.markdown("**🧠 AI Learning from Feedback**")
                    st.info("This system continuously learns from your feedback to improve question quality!")
                    
                    # Initialize learning system
                    try:
                        from feedback_learning_system import FeedbackLearningSystem
                        learning_system = FeedbackLearningSystem(feedback_system)
                        
                        # Get learning insights
                        insights = learning_system.analyze_feedback_patterns()
                        improvements = learning_system.get_question_generation_improvements()
                        
                        if insights:
                            st.markdown("**🔍 Current Learning Insights:**")
                            for insight in insights:
                                confidence_color = "🟢" if insight.confidence >= 0.8 else "🟡" if insight.confidence >= 0.6 else "🔴"
                                st.markdown(f"{confidence_color} **{insight.description}**")
                                st.markdown(f"   ▶️ Action: {insight.action}")
                                st.markdown(f"   📊 Confidence: {insight.confidence:.1%}")
                                st.markdown("---")
                        
                        if improvements['prompt_enhancements']:
                            st.markdown("**🎯 Active Prompt Improvements:**")
                            for enhancement in improvements['prompt_enhancements']:
                                st.success(f"✅ {enhancement['description']}")
                                st.markdown(f"   🔧 Applied: {enhancement['action']}")
                        
                        if improvements['topic_specific_improvements']:
                            st.markdown("**📚 Topic-Specific Learning:**")
                            for topic, improvement in improvements['topic_specific_improvements'].items():
                                st.warning(f"**{topic.title()}:** {improvement['issue']}")
                                st.markdown(f"   🛠️ Improvement: {improvement['action']}")
                        
                        if not insights and not improvements['prompt_enhancements']:
                            st.info("🤖 **Learning Status:** Collecting feedback data to improve AI question generation. Keep providing ratings and comments!")
                            
                        # Learning statistics
                        st.markdown("**📈 Learning Statistics:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Learning Insights", len(insights))
                        with col2:
                            st.metric("Active Improvements", len(improvements['prompt_enhancements']))
                        with col3:
                            st.metric("Topics Being Improved", len(improvements['topic_specific_improvements']))
                        
                    except Exception as e:
                        st.error(f"❌ Learning system not available: {e}")
                        st.info("💡 The AI learning system requires additional feedback data to generate insights.")
            
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
                    
                    # Action buttons for search results
                    col1, col2 = st.columns([1, 1])
                    unique_key = result.get('ticket_id') or result.get('id') or f"search_{idx}"
                    
                    with col1:
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
                    
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_search_{unique_key}", type="secondary"):
                            # Delete the ticket
                            ticket_id = result.get('ticket_id') or result.get('id')
                            if ticket_id:
                                if storage.delete_ticket(ticket_id):
                                    st.success(f"✅ Ticket {ticket_id} deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete ticket")
                            else:
                                st.error("Invalid ticket ID")
        else:
            st.info("No results found. Try different keywords.")
    
    # Recent tickets
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("📅 Stored Tickets")
    with col2:
        show_all = st.checkbox("Show All Tickets", value=False)
    with col3:
        if st.button("🗑️ Delete All", type="secondary", help="Delete all stored tickets"):
            if st.session_state.get('confirm_delete_all', False):
                if storage.delete_all_tickets():
                    st.success("✅ All tickets deleted successfully!")
                    st.session_state['confirm_delete_all'] = False
                    st.rerun()
                else:
                    st.error("❌ Failed to delete all tickets")
            else:
                st.session_state['confirm_delete_all'] = True
                st.warning("⚠️ Click again to confirm deletion of ALL tickets")
    
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
                
                # Action buttons
                col1, col2 = st.columns([1, 1])
                ticket_unique_id = ticket.get('ticket_id') or ticket.get('id') or f"ticket_{idx}"
                
                with col1:
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
                
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{ticket_unique_id}", type="secondary"):
                        # Delete the ticket
                        ticket_id = ticket.get('ticket_id') or ticket.get('id')
                        if ticket_id:
                            if storage.delete_ticket(ticket_id):
                                st.success(f"✅ Ticket {ticket_id} deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete ticket")
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
    
    # GPT-4 Vision Demo Section
    st.markdown("---")
    st.subheader("🤖 GPT-4 Vision Demo")
    st.info("💡 **Want to test GPT-4 Vision?** Upload a design screenshot below to see AI-powered visual analysis!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        demo_image = st.file_uploader(
            "Upload a design screenshot for GPT-4 Vision analysis",
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Upload any UI design, Figma screenshot, or mockup to see what GPT-4 Vision can analyze",
            key="demo_vision_upload"
        )
    
    with col2:
        if st.button("🤖 Analyze with GPT-4 Vision", disabled=not demo_image):
            if demo_image:
                st.info("🚀 Running GPT-4 Vision analysis...")
                
                # Save uploaded image temporarily
                import tempfile
                import os
                temp_dir = tempfile.mkdtemp()
                img_path = os.path.join(temp_dir, f"demo_{demo_image.name}")
                
                with open(img_path, "wb") as f:
                    f.write(demo_image.getbuffer())
                
                try:
                    # Initialize analyzer
                    from jira_figma_analyzer import JiraFigmaAnalyzer
                    analyzer = JiraFigmaAnalyzer()
                    
                    if analyzer.vision_analyzer:
                        # Run visual analysis
                        visual_result = analyzer.analyze_visual_content(img_path)
                        
                        if visual_result:
                            st.success("✅ GPT-4 Vision analysis completed!")
                            
                            # Display key results
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Design Quality", f"{visual_result.design_quality_score:.1f}/10")
                            with col2:
                                st.metric("UI Components", len(visual_result.ui_components_identified))
                            with col3:
                                st.metric("Japanese Elements", len(visual_result.japanese_elements_detected))
                            
                            # Show sample results
                            if visual_result.ui_components_identified:
                                st.write("**UI Components Found:**", ", ".join(visual_result.ui_components_identified[:5]))
                            
                            if visual_result.improvement_suggestions:
                                st.write("**Key Suggestions:**")
                                for suggestion in visual_result.improvement_suggestions[:3]:
                                    st.write(f"• {suggestion}")
                            
                            st.info("💡 For full detailed analysis, use the **📝 Manual Entry** tab and upload images in the **🤖 GPT-4 Vision Analysis** section!")
                        else:
                            st.error("❌ Visual analysis failed")
                    else:
                        st.error("❌ GPT-4 Vision not available")
                        
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    # Cleanup
                    try:
                        os.remove(img_path)
                        os.rmdir(temp_dir)
                    except:
                        pass
    
    st.markdown("---")
    
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
            
            # Japanese text analysis display
            if hasattr(design, 'japanese_text_analysis') and design.japanese_text_analysis:
                japanese_analysis = design.japanese_text_analysis
                
                if japanese_analysis.get('has_japanese'):
                    with st.expander("🇯🇵 Japanese Content Analysis", expanded=True):
                        st.success("✅ Japanese text detected in this design!")
                        
                        # Overview metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Japanese Text Nodes", len(japanese_analysis.get('japanese_text_nodes', [])))
                        with col2:
                            st.metric("Japanese Screens", len(japanese_analysis.get('japanese_screens', [])))
                        with col3:
                            st.metric("Japanese Ratio", f"{japanese_analysis.get('japanese_ratio', 0):.1%}")
                        with col4:
                            st.metric("Total Text Nodes", japanese_analysis.get('total_text_nodes', 0))
                        
                        # Character breakdown
                        char_analysis = japanese_analysis.get('character_analysis', {})
                        if char_analysis:
                            st.subheader("📊 Character Type Breakdown")
                            char_col1, char_col2, char_col3 = st.columns(3)
                            with char_col1:
                                st.metric("Hiragana", f"{char_analysis.get('total_hiragana', 0):.0f} chars")
                            with char_col2:
                                st.metric("Katakana", f"{char_analysis.get('total_katakana', 0):.0f} chars")
                            with char_col3:
                                st.metric("Kanji", f"{char_analysis.get('total_kanji', 0):.0f} chars")
                        
                        # UI Element breakdown
                        ui_analysis = japanese_analysis.get('ui_element_analysis', {})
                        if ui_analysis:
                            st.subheader("🔘 Japanese UI Elements")
                            
                            if ui_analysis.get('japanese_buttons'):
                                st.write("**Buttons:**")
                                for btn in ui_analysis['japanese_buttons'][:5]:  # Show first 5
                                    st.write(f"• {btn}")
                                if len(ui_analysis['japanese_buttons']) > 5:
                                    st.caption(f"... and {len(ui_analysis['japanese_buttons']) - 5} more buttons")
                            
                            if ui_analysis.get('japanese_navigation'):
                                st.write("**Navigation:**")
                                for nav in ui_analysis['japanese_navigation'][:5]:
                                    st.write(f"• {nav}")
                                if len(ui_analysis['japanese_navigation']) > 5:
                                    st.caption(f"... and {len(ui_analysis['japanese_navigation']) - 5} more navigation items")
                            
                            if ui_analysis.get('japanese_labels'):
                                st.write("**Labels:**")
                                for label in ui_analysis['japanese_labels'][:5]:
                                    st.write(f"• {label}")
                                if len(ui_analysis['japanese_labels']) > 5:
                                    st.caption(f"... and {len(ui_analysis['japanese_labels']) - 5} more labels")
                        
                        # Screen breakdown
                        screen_breakdown = japanese_analysis.get('screen_language_breakdown', {})
                        if screen_breakdown:
                            st.subheader("📱 Screen Language Analysis")
                            
                            # Create a DataFrame for better display
                            screen_data = []
                            for screen_name, data in screen_breakdown.items():
                                screen_data.append({
                                    "Screen": screen_name,
                                    "Japanese Texts": data.get('japanese_text_count', 0),
                                    "Total Texts": data.get('total_text_count', 0),
                                    "Japanese %": f"{data.get('japanese_ratio', 0):.1%}",
                                    "Primarily Japanese": "✅" if data.get('is_primarily_japanese') else "❌"
                                })
                            
                            if screen_data:
                                df = pd.DataFrame(screen_data)
                                st.dataframe(df, use_container_width=True)
                else:
                    with st.expander("🌐 Language Analysis", expanded=False):
                        st.info("📝 This design appears to use primarily English/Latin text.")
                        if japanese_analysis.get('total_text_nodes', 0) > 0:
                            st.write(f"**Total text nodes analyzed:** {japanese_analysis.get('total_text_nodes', 0)}")
            else:
                with st.expander("🌐 Language Analysis", expanded=False):
                    st.info("📝 Language analysis not available for this design.")
            
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
