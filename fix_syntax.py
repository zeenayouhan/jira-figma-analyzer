#!/usr/bin/env python3
"""
Fix syntax errors in jira_figma_analyzer.py
"""

import re

def fix_syntax_errors():
    with open('jira_figma_analyzer.py', 'r') as f:
        content = f.read()
    
    # Fix common indentation issues
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix lines that have too much indentation after certain patterns
        if i > 0 and lines[i-1].strip().endswith(':'):
            # If previous line ends with colon, current line should be indented
            if line.strip() and not line.startswith('        ') and not line.startswith('    '):
                if line.strip().startswith('test_cases.extend') or line.strip().startswith('questions.extend'):
                    line = '        ' + line.strip()
        
        # Fix specific patterns
        if 'test_cases.extend([' in line and not line.startswith('        '):
            line = '        ' + line.strip()
        elif 'questions.extend([' in line and not line.startswith('        '):
            line = '        ' + line.strip()
        elif line.strip().startswith('"**') and not line.startswith('        '):
            line = '        ' + line.strip()
        elif line.strip().startswith('"•') and not line.startswith('        '):
            line = '        ' + line.strip()
        
        fixed_lines.append(line)
    
    # Write back the fixed content
    with open('jira_figma_analyzer.py', 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Syntax errors fixed!")

if __name__ == "__main__":
    fix_syntax_errors()
