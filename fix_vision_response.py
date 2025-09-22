#!/usr/bin/env python3
"""
Fix GPT-4 Vision response parsing to match VisualAnalysisResult dataclass
"""

def fix_vision_response():
    # Read the current file
    with open('gpt4_vision_integration.py', 'r') as f:
        content = f.read()
    
    # Fix the VisualAnalysisResult constructor call
    old_constructor = '''            return VisualAnalysisResult(
                analysis_id=f"gpt4v_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                image_source=source,
                
                # Extract structured data with fallbacks
                ui_components_identified=parsed_data.get('ui_components', []),
                layout_assessment=parsed_data.get('layout_assessment', {}),
                color_scheme_analysis=parsed_data.get('color_analysis', {}),
                typography_analysis=parsed_data.get('typography_analysis', {}),
                
                japanese_elements_detected=parsed_data.get('japanese_elements', []),
                japanese_text_quality=parsed_data.get('japanese_quality', {}),
                localization_recommendations=parsed_data.get('localization_recommendations', []),
                
                design_quality_score=parsed_data.get('design_quality_score', 7.0),
                accessibility_assessment=parsed_data.get('accessibility', {}),
                design_patterns_identified=parsed_data.get('design_patterns', []),
                improvement_suggestions=parsed_data.get('improvements', []),
                
                user_flow_insights=parsed_data.get('user_flow_insights', []),
                navigation_assessment=parsed_data.get('navigation_assessment', {}),
                interaction_recommendations=parsed_data.get('interaction_recommendations', []),
                
                implementation_complexity=parsed_data.get('implementation_complexity', 'medium'),
                development_recommendations=parsed_data.get('development_recommendations', []),
                potential_issues=parsed_data.get('potential_issues', []),
                
                analysis_timestamp=datetime.now().isoformat(),
                confidence_score=parsed_data.get('confidence_score', 0.8),
                processing_time=processing_time
            )'''
    
    new_constructor = '''            return VisualAnalysisResult(
                analysis_id=f"gpt4v_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                image_source=source,
                
                # Extract structured data with fallbacks
                ui_components_identified=parsed_data.get('ui_components', []),
                layout_assessment=parsed_data.get('layout_assessment', {}),
                color_scheme_analysis=parsed_data.get('color_analysis', {}),
                typography_analysis=parsed_data.get('typography_analysis', {}),
                
                japanese_elements_detected=parsed_data.get('japanese_elements', []),
                japanese_text_quality=parsed_data.get('japanese_quality', {}),
                localization_recommendations=parsed_data.get('localization_recommendations', []),
                
                design_quality_score=parsed_data.get('design_quality_score', 7.0),
                accessibility_score=parsed_data.get('accessibility', {}).get('score', 7.0) if isinstance(parsed_data.get('accessibility', {}), dict) else 7.0,
                accessibility=parsed_data.get('accessibility', {}),
                design_patterns_identified=parsed_data.get('design_patterns', []),
                improvement_suggestions=parsed_data.get('improvements', []),
                design_quality_breakdown=parsed_data.get('design_quality_breakdown', {}),
                
                user_flow_insights=parsed_data.get('user_flow_insights', []),
                user_flow_analysis=parsed_data.get('user_flow_analysis', {}),
                navigation_assessment=parsed_data.get('navigation_assessment', {}),
                interaction_recommendations=parsed_data.get('interaction_recommendations', []),
                
                implementation_complexity=parsed_data.get('implementation_complexity', {}),
                development_recommendations=parsed_data.get('development_recommendations', []),
                potential_issues=parsed_data.get('potential_issues', []),
                
                analysis_timestamp=datetime.now().isoformat(),
                confidence_score=parsed_data.get('confidence_score', 0.8),
                processing_time=processing_time
            )'''
    
    content = content.replace(old_constructor, new_constructor)
    
    # Write the updated content
    with open('gpt4_vision_integration.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed GPT-4 Vision response parsing to match dataclass")

if __name__ == "__main__":
    fix_vision_response()
