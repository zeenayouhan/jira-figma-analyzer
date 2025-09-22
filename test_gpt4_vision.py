#!/usr/bin/env python3
"""
Test GPT-4 Vision analysis with a simple test
"""

from jira_figma_analyzer import JiraFigmaAnalyzer
import os

def test_gpt4_vision():
    print("🧪 Testing GPT-4 Vision analysis...")
    
    analyzer = JiraFigmaAnalyzer()
    
    if not analyzer.vision_analyzer:
        print("❌ Vision analyzer not available")
        return
    
    print("✅ Vision analyzer available")
    
    # Test with a simple image (create a test image)
    from PIL import Image
    import tempfile
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    temp_path = tempfile.mktemp(suffix='.png')
    img.save(temp_path)
    
    print(f"📸 Created test image: {temp_path}")
    
    try:
        # Run analysis
        print("🔍 Running GPT-4 Vision analysis...")
        result = analyzer.analyze_visual_content(temp_path)
        
        if result:
            print("✅ Analysis completed successfully!")
            print(f"Design Quality Score: {result.design_quality_score}")
            print(f"UI Components: {len(result.ui_components_identified)}")
            print(f"Accessibility Score: {result.accessibility_score}")
            print(f"Japanese Elements: {len(result.japanese_elements_detected)}")
            
            if hasattr(result, 'layout_assessment') and result.layout_assessment:
                print(f"Layout Assessment: {result.layout_assessment}")
            
            if hasattr(result, 'improvement_suggestions') and result.improvement_suggestions:
                print(f"Improvement Suggestions: {result.improvement_suggestions[:3]}")
        else:
            print("❌ Analysis returned None")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print("🧹 Cleaned up test image")

if __name__ == "__main__":
    test_gpt4_vision()
