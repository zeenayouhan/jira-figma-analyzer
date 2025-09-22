import streamlit as st
import json
import os
from typing import Dict, List, Optional

class ImplementedScreensManager:
    """Manages already implemented screens/features with their Figma designs and technical details."""
    
    def __init__(self):
        self.data_file = "implemented_screens.json"
        self.screens = self.load_screens()
    
    def load_screens(self) -> List[Dict]:
        """Load implemented screens from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading screens data: {e}")
                return []
        return []
    
    def save_screens(self):
        """Save screens to JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.screens, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving screens data: {e}")
            return False
    
    def add_screen(self, screen_data: Dict):
        """Add a new implemented screen."""
        self.screens.append(screen_data)
        return self.save_screens()
    
    def update_screen(self, index: int, screen_data: Dict):
        """Update an existing screen."""
        if 0 <= index < len(self.screens):
            self.screens[index] = screen_data
            return self.save_screens()
        return False
    
    def delete_screen(self, index: int):
        """Delete a screen."""
        if 0 <= index < len(self.screens):
            del self.screens[index]
            return self.save_screens()
        return False
    
    def get_screen_by_figma_url(self, figma_url: str) -> Optional[Dict]:
        """Get screen data by Figma URL."""
        for screen in self.screens:
            if figma_url in screen.get('figma_links', []):
                return screen
        return None
    
    def search_screens(self, query: str) -> List[Dict]:
        """Search screens by query."""
        query = query.lower()
        results = []
        for screen in self.screens:
            if (query in screen.get('name', '').lower() or 
                query in screen.get('description', '').lower() or
                query in screen.get('framework', '').lower() or
                query in screen.get('feature_type', '').lower()):
                results.append(screen)
        return results

def render_implemented_screens_ui():
    """Render the implemented screens management UI."""
    st.header("🏗️ Implemented Screens Manager")
    st.markdown("Manage already implemented screens/features with their Figma designs, frameworks, and source code.")
    
    manager = ImplementedScreensManager()
    
    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 View Screens", 
        "➕ Add Screen", 
        "✏️ Edit Screen", 
        "🔍 Search Screens"
    ])
    
    with tab1:
        render_view_screens(manager)
    
    with tab2:
        render_add_screen(manager)
    
    with tab3:
        render_edit_screen(manager)
    
    with tab4:
        render_search_screens(manager)

def render_view_screens(manager: ImplementedScreensManager):
    """Render the view screens tab."""
    st.subheader("📋 Implemented Screens")
    
    if not manager.screens:
        st.info("No implemented screens found. Add some screens using the 'Add Screen' tab.")
        return
    
    # Display screens in a grid
    for i, screen in enumerate(manager.screens):
        with st.expander(f"🖥️ {screen.get('name', 'Unnamed Screen')} - {screen.get('feature_type', 'Unknown Type')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Description:** {screen.get('description', 'No description')}")
                st.write(f"**Framework:** {screen.get('framework', 'Not specified')}")
                st.write(f"**Status:** {screen.get('status', 'Unknown')}")
                st.write(f"**Last Updated:** {screen.get('last_updated', 'Unknown')}")
            
            with col2:
                st.write(f"**Feature Type:** {screen.get('feature_type', 'Unknown')}")
                st.write(f"**Complexity:** {screen.get('complexity', 'Unknown')}")
                st.write(f"**Team:** {screen.get('team', 'Not specified')}")
                
                # Figma links
                if screen.get('figma_links'):
                    st.write("**Figma Links:**")
                    for link in screen['figma_links']:
                        st.markdown(f"- [{link}]({link})")
                
                # Source code links
                if screen.get('source_code_links'):
                    st.write("**Source Code:**")
                    for link in screen['source_code_links']:
                        st.markdown(f"- [{link}]({link})")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Edit", key=f"edit_{i}"):
                    st.session_state.edit_screen_index = i
                    st.rerun()
            with col2:
                if st.button(f"Delete", key=f"delete_{i}"):
                    if manager.delete_screen(i):
                        st.success("Screen deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete screen.")
            with col3:
                if st.button(f"Copy Figma URL", key=f"copy_{i}"):
                    if screen.get('figma_links'):
                        st.code(screen['figma_links'][0])
                        st.success("Figma URL copied to clipboard!")

