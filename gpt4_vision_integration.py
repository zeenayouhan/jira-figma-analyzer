#!/usr/bin/env python3
"""
GPT-4 Vision Integration for Jira-Figma Analyzer

This module provides advanced visual analysis capabilities using OpenAI's GPT-4 Vision API
to analyze Figma designs, screenshots, and UI mockups directly from images.
"""

import os
import base64
import requests
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from PIL import Image
import io

@dataclass
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
    accessibility_assessment: Dict[str, Any]
    design_patterns_identified: List[str]
    improvement_suggestions: List[str]
    
    # User Experience Analysis
    user_flow_insights: List[str]
    navigation_assessment: Dict[str, Any]
    interaction_recommendations: List[str]
    
    # Technical Implementation
    implementation_complexity: str  # 'low', 'medium', 'high'
    development_recommendations: List[str]
    potential_issues: List[str]
    
    # Metadata
    analysis_timestamp: str
    confidence_score: float
    processing_time: Optional[float] = None

class GPT4VisionAnalyzer:
    """Main class for GPT-4 Vision-powered visual analysis."""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        } if self.openai_api_key else {}
        
        if not self.openai_api_key:
            print("⚠️ OpenAI API key not found. GPT-4 Vision features will be limited.")
        else:
            print("🤖 GPT-4 Vision Analyzer initialized")
    
    def analyze_figma_screenshot(self, image_path: str, context: Dict[str, Any] = None) -> Optional[VisualAnalysisResult]:
        """Analyze a Figma screenshot using GPT-4 Vision."""
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return None
        
        print(f"🔍 Analyzing Figma screenshot with GPT-4 Vision: {os.path.basename(image_path)}")
        
        # Encode image to base64
        image_base64 = self._encode_image_to_base64(image_path)
        if not image_base64:
            return None
        
        # Generate analysis prompt
        analysis_prompt = self._create_figma_analysis_prompt(context)
        
        # Call GPT-4 Vision API
        response = self._call_gpt4_vision_api(image_base64, analysis_prompt)
        if not response:
            return None
        
        # Parse and structure the response
        return self._parse_vision_response(response, 'figma_screenshot', image_path, context)
    
    def analyze_ui_mockup(self, image_path: str, ticket_context: Dict[str, Any] = None) -> Optional[VisualAnalysisResult]:
        """Analyze a UI mockup or design image."""
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return None
        
        print(f"🎨 Analyzing UI mockup with GPT-4 Vision: {os.path.basename(image_path)}")
        
        # Encode image to base64
        image_base64 = self._encode_image_to_base64(image_path)
        if not image_base64:
            return None
        
        # Generate analysis prompt
        analysis_prompt = self._create_ui_analysis_prompt(ticket_context)
        
        # Call GPT-4 Vision API
        response = self._call_gpt4_vision_api(image_base64, analysis_prompt)
        if not response:
            return None
        
        # Parse and structure the response
        return self._parse_vision_response(response, 'uploaded_image', image_path, ticket_context)
    
    def analyze_design_comparison(self, image_paths: List[str], comparison_context: str = None) -> Optional[Dict[str, Any]]:
        """Compare multiple design images and provide analysis."""
        if len(image_paths) < 2:
            print("❌ Need at least 2 images for comparison")
            return None
        
        print(f"🔄 Comparing {len(image_paths)} designs with GPT-4 Vision")
        
        # Encode all images
        encoded_images = []
        for path in image_paths:
            encoded = self._encode_image_to_base64(path)
            if encoded:
                encoded_images.append({
                    "path": path,
                    "data": encoded
                })
        
        if len(encoded_images) < 2:
            print("❌ Failed to encode enough images for comparison")
            return None
        
        # Create comparison prompt
        comparison_prompt = self._create_comparison_prompt(comparison_context)
        
        # Call API with multiple images
        response = self._call_gpt4_vision_api_multiple(encoded_images, comparison_prompt)
        
        return self._parse_comparison_response(response) if response else None
    
    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Encode image to base64 for API submission."""
        try:
            # Open and potentially resize image for API efficiency
            with Image.open(image_path) as img:
                # Resize if too large (GPT-4 Vision has size limits)
                max_size = (2048, 2048)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    print(f"📏 Resized image to {img.size} for API efficiency")
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save to bytes
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                
                # Encode to base64
                image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                return image_data
                
        except Exception as e:
            print(f"❌ Error encoding image {image_path}: {e}")
            return None
    
    def _create_figma_analysis_prompt(self, context: Dict[str, Any] = None) -> str:
        """Create a comprehensive prompt for Figma design analysis."""
        base_prompt = """
