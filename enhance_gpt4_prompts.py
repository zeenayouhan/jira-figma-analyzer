#!/usr/bin/env python3
"""
Enhance GPT-4 Vision prompts to include all comprehensive analysis fields
"""

def enhance_gpt4_prompts():
    # Read the current file
    with open('gpt4_vision_integration.py', 'r') as f:
        content = f.read()
    
    # Replace the UI analysis prompt with comprehensive version
    old_prompt = '''    def _create_ui_analysis_prompt(self, ticket_context: Dict[str, Any] = None) -> str:
        """Create a prompt for general UI mockup analysis."""
        return """
You are a senior UX/UI designer specializing in mobile app design and Japanese localization.
Analyze this UI design image and provide detailed insights.

Focus on:
1. **Component Identification**: What UI elements do you see?
2. **Design Quality**: How well is this designed? What could be improved?
3. **Japanese Elements**: Any Japanese text or culturally-specific design patterns?
4. **Implementation Complexity**: How complex would this be to implement?
5. **User Experience**: How intuitive and user-friendly is this design?
6. **Accessibility**: What accessibility considerations should be addressed?

Provide your analysis in this exact JSON format:

{
  "ui_components": ["button", "form", "navigation"],
  "layout_assessment": {
    "structure": "Description of layout structure",
    "spacing": "Analysis of spacing and alignment",
    "responsiveness": "Mobile responsiveness assessment"
  },
  "color_analysis": {
    "primary_colors": ["#color1", "#color2"],
    "contrast_ratio": "Assessment of contrast",
    "accessibility": "WCAG compliance notes"
  },
  "typography_analysis": {
    "fonts_used": ["Font1", "Font2"],
    "hierarchy": "Typography hierarchy assessment",
    "readability": "Readability analysis"
  },
  "design_quality_score": 8.5,
  "accessibility": {
    "issues": ["Issue 1", "Issue 2"],
    "score": 7.0,
    "recommendations": ["Rec 1", "Rec 2"]
  },
  "japanese_elements": ["Japanese text found"],
  "improvements": ["Improvement 1", "Improvement 2"],
  "design_patterns": ["Pattern 1", "Pattern 2"],
  "navigation_assessment": {
    "clarity": "Navigation clarity assessment",
    "hierarchy": "Information hierarchy evaluation",
    "user_flow": "User flow analysis"
  }
}
        """.strip()'''
    
    new_prompt = '''    def _create_ui_analysis_prompt(self, ticket_context: Dict[str, Any] = None) -> str:
        """Create a prompt for general UI mockup analysis."""
        return """
You are a senior UX/UI designer specializing in mobile app design and Japanese localization.
Analyze this UI design image and provide comprehensive detailed insights.

Focus on:
1. **Component Identification**: What UI elements do you see?
2. **Design Quality**: How well is this designed? What could be improved?
3. **Japanese Elements**: Any Japanese text or culturally-specific design patterns?
4. **Implementation Complexity**: How complex would this be to implement?
5. **User Experience**: How intuitive and user-friendly is this design?
6. **Accessibility**: What accessibility considerations should be addressed?
7. **Layout & Visual Hierarchy**: How is the layout structured?
8. **Color & Typography**: What design system elements are used?
9. **User Flow**: How does the user navigate through this interface?

Provide your analysis in this exact JSON format:

{
  "ui_components": ["button", "form", "navigation", "list", "profile picture", "text"],
  "layout_assessment": {
    "structure": "Description of layout structure and organization",
    "hierarchy": "Visual hierarchy and information architecture",
    "spacing": "Analysis of spacing, padding, and alignment",
    "responsiveness": "Mobile responsiveness assessment"
  },
  "color_scheme_analysis": {
    "primary_colors": ["#color1", "#color2"],
    "contrast_rating": "High/Medium/Low contrast assessment",
    "consistency": "Color consistency across the design",
    "accessibility": "WCAG compliance notes"
  },
  "typography_analysis": {
    "font_hierarchy": "Typography hierarchy and font usage",
    "readability": "Text readability and legibility assessment",
    "consistency": "Typography consistency across the design",
    "fonts_used": ["Font1", "Font2"]
  },
  "design_quality_score": 8.5,
  "accessibility_score": 7.0,
  "accessibility": {
    "color_contrast": "Color contrast assessment",
    "text_size": "Text size and legibility evaluation",
    "interactive_elements": "Interactive element accessibility",
    "issues": ["Issue 1", "Issue 2"],
    "recommendations": ["Rec 1", "Rec 2"]
  },
  "japanese_elements_detected": ["Japanese text found", "Cultural elements"],
  "improvement_suggestions": ["Improvement 1", "Improvement 2", "Improvement 3"],
  "design_patterns_identified": ["Pattern 1", "Pattern 2"],
  "navigation_assessment": {
    "clarity": "Navigation clarity and intuitiveness",
    "intuitiveness": "How intuitive is the navigation",
    "accessibility": "Navigation accessibility considerations",
    "hierarchy": "Information hierarchy evaluation"
  },
  "user_flow_analysis": {
    "flow_clarity": "How clear is the user flow",
    "step_count": "Number of steps required",
    "complexity": "Flow complexity assessment"
  },
  "implementation_complexity": {
    "overall_complexity": "Low/Medium/High",
    "technical_challenges": ["Challenge 1", "Challenge 2"],
    "development_time": "Estimated development time"
  },
  "design_quality_breakdown": {
    "visual_appeal": "Visual appeal assessment",
    "usability": "Usability evaluation",
    "consistency": "Design consistency rating"
  }
}
        """.strip()'''
    
    content = content.replace(old_prompt, new_prompt)
    
    # Write the updated content
    with open('gpt4_vision_integration.py', 'w') as f:
        f.write(content)
    
    print("✅ Enhanced GPT-4 Vision prompts with comprehensive analysis fields")

if __name__ == "__main__":
    enhance_gpt4_prompts()
