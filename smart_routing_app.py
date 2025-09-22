"""
Smart Routing Streamlit App
Enhanced Jira-Figma Analyzer with Smart Routing capabilities
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional

# Import the main analyzer
from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket
from smart_routing_system import SmartRoutingSystem, DeveloperProfile

def main():
    st.set_page_config(
        page_title="Smart Routing - Jira Figma Analyzer",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Smart Routing System</h1>', unsafe_allow_html=True)
    st.markdown("**Intelligent ticket assignment and team management**")
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        with st.spinner("Initializing Smart Routing System..."):
            st.session_state.analyzer = JiraFigmaAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Navigation")
        page = st.selectbox(
            "Choose a page:",
            [
                "🏠 Dashboard",
                "📋 Analyze Ticket",
                "👥 Team Management", 
                "📊 Analytics",
                "⚙️ Settings"
            ]
        )
    
    # Main content based on page selection
    if page == "🏠 Dashboard":
        dashboard_page(analyzer)
    elif page == "📋 Analyze Ticket":
        analyze_ticket_page(analyzer)
    elif page == "👥 Team Management":
        team_management_page(analyzer)
    elif page == "📊 Analytics":
        analytics_page(analyzer)
    elif page == "⚙️ Settings":
        settings_page(analyzer)

def dashboard_page(analyzer):
    """Main dashboard with overview metrics"""
    st.header("🏠 Smart Routing Dashboard")
    
    # Get team analytics
    if analyzer.smart_routing:
        analytics = analyzer.get_team_analytics()
        if analytics:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Developers",
                    analytics['team_overview']['total_developers'],
                    help="Number of developers in the system"
                )
            
            with col2:
                st.metric(
                    "Team Utilization",
                    analytics['team_overview']['current_utilization'],
                    help="Current workload vs capacity"
                )
            
            with col3:
                st.metric(
                    "Overloaded",
                    analytics['team_overview']['overloaded_count'],
                    help="Developers at >90% capacity"
                )
            
            with col4:
                st.metric(
                    "Underutilized",
                    analytics['team_overview']['underutilized_count'],
                    help="Developers at <30% capacity"
                )
            
            # Developer performance overview
            st.subheader("👥 Developer Performance Overview")
            
            if analytics['developers']:
                df = pd.DataFrame(analytics['developers'])
                
                # Performance score chart
                fig_performance = px.bar(
                    df, 
                    x='name', 
                    y='performance_score',
                    title="Developer Performance Scores",
                    color='performance_score',
                    color_continuous_scale='RdYlGn'
                )
                fig_performance.update_layout(height=400)
                st.plotly_chart(fig_performance, use_container_width=True)
                
                # Workload distribution
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_workload = px.bar(
                        df,
                        x='name',
                        y='current_workload',
                        title="Current Workload",
                        color='current_workload',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig_workload, use_container_width=True)
                
                with col2:
                    fig_utilization = px.bar(
                        df,
                        x='name',
                        y='utilization',
                        title="Utilization Rate",
                        color='utilization',
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig_utilization, use_container_width=True)
                
                # Detailed developer table
                st.subheader("📋 Developer Details")
                st.dataframe(df.drop(columns=["top_skills"]), width="stretch")
                
                # Display top skills separately
                if "top_skills" in df.columns:
                    st.subheader("🎯 Top Skills by Developer")
                    for _, row in df.iterrows():
                        st.write(f"**{row["name"]}:** {row["top_skills"]}")            
            # Recommendations
            if analytics['recommendations']:
                st.subheader("💡 Workload Recommendations")
                for rec in analytics['recommendations']:
                    st.warning(f"Consider reassigning work from {rec['from']} to {rec['to']}: {rec['reason']}")
        else:
            st.error("Unable to load team analytics")
    else:
        st.error("Smart routing system not available")

def analyze_ticket_page(analyzer):
    """Analyze a ticket and get smart routing recommendations"""
    st.header("📋 Analyze Ticket with Smart Routing")
    
    # Ticket input form
    with st.form("ticket_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            ticket_id = st.text_input("Ticket ID", value="HAB-123", help="Enter the Jira ticket ID")
            title = st.text_area("Title", value="Implement Japanese localization for mobile app login screen", help="Brief description of the ticket")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=2)
        
        with col2:
            description = st.text_area(
                "Description", 
                value="Add Japanese language support to the React Native login screen with proper RTL layout and cultural considerations. Include form validation messages in Japanese.",
                help="Detailed description of the requirements"
            )
            deadline = st.date_input("Deadline (Optional)", help="Target completion date")
        
        # Figma and media uploads
        st.subheader("🎨 Design Files")
        figma_url = st.text_input("Figma URL (Optional)", help="Link to Figma design file")
        
        col1, col2 = st.columns(2)
        with col1:
            uploaded_pdf = st.file_uploader("PDF Design Files", type=['pdf'], help="Upload design PDFs")
        with col2:
            uploaded_media = st.file_uploader("Media Files", type=['png', 'jpg', 'jpeg', 'mp4', 'mov'], help="Upload images or videos")
        
        submitted = st.form_submit_button("🎯 Analyze with Smart Routing", type="primary")
    
    if submitted:
        # Prepare ticket data
        ticket_data = {
            'ticket_id': ticket_id,
            'title': title,
            'description': description,
            'priority': priority.lower(),
            'deadline': deadline.isoformat() if deadline else None,
            'figma_url': figma_url if figma_url else None
        }
        
        # Analyze ticket
        with st.spinner("Analyzing ticket and generating smart routing recommendations..."):
            # Get smart routing recommendations
            if analyzer.smart_routing:
                recommendations = analyzer.get_smart_routing_recommendations(ticket_data)
                
                if recommendations:
                    # Display ticket analysis
                    st.subheader("�� Ticket Analysis")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Complexity", f"{recommendations['ticket_analysis']['complexity_level']}/10")
                    with col2:
                        st.metric("Estimated Effort", f"{recommendations['ticket_analysis']['estimated_effort']} story points")
                    with col3:
                        st.metric("Priority", recommendations['ticket_analysis']['priority'].title())
                    
                    # Required skills
                    st.write("**Required Skills:**")
                    skills = recommendations['ticket_analysis']['required_skills']
                    if skills:
                        for skill in skills:
                            st.write(f"• {skill.replace('_', ' ').title()}")
                    else:
                        st.write("• No specific skills detected")
                    
                    # Smart routing recommendation
                    st.subheader("🎯 Smart Routing Recommendation")
                    
                    rec = recommendations['recommendation']
                    if rec['recommended_developer'] != "none":
                        # Success card for recommendation
                        st.markdown(f"""
                        <div class="success-card">
                            <h4>🏆 Recommended Developer: {rec['developer_name']}</h4>
                            <p><strong>Confidence Score:</strong> {rec['confidence_score']:.2f}/1.0</p>
                            <p><strong>Estimated Completion:</strong> {rec['estimated_completion_time']} days</p>
                            <p><strong>Workload Impact:</strong> {rec['workload_impact'].title()}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Reasoning
                        st.write("**Why this developer?**")
                        for reason in rec['reasoning']:
                            st.write(f"• {reason}")
                        
                        # Risk factors
                        if rec['risk_factors']:
                            st.write("**⚠️ Risk Factors:**")
                            for risk in rec['risk_factors']:
                                st.write(f"• {risk}")
                        
                        # Skill gaps
                        if rec['skill_gaps']:
                            st.write("**📚 Skill Gaps:**")
                            for gap in rec['skill_gaps']:
                                st.write(f"• {gap}")
                        
                        # Assignment action
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("✅ Assign Ticket", type="primary"):
                                success = analyzer.assign_ticket_to_developer(
                                    ticket_id, 
                                    rec['recommended_developer'], 
                                    rec['confidence_score'], 
                                    rec['workload_impact'],
                                    f"Auto-assigned by smart routing system"
                                )
                                if success:
                                    st.success("Ticket assigned successfully!")
                                else:
                                    st.error("Failed to assign ticket")
                        
                        with col2:
                            if st.button("📝 Add Notes"):
                                st.session_state.show_notes = True
                        
                        with col3:
                            if st.button("🔄 Reanalyze"):
                                st.rerun()
                        
                        # Alternative developers
                        if recommendations['alternatives']:
                            st.subheader("🔄 Alternative Developers")
                            alt_df = pd.DataFrame(recommendations['alternatives'])
                            st.dataframe(alt_df, use_container_width=True)
                    else:
                        st.error("No suitable developer found for this ticket")
                    
                    # Workload analysis
                    st.subheader("📊 Team Workload Impact")
                    workload = recommendations['workload_analysis']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Team Utilization", workload['current_utilization'])
                    with col2:
                        st.metric("Overloaded Developers", workload['overloaded_developers'])
                    with col3:
                        st.metric("Underutilized Developers", workload['underutilized_developers'])
                else:
                    st.error("Unable to generate smart routing recommendations")
            else:
                st.error("Smart routing system not available")
            
            # Regular analysis (if needed)
            if st.checkbox("Show detailed analysis"):
                try:
                    # Create JiraTicket object
                    ticket = JiraTicket(
                        ticket_id=ticket_id,
                        title=title,
                        description=description,
                        priority=priority,
                        assignee=None,
                        reporter=None,
                        labels=[],
                        components=[],
                        comments=[],
                        figma_urls=[figma_url] if figma_url else [],
                        pdf_design_files=[]
                    )
                    
                    # Analyze ticket
                    result = analyzer.analyze_ticket_content(ticket)
                    
                    # Display results
                    st.subheader("📊 Analysis Results")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Questions:**")
                        for i, question in enumerate(result.questions, 1):
                            st.write(f"{i}. {question}")
                    
                    with col2:
                        st.write("**Test Cases:**")
                        for i, test_case in enumerate(result.test_cases, 1):
                            st.write(f"{i}. {test_case}")
                    
                    if result.risks:
                        st.write("**Risks:**")
                        for i, risk in enumerate(result.risks, 1):
                            st.write(f"{i}. {risk}")
                
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

