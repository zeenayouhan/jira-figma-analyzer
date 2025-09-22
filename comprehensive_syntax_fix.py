#!/usr/bin/env python3
"""
Comprehensive syntax fix for jira_figma_analyzer.py
"""

import re

def comprehensive_syntax_fix():
    file_path = 'jira_figma_analyzer.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the missing indented block after if statement around line 1001
    pattern1 = r'            try:\n                if self\.openai_client and design_context\.strip\(\):\n                response = self\.openai_client\.chat\.completions\.create\('
    
    replacement1 = '''            try:
                if self.openai_client and design_context.strip():
                    response = self.openai_client.chat.completions.create('''
    
    content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
    
    # Fix any other similar indentation issues
    # Look for lines that should be indented but aren't
    lines = content.split('\n')
    fixed_lines = []
    in_try_block = False
    in_if_block = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        # Track if we're in a try block
        if 'try:' in line and not line.strip().startswith('#'):
            in_try_block = True
            indent_level = len(line) - len(line.lstrip())
        elif 'except' in line and not line.strip().startswith('#'):
            in_try_block = False
            indent_level = len(line) - len(line.lstrip())
        elif 'if ' in line and ':' in line and not line.strip().startswith('#'):
            in_if_block = True
            indent_level = len(line) - len(line.lstrip())
        elif line.strip() and not line.startswith(' ') and not line.strip().startswith('#'):
            in_if_block = False
            in_try_block = False
        
        # Fix specific problematic lines
        if i > 0 and lines[i-1].strip().endswith(':') and not line.strip().startswith('#') and line.strip():
            # This line should be indented
            if not line.startswith(' '):
                line = '    ' * (indent_level // 4 + 1) + line.strip()
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Applied comprehensive syntax fix to jira_figma_analyzer.py")

if __name__ == "__main__":
    comprehensive_syntax_fix()
