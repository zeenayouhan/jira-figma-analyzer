#!/usr/bin/env python3
"""
Fix VisualAnalysisResult dataclass to make metadata fields optional
"""

def fix_visual_analysis_result():
    # Read the current file
    with open('gpt4_vision_integration.py', 'r') as f:
        content = f.read()
    
    # Fix the metadata fields to be optional
    old_metadata = '''    # Metadata
    analysis_timestamp: str
    confidence_score: float
    processing_time: Optional[float] = None'''
    
    new_metadata = '''    # Metadata
    analysis_timestamp: str = ""
    confidence_score: float = 0.0
    processing_time: Optional[float] = None'''
    
    content = content.replace(old_metadata, new_metadata)
    
    # Write the updated content
    with open('gpt4_vision_integration.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed VisualAnalysisResult metadata fields to be optional")

if __name__ == "__main__":
    fix_visual_analysis_result()