You are a senior UX/UI designer and React Native developer with expertise in Japanese mobile app design. 
Analyze this Figma design screenshot and provide comprehensive insights.

ANALYSIS REQUIREMENTS:

1. **UI Components Identification**:
   - List all visible UI components (buttons, inputs, cards, etc.)
   - Identify navigation elements and their hierarchy
   - Note any custom components or design patterns

2. **Japanese Content Analysis**:
   - Identify all Japanese text elements (buttons, labels, content)
   - Assess Japanese typography quality and readability
   - Evaluate Japanese text layout and spacing
   - Check for proper Japanese character support

3. **Layout & Design Quality**:
   - Assess overall layout composition and balance
   - Evaluate spacing, alignment, and visual hierarchy
   - Rate design consistency and adherence to design systems
   - Identify any layout issues or improvements needed

4. **Color Scheme & Typography**:
   - Analyze color palette and contrast ratios
   - Evaluate typography choices and hierarchy
   - Check accessibility compliance (WCAG guidelines)
   - Assess brand consistency

5. **User Experience Assessment**:
   - Evaluate navigation flow and user journey
   - Identify potential usability issues
   - Assess information architecture and content organization
   - Rate overall user-friendliness

6. **Mobile/React Native Considerations**:
   - Assess adaptability for different screen sizes
   - Identify potential implementation challenges
   - Evaluate performance implications
   - Consider platform-specific design patterns (iOS/Android)

7. **Accessibility Evaluation**:
   - Check color contrast and readability
   - Assess button sizes and touch targets
   - Evaluate content structure and hierarchy
   - Identify accessibility improvements needed

Please provide your analysis in this exact JSON format:

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
  "design_patterns": ["Pattern 1", "Pattern 2"]
}
        """
        
        if context:
            ticket_info = f"""