def render_add_screen(manager: ImplementedScreensManager):
    """Render the add screen tab."""
    st.subheader("➕ Add New Implemented Screen")
    
    with st.form("add_screen_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Screen/Feature Name *", placeholder="e.g., User Profile Screen")
            feature_type = st.selectbox("Feature Type *", [
                "Authentication", "Dashboard", "Profile Management", "Settings", 
                "Navigation", "Forms", "Lists/Tables", "Charts/Analytics",
                "Notifications", "Search/Filter", "Payment", "Social Features",
                "Mobile App Screen", "Web Page", "API Endpoint", "Other"
            ])
            framework = st.text_input("Framework/Technology *", placeholder="e.g., React, Vue.js, Flutter, Swift, Kotlin")
            status = st.selectbox("Implementation Status", [
                "Completed", "In Progress", "Testing", "Deployed", "Maintenance"
            ])
            complexity = st.selectbox("Complexity Level", ["Simple", "Medium", "Complex", "Very Complex"])
        
        with col2:
            team = st.text_input("Development Team", placeholder="e.g., Frontend Team, Mobile Team")
            last_updated = st.date_input("Last Updated")
            version = st.text_input("Version", placeholder="e.g., v1.2.3")
            performance_score = st.slider("Performance Score (1-10)", 1, 10, 5)
        
        description = st.text_area("Description *", placeholder="Describe what this screen/feature does...")
        
        # Figma links
        st.subheader("🎨 Design Information")
        figma_links = st.text_area("Figma Links (one per line)", placeholder="https://www.figma.com/design/...")
        
        # Source code information
        st.subheader("💻 Source Code Information")
        source_code_links = st.text_area("Source Code Links (one per line)", placeholder="https://bitbucket.org/...")
        repository = st.text_input("Repository", placeholder="e.g., bitbucket.org/company/project")
        file_paths = st.text_area("Key File Paths (one per line)", placeholder="src/components/ProfileScreen.jsx")
        
        # Technical details
        st.subheader("🔧 Technical Details")
        col1, col2 = st.columns(2)
        with col1:
            dependencies = st.text_area("Key Dependencies", placeholder="react, axios, styled-components")
            api_endpoints = st.text_area("API Endpoints Used", placeholder="/api/users/profile, /api/users/update")
        with col2:
            database_tables = st.text_area("Database Tables", placeholder="users, profiles, settings")
            environment_vars = st.text_area("Environment Variables", placeholder="REACT_APP_API_URL, API_KEY")
        
        # User experience details
        st.subheader("👥 User Experience")
        user_roles = st.text_input("Target User Roles", placeholder="e.g., Admin, User, Guest")
        accessibility_features = st.text_area("Accessibility Features", placeholder="Screen reader support, keyboard navigation")
        mobile_responsive = st.checkbox("Mobile Responsive")
        cross_browser_support = st.checkbox("Cross-browser Support")
        
        # Testing information
        st.subheader("🧪 Testing Information")
        test_coverage = st.slider("Test Coverage (%)", 0, 100, 0)
        test_framework = st.text_input("Test Framework", placeholder="Jest, Cypress, Selenium")
        test_files = st.text_area("Test File Paths", placeholder="src/__tests__/ProfileScreen.test.jsx")
        
        submitted = st.form_submit_button("Add Screen", type="primary")
        
        if submitted:
            if not name or not feature_type or not framework or not description:
                st.error("Please fill in all required fields (marked with *)")
                return
            
            # Prepare screen data
            screen_data = {
                "name": name,
                "feature_type": feature_type,
                "framework": framework,
                "status": status,
                "complexity": complexity,
                "team": team,
                "last_updated": str(last_updated),
                "version": version,
                "performance_score": performance_score,
                "description": description,
                "figma_links": [link.strip() for link in figma_links.split("\n") if link.strip()],
                "source_code_links": [link.strip() for link in source_code_links.split("\n") if link.strip()],
                "repository": repository,
                "file_paths": [path.strip() for path in file_paths.split("\n") if path.strip()],
                "dependencies": [dep.strip() for dep in dependencies.split(",") if dep.strip()],
                "api_endpoints": [endpoint.strip() for endpoint in api_endpoints.split("\n") if endpoint.strip()],
                "database_tables": [table.strip() for table in database_tables.split(",") if table.strip()],
                "environment_vars": [var.strip() for var in environment_vars.split("\n") if var.strip()],
                "user_roles": [role.strip() for role in user_roles.split(",") if role.strip()],
                "accessibility_features": [feature.strip() for feature in accessibility_features.split("\n") if feature.strip()],
                "mobile_responsive": mobile_responsive,
                "cross_browser_support": cross_browser_support,
                "test_coverage": test_coverage,
                "test_framework": test_framework,
                "test_files": [file.strip() for file in test_files.split("\n") if file.strip()]
            }
            
            if manager.add_screen(screen_data):
                st.success("✅ Screen added successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to add screen. Please try again.")

