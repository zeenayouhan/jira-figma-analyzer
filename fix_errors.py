#!/usr/bin/env python3
"""
Fix the two main errors:
1. question_type not defined in ticket_storage_system.py
2. implementation_complexity.title() error in complete_streamlit_app.py
"""

import re

def fix_question_type_error():
    """Fix the question_type error in ticket_storage_system.py"""
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the question storage loop - question_type should be question[1]
    pattern = r"(for question in questions:\n\s+cursor\.execute\('''\n\s+INSERT INTO questions \(ticket_id, question_text, question_type\)\n\s+VALUES \(\?, \?, \?\)\n\s+''', \(ticket_id, question, question_type\)\))"
    
    replacement = r"for question, question_type in questions:\n            cursor.execute('''\n                INSERT INTO questions (ticket_id, question_text, question_type)\n                VALUES (?, ?, ?)\n            ''', (ticket_id, question, question_type))"
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed question_type error in ticket_storage_system.py")

def fix_implementation_complexity_error():
    """Fix the implementation_complexity.title() error in complete_streamlit_app.py"""
    file_path = 'complete_streamlit_app.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the implementation_complexity display
    pattern = r'st\.metric\("Implementation Complexity", visual_analysis\.implementation_complexity\.title\(\)\)'
    
    replacement = r'st.metric("Implementation Complexity", str(visual_analysis.implementation_complexity.get("level", "Unknown")).title())'
    
    content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed implementation_complexity.title() error in complete_streamlit_app.py")

if __name__ == "__main__":
    fix_question_type_error()
    fix_implementation_complexity_error()
    print("🎉 All errors fixed!")