TICKET CONTEXT:
- Title: {context.get('ticket_title', 'N/A')}
- Description: {context.get('ticket_description', 'N/A')}
- Priority: {context.get('ticket_priority', 'N/A')}
- Focus Areas: {', '.join(context.get('focus_areas', []))}
            """
            base_prompt += ticket_info
        
        return base_prompt.strip()
    
    def _create_ui_analysis_prompt(self, ticket_context: Dict[str, Any] = None) -> str:
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
        """.strip()
    
    def _create_comparison_prompt(self, comparison_context: str = None) -> str:
        """Create a prompt for comparing multiple designs."""
        base_prompt = """
You are a senior UX/UI designer. Compare these design images and provide detailed analysis.

For each image, analyze:
1. **Design Approach**: What design philosophy/approach is used?
2. **Strengths & Weaknesses**: What works well and what doesn't?
3. **Consistency**: How consistent are the designs with each other?
4. **Best Practices**: Which design follows best practices better?
5. **Recommendations**: Which elements should be adopted/avoided?

Provide a comprehensive comparison with specific recommendations.
        """
        
        if comparison_context:
            base_prompt += f"\n\nCONTEXT: {comparison_context}"
        
        return base_prompt.strip()
    
    def _call_gpt4_vision_api(self, image_base64: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Call GPT-4 Vision API with image and prompt."""
        if not self.openai_api_key:
            print("❌ OpenAI API key required for GPT-4 Vision")
            return None
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }
        
        try:
            print("🤖 Calling GPT-4 Vision API...")
            start_time = datetime.now()
            
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"⏱️ GPT-4 Vision processing completed in {processing_time:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                result['processing_time'] = processing_time
                return result
            else:
                print(f"❌ GPT-4 Vision API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error calling GPT-4 Vision API: {e}")
            return None
    
    def _call_gpt4_vision_api_multiple(self, encoded_images: List[Dict], prompt: str) -> Optional[Dict[str, Any]]:
        """Call GPT-4 Vision API with multiple images."""
        if not self.openai_api_key:
            return None
        
        # Create content array with prompt and all images
        content = [{"type": "text", "text": prompt}]
        
        for i, img_data in enumerate(encoded_images):
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_data['data']}",
                    "detail": "high"
                }
            })
        
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 3000,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"❌ Error in multi-image analysis: {e}")
            return None
    
    def _parse_vision_response(self, response: Dict[str, Any], source: str, image_path: str, context: Dict[str, Any] = None) -> VisualAnalysisResult:
        """Parse GPT-4 Vision response into structured result."""
        try:
            content = response['choices'][0]['message']['content']
            processing_time = response.get('processing_time', 0)
            
            # Try to parse as JSON, fallback to text parsing
            try:
                if '{' in content and '}' in content:
                    # Extract JSON from response
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    json_content = content[json_start:json_end]
                    parsed_data = json.loads(json_content)
                else:
                    # Fallback to text parsing
                    parsed_data = self._parse_text_response(content)
            except:
                parsed_data = self._parse_text_response(content)
            
            return VisualAnalysisResult(
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
            )
            
        except Exception as e:
            print(f"❌ Error parsing GPT-4 Vision response: {e}")
            return None
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """Fallback text parsing when JSON parsing fails."""
        # Basic text parsing logic
        return {
            'ui_components': [],
            'layout_assessment': {'quality': 'good'},
            'design_quality_score': 7.0,
            'improvements': [content[:200] + "..." if len(content) > 200 else content],
            'confidence_score': 0.6
        }
    
    def _parse_comparison_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse comparison analysis response."""
        try:
            content = response['choices'][0]['message']['content']
            return {
                'comparison_analysis': content,
                'timestamp': datetime.now().isoformat(),
                'recommendations': []  # Could be enhanced with more parsing
            }
        except:
            return {}
    
    def get_analysis_context_for_ai(self, vision_result: VisualAnalysisResult) -> Dict[str, Any]:
        """Get structured context from vision analysis for AI question generation."""
        return {
            'visual_analysis': {
                'ui_components': vision_result.ui_components_identified,
                'design_quality_score': vision_result.design_quality_score,
                'japanese_elements': vision_result.japanese_elements_detected,
                'accessibility_issues': vision_result.accessibility_assessment.get('issues', []),
                'improvement_suggestions': vision_result.improvement_suggestions,
                'implementation_complexity': vision_result.implementation_complexity
            },
            'analysis_metadata': {
                'source': vision_result.image_source,
                'confidence': vision_result.confidence_score,
                'timestamp': vision_result.analysis_timestamp
            }
        }

# Example usage and testing
if __name__ == "__main__":
    analyzer = GPT4VisionAnalyzer()
    
    # Test with a sample image (if available)
    test_image = "sample_figma_screenshot.png"
    if os.path.exists(test_image):
        result = analyzer.analyze_figma_screenshot(test_image)
        if result:
            print(f"✅ Analysis completed with {result.confidence_score:.1%} confidence")
            print(f"🎯 Design quality score: {result.design_quality_score}/10")
            print(f"🇯🇵 Japanese elements found: {len(result.japanese_elements_detected)}")
    else:
        print("🧪 GPT-4 Vision Analyzer module created successfully!")
        print("📷 Ready to analyze Figma screenshots and UI mockups!") 