def render_edit_screen(manager: ImplementedScreensManager):
    """Render the edit screen tab."""
    st.subheader("✏️ Edit Screen")
    
    if not manager.screens:
        st.info("No screens available to edit.")
        return
    
    # Select screen to edit
    screen_options = [f"{i+1}. {screen.get('name', 'Unnamed')} - {screen.get('feature_type', 'Unknown')}" 
                     for i, screen in enumerate(manager.screens)]
    
    selected_index = st.selectbox("Select screen to edit:", range(len(manager.screens)), 
                                 format_func=lambda x: screen_options[x])
    
    if selected_index is not None:
        screen = manager.screens[selected_index]
        
        with st.form("edit_screen_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Screen/Feature Name *", value=screen.get('name', ''))
                feature_type = st.selectbox("Feature Type *", [
                    "Authentication", "Dashboard", "Profile Management", "Settings", 
                    "Navigation", "Forms", "Lists/Tables", "Charts/Analytics",
                    "Notifications", "Search/Filter", "Payment", "Social Features",
                    "Mobile App Screen", "Web Page", "API Endpoint", "Other"
                ], index=0 if screen.get('feature_type') not in [
                    "Authentication", "Dashboard", "Profile Management", "Settings", 
                    "Navigation", "Forms", "Lists/Tables", "Charts/Analytics",
                    "Notifications", "Search/Filter", "Payment", "Social Features",
                    "Mobile App Screen", "Web Page", "API Endpoint", "Other"
                ] else [
                    "Authentication", "Dashboard", "Profile Management", "Settings", 
                    "Navigation", "Forms", "Lists/Tables", "Charts/Analytics",
                    "Notifications", "Search/Filter", "Payment", "Social Features",
                    "Mobile App Screen", "Web Page", "API Endpoint", "Other"
                ].index(screen.get('feature_type', 'Other')))
                framework = st.text_input("Framework/Technology *", value=screen.get('framework', ''))
                status = st.selectbox("Implementation Status", [
                    "Completed", "In Progress", "Testing", "Deployed", "Maintenance"
                ], index=[
                    "Completed", "In Progress", "Testing", "Deployed", "Maintenance"
                ].index(screen.get('status', 'Completed')))
                # Parse complexity from potentially descriptive text
                current_complexity = screen.get('complexity', 'Medium')
                if isinstance(current_complexity, str):
                    if 'simple' in current_complexity.lower():
                        complexity_level = 'Simple'
                    elif 'complex' in current_complexity.lower() and 'very' in current_complexity.lower():
                        complexity_level = 'Very Complex'
                    elif 'complex' in current_complexity.lower():
                        complexity_level = 'Complex'
                    elif 'medium' in current_complexity.lower():
                        complexity_level = 'Medium'
                    else:
                        complexity_level = 'Medium'
                else:
                    complexity_level = 'Medium'
                
                complexity = st.selectbox("Complexity Level", ["Simple", "Medium", "Complex", "Very Complex"],
                                        index=["Simple", "Medium", "Complex", "Very Complex"].index(complexity_level))
            
            with col2:
                team = st.text_input("Development Team", value=screen.get('team', ''))
                last_updated = st.date_input("Last Updated", value=screen.get('last_updated', ''))
                version = st.text_input("Version", value=screen.get('version', ''))
                performance_score = st.slider("Performance Score (1-10)", 1, 10, screen.get('performance_score', 5))
            
            description = st.text_area("Description *", value=screen.get('description', ''))
            
            # Figma links
            st.subheader("🎨 Design Information")
            figma_links = st.text_area("Figma Links (one per line)", 
                                     value="\n".join(screen.get('figma_links', [])))
            
            # Source code information
            st.subheader("💻 Source Code Information")
            source_code_links = st.text_area("Source Code Links (one per line)", 
                                           value="\n".join(screen.get('source_code_links', [])))
            repository = st.text_input("Repository", value=screen.get('repository', ''))
            file_paths = st.text_area("Key File Paths (one per line)", 
                                    value="\n".join(screen.get('file_paths', [])))
            
            submitted = st.form_submit_button("Update Screen", type="primary")
            
            if submitted:
                if not name or not feature_type or not framework or not description:
                    st.error("Please fill in all required fields (marked with *)")
                    return
                
                # Update screen data
                updated_screen = screen.copy()
                updated_screen.update({
                    "name": name,
                    "feature_type": feature_type,
                    "framework": framework,
                    "status": status,
                    "complexity": complexity,
                    "team": team,
                    "last_updated": str(last_updated),
                    "version": version,
                    "performance_score": performance_score,
                    "description": description,
                    "figma_links": [link.strip() for link in figma_links.split("\n") if link.strip()],
                    "source_code_links": [link.strip() for link in source_code_links.split("\n") if link.strip()],
                    "repository": repository,
                    "file_paths": [path.strip() for path in file_paths.split("\n") if path.strip()]
                })
                
                if manager.update_screen(selected_index, updated_screen):
                    st.success("✅ Screen updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update screen. Please try again.")

