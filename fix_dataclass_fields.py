#!/usr/bin/env python3
"""
Fix dataclass field ordering issue
"""

def fix_dataclass_fields():
    # Read the current file
    with open('gpt4_vision_integration.py', 'r') as f:
        content = f.read()
    
    # Fix the dataclass by removing the problematic legacy fields
    old_dataclass = '''@dataclass
class VisualAnalysisResult:
    """Results from GPT-4 Vision analysis."""
    analysis_id: str
    image_source: str  # 'figma_screenshot', 'uploaded_image', 'figma_export'
    
    # Visual Analysis
    ui_components_identified: List[str]
    layout_assessment: Dict[str, Any]
    color_scheme_analysis: Dict[str, Any]
    typography_analysis: Dict[str, Any]
    
    # Japanese Content Analysis
    japanese_elements_detected: List[str]
    japanese_text_quality: Dict[str, Any]
    localization_recommendations: List[str]
    
    # Design Quality Assessment
    design_quality_score: float  # 0-10
    accessibility_score: float  # 0-10
    accessibility: Dict[str, Any]  # Alias for accessibility_assessment
    design_patterns_identified: List[str]
    improvement_suggestions: List[str]
    design_quality_breakdown: Dict[str, Any]
    
    # User Experience Analysis
    user_flow_insights: List[str]
    user_flow_analysis: Dict[str, Any]
    navigation_assessment: Dict[str, Any]
    interaction_recommendations: List[str]
    
    # Technical Implementation
    implementation_complexity: str  # 'low', 'medium', 'high'
    development_recommendations: List[str]
    potential_issues: List[str]
    
    # Legacy fields for backward compatibility
    accessibility_assessment: Dict[str, Any] = None
    color_scheme_analysis: Dict[str, Any] = None'''
    
    new_dataclass = '''@dataclass
class VisualAnalysisResult:
    """Results from GPT-4 Vision analysis."""
    analysis_id: str
    image_source: str  # 'figma_screenshot', 'uploaded_image', 'figma_export'
    
    # Visual Analysis
    ui_components_identified: List[str]
    layout_assessment: Dict[str, Any]
    color_scheme_analysis: Dict[str, Any]
    typography_analysis: Dict[str, Any]
    
    # Japanese Content Analysis
    japanese_elements_detected: List[str]
    japanese_text_quality: Dict[str, Any]
    localization_recommendations: List[str]
    
    # Design Quality Assessment
    design_quality_score: float  # 0-10
    accessibility_score: float  # 0-10
    accessibility: Dict[str, Any]  # Alias for accessibility_assessment
    design_patterns_identified: List[str]
    improvement_suggestions: List[str]
    design_quality_breakdown: Dict[str, Any]
    
    # User Experience Analysis
    user_flow_insights: List[str]
    user_flow_analysis: Dict[str, Any]
    navigation_assessment: Dict[str, Any]
    interaction_recommendations: List[str]
    
    # Technical Implementation
    implementation_complexity: Dict[str, Any]  # Changed to Dict for consistency
    development_recommendations: List[str]
    potential_issues: List[str]'''
    
    content = content.replace(old_dataclass, new_dataclass)
    
    # Write the updated content
    with open('gpt4_vision_integration.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed dataclass field ordering")

if __name__ == "__main__":
    fix_dataclass_fields()