def team_management_page(analyzer):
    """Team management and developer profiles"""
    st.header("👥 Team Management")
    
    if not analyzer.smart_routing:
        st.error("Smart routing system not available")
        return
    
    # Tabs for different management functions
    tab1, tab2, tab3 = st.tabs(["👥 Developer Profiles", "➕ Add Developer", "📊 Performance Tracking"])
    
    with tab1:
        st.subheader("Current Team")
        
        analytics = analyzer.get_team_analytics()
        if analytics and analytics['developers']:
            df = pd.DataFrame(analytics['developers'])
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                availability_filter = st.selectbox("Filter by Availability", ["All", "Available", "Busy", "Unavailable"])
            with col2:
                sort_by = st.selectbox("Sort by", ["Performance Score", "Success Rate", "Current Workload", "Name"])
            
            # Apply filters
            if availability_filter != "All":
                df = df[df['availability'] == availability_filter.lower()]
            
            # Sort
            if sort_by == "Performance Score":
                df = df.sort_values('performance_score', ascending=False)
            elif sort_by == "Success Rate":
                df = df.sort_values('success_rate', ascending=False)
            elif sort_by == "Current Workload":
                df = df.sort_values('current_workload', ascending=False)
            else:
                df = df.sort_values('name')
            
            # Display table
            st.dataframe(df.drop(columns=["top_skills"]), width="stretch")
            
                # Display top skills separately
            if "top_skills" in df.columns:
                st.subheader("🎯 Top Skills by Developer")
                for _, row in df.iterrows():
                    st.write(f"**{row["name"]}:** {row["top_skills"]}")            
            # Individual developer details
            if st.checkbox("Show detailed developer profiles"):
                selected_dev = st.selectbox("Select Developer", df['name'].tolist())
                if selected_dev:
                    dev_data = df[df['name'] == selected_dev].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {dev_data['name']}")
                        st.write(f"**Performance Score:** {dev_data['performance_score']}/10")
                        st.write(f"**Success Rate:** {dev_data['success_rate']:.1f}%")
                        st.write(f"**Current Workload:** {dev_data['current_workload']}/{dev_data['max_capacity']}")
                    
                    with col2:
                        st.write(f"**Availability:** {dev_data['availability'].title()}")
                        st.write(f"**Utilization:** {dev_data['utilization']}")
                        st.write(f"**Top Skills:** {', '.join([f'{skill}({score})' for skill, score in dev_data['top_skills']])}")
        else:
            st.info("No developers found. Add developers to get started.")
    
    with tab2:
        st.subheader("Add New Developer")
        
        with st.form("add_developer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                dev_id = st.text_input("Developer ID", help="Unique identifier")
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                timezone = st.selectbox("Timezone", ["UTC", "Asia/Tokyo", "America/New_York", "Europe/London"])
            
            with col2:
                max_capacity = st.number_input("Max Capacity", min_value=1, max_value=20, value=5)
                performance_score = st.slider("Performance Score", 0.0, 10.0, 5.0)
                availability = st.selectbox("Availability", ["Available", "Busy", "Unavailable"])
            
            # Skills section
            st.subheader("Skills Assessment")
            skills = {}
            skill_names = ["react_native", "javascript", "python", "figma", "japanese", "testing", "api_integration", "database", "ui_ux", "accessibility"]
            
            cols = st.columns(3)
            for i, skill in enumerate(skill_names):
                with cols[i % 3]:
                    skills[skill] = st.slider(f"{skill.replace('_', ' ').title()}", 0.0, 10.0, 5.0)
            
            # Specializations
            specializations = st.multiselect(
                "Specializations",
                ["frontend", "backend", "mobile", "design", "testing", "devops"],
                default=["frontend"]
            )
            
            # Preferred ticket types
            preferred_types = st.multiselect(
                "Preferred Ticket Types",
                ["bug", "feature", "enhancement", "task"],
                default=["feature"]
            )
            
            submitted = st.form_submit_button("Add Developer", type="primary")
            
            if submitted:
                if not dev_id or not name or not email:
                    st.error("Please fill in all required fields")
                else:
                    # Create developer profile
                    developer = DeveloperProfile(
                        developer_id=dev_id,
                        name=name,
                        email=email,
                        skills=skills,
                        specializations=specializations,
                        current_workload=0,
                        max_capacity=max_capacity,
                        performance_score=performance_score,
                        availability=availability.lower(),
                        timezone=timezone,
                        working_hours={"monday": [9, 17], "tuesday": [9, 17], "wednesday": [9, 17], "thursday": [9, 17], "friday": [9, 16]},
                        preferred_ticket_types=preferred_types,
                        last_active=datetime.now().isoformat(),
                        success_rate=0.0,
                        avg_completion_time=0.0,
                        created_at=datetime.now().isoformat()
                    )
                    
                    success = analyzer.smart_routing.add_developer(developer)
                    if success:
                        st.success(f"Developer {name} added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add developer")
    
    with tab3:
        st.subheader("Performance Tracking")
        
        # Completion tracking form
        with st.form("completion_tracking_form"):
            st.write("Record ticket completion to update performance metrics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                completed_ticket_id = st.text_input("Completed Ticket ID")
            with col2:
                success_rating = st.slider("Success Rating (1-5)", 1, 5, 4)
            with col3:
                completion_time = st.number_input("Completion Time (days)", min_value=0.1, max_value=100.0, value=3.0)
            
            notes = st.text_area("Notes (Optional)")
            
            submitted = st.form_submit_button("Record Completion", type="primary")
            
            if submitted:
                if completed_ticket_id:
                    success = analyzer.record_ticket_completion(
                        completed_ticket_id, 
                        success_rating, 
                        completion_time, 
                        notes
                    )
                    if success:
                        st.success("Completion recorded successfully!")
                    else:
                        st.error("Failed to record completion")
                else:
                    st.error("Please enter a ticket ID")

def analytics_page(analyzer):
    """Advanced analytics and insights"""
    st.header("📊 Advanced Analytics")
    
    if not analyzer.smart_routing:
        st.error("Smart routing system not available")
        return
    
    analytics = analyzer.get_team_analytics()
    if not analytics:
        st.error("Unable to load analytics")
        return
    
    # Performance trends
    st.subheader("📈 Performance Trends")
    
    df = pd.DataFrame(analytics['developers'])
    
    # Performance distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig_performance = px.histogram(
            df, 
            x='performance_score',
            title="Performance Score Distribution",
            nbins=10
        )
        st.plotly_chart(fig_performance, use_container_width=True)
    
    with col2:
        fig_success = px.histogram(
            df, 
            x='success_rate',
            title="Success Rate Distribution",
            nbins=10
        )
        st.plotly_chart(fig_success, use_container_width=True)
    
    # Workload analysis
    st.subheader("⚖️ Workload Analysis")
    
    # Utilization scatter plot
    fig_utilization = px.scatter(
        df,
        x='current_workload',
        y='max_capacity',
        size='performance_score',
        color='success_rate',
        hover_name='name',
        title="Workload vs Capacity (Size = Performance, Color = Success Rate)",
        labels={'current_workload': 'Current Workload', 'max_capacity': 'Max Capacity'}
    )
    st.plotly_chart(fig_utilization, use_container_width=True)
    
    # Team efficiency metrics
    st.subheader("🎯 Team Efficiency Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    avg_performance = df['performance_score'].mean()
    avg_success = df['success_rate'].mean()
    total_capacity = df['max_capacity'].sum()
    total_workload = df['current_workload'].sum()
    
    with col1:
        st.metric("Avg Performance", f"{avg_performance:.1f}/10")
    with col2:
        st.metric("Avg Success Rate", f"{avg_success:.1f}%")
    with col3:
        st.metric("Total Capacity", total_capacity)
    with col4:
        st.metric("Capacity Utilization", f"{(total_workload/total_capacity)*100:.1f}%")
    
    # Recommendations
    if analytics['recommendations']:
        st.subheader("💡 Smart Recommendations")
        for rec in analytics['recommendations']:
            st.info(f"**Reassignment Suggestion:** Move work from {rec['from']} to {rec['to']} - {rec['reason']}")

def settings_page(analyzer):
    """System settings and configuration"""
    st.header("⚙️ Settings")
    
    st.subheader("Smart Routing Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Status**")
        if analyzer.smart_routing:
            st.success("✅ Smart routing system is active")
        else:
            st.error("❌ Smart routing system is not available")
    
    with col2:
        st.write("**Database Status**")
        if os.path.exists("ticket_storage.db"):
            st.success("✅ Database is available")
        else:
            st.warning("⚠️ Database not found")
    
    # Export/Import functionality
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Team Data"):
            if analyzer.smart_routing:
                # Export developer profiles
                with open("developer_profiles.json", "r") as f:
                    data = f.read()
                
                st.download_button(
                    label="Download Developer Profiles",
                    data=data,
                    file_name=f"developer_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.error("Smart routing system not available")
    
    with col2:
        uploaded_file = st.file_uploader("📥 Import Team Data", type=['json'])
        if uploaded_file:
            if st.button("Import Data"):
                try:
                    data = json.load(uploaded_file)
                    st.success("Data imported successfully!")
                except Exception as e:
                    st.error(f"Import failed: {e}")
    
    # System information
    st.subheader("System Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.write("**Version:** 1.0.0")
        st.write("**Last Updated:** 2024-01-15")
    
    with info_col2:
        st.write("**Features:**")
        st.write("• Smart ticket assignment")
        st.write("• Workload balancing")
        st.write("• Performance tracking")
        st.write("• Team analytics")

if __name__ == "__main__":
    main()