def render_search_screens(manager: ImplementedScreensManager):
    """Render the search screens tab."""
    st.subheader("🔍 Search Screens")
    
    search_query = st.text_input("Search query", placeholder="Search by name, description, framework, or feature type...")
    
    if search_query:
        results = manager.search_screens(search_query)
        
        if results:
            st.write(f"Found {len(results)} screen(s) matching '{search_query}':")
            
            for screen in results:
                with st.expander(f"🖥️ {screen.get('name', 'Unnamed Screen')} - {screen.get('feature_type', 'Unknown Type')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {screen.get('description', 'No description')}")
                        st.write(f"**Framework:** {screen.get('framework', 'Not specified')}")
                        st.write(f"**Status:** {screen.get('status', 'Unknown')}")
                    
                    with col2:
                        st.write(f"**Feature Type:** {screen.get('feature_type', 'Unknown')}")
                        st.write(f"**Complexity:** {screen.get('complexity', 'Unknown')}")
                        st.write(f"**Team:** {screen.get('team', 'Not specified')}")
                    
                    # Figma links
                    if screen.get('figma_links'):
                        st.write("**Figma Links:**")
                        for link in screen['figma_links']:
                            st.markdown(f"- [{link}]({link})")
                    
                    # Source code links
                    if screen.get('source_code_links'):
                        st.write("**Source Code:**")
                        for link in screen['source_code_links']:
                            st.markdown(f"- [{link}]({link})")
        else:
            st.info(f"No screens found matching '{search_query}'")
    else:
        st.info("Enter a search query to find screens.")
