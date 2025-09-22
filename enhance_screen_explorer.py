#!/usr/bin/env python3
"""
Enhance Screen Explorer to include GPT-4 Vision analysis for Figma screens
"""

def enhance_screen_explorer():
    # Read the current file
    with open('complete_streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Find the section where screens are displayed and add GPT-4 Vision analysis
    old_screen_display = '''            # Display screens with detailed information
            st.subheader("📱 Screen Details")
            
            for idx, screen in enumerate(design.screen_details):
                if isinstance(screen, dict):
                    screen_name = screen.get('screen_name', f'Screen {idx + 1}')
                    with st.expander(f"📱 {screen_name}", expanded=False):
                        # Screen metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Form Fields", screen.get('field_count', 0))
                        with col2:
                            st.metric("CTAs", screen.get('cta_count', 0))
                        with col3:
                            st.metric("Navigation Items", screen.get('navigation_count', 0))
                        with col4:
                            st.metric("Content Areas", screen.get('content_area_count', 0))
                        
                        # Form fields
                        if screen.get('form_fields'):
                            st.write("**📝 Form Fields:**")
                            for field in screen['form_fields']:
                                field_type = field.get('type', 'Unknown')
                                label = field.get('label', 'No label')
                                placeholder = field.get('placeholder', '')
                                required = "✅ Required" if field.get('required', False) else "❌ Optional"
                                st.write(f"• **{label}** ({field_type}) - {placeholder} - {required}")
                        
                        # CTAs
                        if screen.get('ctas'):
                            st.write("**🔘 Call-to-Action Buttons:**")
                            for cta in screen['ctas']:
                                name = cta.get('name', 'Unknown')
                                text = cta.get('text', 'No text')
                                cta_type = cta.get('type', 'Unknown')
                                style = cta.get('style', 'Unknown')
                                st.write(f"• **{name}**: \"{text}\" ({cta_type}, {style})")
                        
                        # Navigation
                        if screen.get('navigation'):
                            st.write("**🧭 Navigation Elements:**")
                            for nav in screen['navigation']:
                                nav_type = nav.get('type', 'Unknown')
                                text = nav.get('text', 'No text')
                                st.write(f"• **{nav_type}**: \"{text}\"")
                        
                        # Content areas
                        if screen.get('content_areas'):
                            st.write("**📄 Content Areas:**")
                            for area in screen['content_areas']:
                                area_type = area.get('type', 'Unknown')
                                description = area.get('description', 'No description')
                                st.write(f"• **{area_type}**: {description}")
                        
                        # Natural language description
                        if screen.get('natural_description'):
                            st.write("**📝 User Flow Description:**")
                            st.write(screen['natural_description'])'''
    
    new_screen_display = '''            # Display screens with detailed information and GPT-4 Vision analysis
            st.subheader("📱 Screen Details")
            
            for idx, screen in enumerate(design.screen_details):
                if isinstance(screen, dict):
                    screen_name = screen.get('screen_name', f'Screen {idx + 1}')
                    with st.expander(f"📱 {screen_name}", expanded=False):
                        # Screen metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Form Fields", screen.get('field_count', 0))
                        with col2:
                            st.metric("CTAs", screen.get('cta_count', 0))
                        with col3:
                            st.metric("Navigation Items", screen.get('navigation_count', 0))
                        with col4:
                            st.metric("Content Areas", screen.get('content_area_count', 0))
                        
                        # GPT-4 Vision Analysis for this screen
                        st.markdown("---")
                        st.subheader("🤖 GPT-4 Vision Analysis")
                        
                        # Check if we have a screenshot for this screen
                        screen_screenshot = None
                        if hasattr(design, 'screenshots') and design.screenshots:
                            screen_screenshot = design.screenshots.get(screen_name)
                        
                        if screen_screenshot:
                            st.success("✅ Screenshot available for GPT-4 Vision analysis")
                            
                            # Initialize analyzer for GPT-4 Vision
                            from jira_figma_analyzer import JiraFigmaAnalyzer
                            analyzer = JiraFigmaAnalyzer()
                            
                            if analyzer.vision_analyzer:
                                try:
                                    # Run visual analysis on the screenshot
                                    visual_result = analyzer.analyze_visual_content(screen_screenshot)
                                    
                                    if visual_result:
                                        # Display key visual analysis results
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Design Quality", f"{visual_result.design_quality_score:.1f}/10")
                                        with col2:
                                            st.metric("UI Components", len(visual_result.ui_components_identified))
                                        with col3:
                                            st.metric("Accessibility Score", f"{visual_result.accessibility_score:.1f}/10")
                                        
                                        # Layout assessment
                                        if hasattr(visual_result, 'layout_assessment') and visual_result.layout_assessment:
                                            st.write("**📐 Layout Assessment:**")
                                            layout = visual_result.layout_assessment
                                            if isinstance(layout, dict):
                                                st.write(f"• **Structure**: {layout.get('structure', 'N/A')}")
                                                st.write(f"• **Hierarchy**: {layout.get('hierarchy', 'N/A')}")
                                                st.write(f"• **Spacing**: {layout.get('spacing', 'N/A')}")
                                            else:
                                                st.write(f"• {layout}")
                                        
                                        # Color analysis
                                        if hasattr(visual_result, 'color_scheme_analysis') and visual_result.color_scheme_analysis:
                                            st.write("**�� Color Analysis:**")
                                            colors = visual_result.color_scheme_analysis
                                            if isinstance(colors, dict):
                                                st.write(f"• **Primary Colors**: {colors.get('primary_colors', 'N/A')}")
                                                st.write(f"• **Contrast**: {colors.get('contrast_rating', 'N/A')}")
                                                st.write(f"• **Consistency**: {colors.get('consistency', 'N/A')}")
                                            else:
                                                st.write(f"• {colors}")
                                        
                                        # Typography analysis
                                        if hasattr(visual_result, 'typography_analysis') and visual_result.typography_analysis:
                                            st.write("**📝 Typography Analysis:**")
                                            typography = visual_result.typography_analysis
                                            if isinstance(typography, dict):
                                                st.write(f"• **Font Hierarchy**: {typography.get('font_hierarchy', 'N/A')}")
                                                st.write(f"• **Readability**: {typography.get('readability', 'N/A')}")
                                                st.write(f"• **Consistency**: {typography.get('consistency', 'N/A')}")
                                            else:
                                                st.write(f"• {typography}")
                                        
                                        # Navigation assessment
                                        if hasattr(visual_result, 'navigation_assessment') and visual_result.navigation_assessment:
                                            st.write("**🧭 Navigation Assessment:**")
                                            navigation = visual_result.navigation_assessment
                                            if isinstance(navigation, dict):
                                                st.write(f"• **Clarity**: {navigation.get('clarity', 'N/A')}")
                                                st.write(f"• **Intuitiveness**: {navigation.get('intuitiveness', 'N/A')}")
                                                st.write(f"• **Accessibility**: {navigation.get('accessibility', 'N/A')}")
                                            else:
                                                st.write(f"• {navigation}")
                                        
                                        # Accessibility assessment
                                        if hasattr(visual_result, 'accessibility') and visual_result.accessibility:
                                            st.write("**♿ Accessibility Assessment:**")
                                            accessibility = visual_result.accessibility
                                            if isinstance(accessibility, dict):
                                                st.write(f"• **Color Contrast**: {accessibility.get('color_contrast', 'N/A')}")
                                                st.write(f"• **Text Size**: {accessibility.get('text_size', 'N/A')}")
                                                st.write(f"• **Interactive Elements**: {accessibility.get('interactive_elements', 'N/A')}")
                                            else:
                                                st.write(f"• {accessibility}")
                                        
                                        # Improvement suggestions
                                        if hasattr(visual_result, 'improvement_suggestions') and visual_result.improvement_suggestions:
                                            st.write("**💡 Improvement Suggestions:**")
                                            for suggestion in visual_result.improvement_suggestions[:3]:
                                                st.write(f"• {suggestion}")
                                        
                                        # Japanese elements
                                        if hasattr(visual_result, 'japanese_elements_detected') and visual_result.japanese_elements_detected:
                                            st.write("**🇯🇵 Japanese Elements Detected:**")
                                            for element in visual_result.japanese_elements_detected[:5]:
                                                st.write(f"• {element}")
                                        
                                    else:
                                        st.warning("⚠️ GPT-4 Vision analysis failed for this screen")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error in GPT-4 Vision analysis: {e}")
                            else:
                                st.warning("⚠️ GPT-4 Vision not available")
                        else:
                            st.info("ℹ️ No screenshot available for GPT-4 Vision analysis")
                        
                        st.markdown("---")
                        
                        # Form fields
                        if screen.get('form_fields'):
                            st.write("**📝 Form Fields:**")
                            for field in screen['form_fields']:
                                field_type = field.get('type', 'Unknown')
                                label = field.get('label', 'No label')
                                placeholder = field.get('placeholder', '')
                                required = "✅ Required" if field.get('required', False) else "❌ Optional"
                                st.write(f"• **{label}** ({field_type}) - {placeholder} - {required}")
                        
                        # CTAs
                        if screen.get('ctas'):
                            st.write("**🔘 Call-to-Action Buttons:**")
                            for cta in screen['ctas']:
                                name = cta.get('name', 'Unknown')
                                text = cta.get('text', 'No text')
                                cta_type = cta.get('type', 'Unknown')
                                style = cta.get('style', 'Unknown')
                                st.write(f"• **{name}**: \"{text}\" ({cta_type}, {style})")
                        
                        # Navigation
                        if screen.get('navigation'):
                            st.write("**🧭 Navigation Elements:**")
                            for nav in screen['navigation']:
                                nav_type = nav.get('type', 'Unknown')
                                text = nav.get('text', 'No text')
                                st.write(f"• **{nav_type}**: \"{text}\"")
                        
                        # Content areas
                        if screen.get('content_areas'):
                            st.write("**📄 Content Areas:**")
                            for area in screen['content_areas']:
                                area_type = area.get('type', 'Unknown')
                                description = area.get('description', 'No description')
                                st.write(f"• **{area_type}**: {description}")
                        
                        # Natural language description
                        if screen.get('natural_description'):
                            st.write("**📝 User Flow Description:**")
                            st.write(screen['natural_description'])'''
    
    # Replace the old screen display with the new one
    content = content.replace(old_screen_display, new_screen_display)
    
    # Write the updated content
    with open('complete_streamlit_app.py', 'w') as f:
        f.write(content)
    
    print("✅ Enhanced Screen Explorer with GPT-4 Vision analysis")

if __name__ == "__main__":
    enhance_screen_explorer()
