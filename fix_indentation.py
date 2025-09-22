#!/usr/bin/env python3
"""
Fix indentation error in jira_figma_analyzer.py around line 857
"""

import re

def fix_indentation():
    file_path = 'jira_figma_analyzer.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the indentation issue around line 857
    # The test_cases.extend should be properly indented
    
    pattern = r'''        content_lower = f"\{ticket\.title\} \{ticket\.description\}"\.lower\(\)\n        \n            test_cases\.extend\(\[\n        "\*\*Functional Tests:\*\*",\n        "• Verify the main feature works as described in acceptance criteria",\n        "• Verify user can complete the primary user journey successfully",\n        "• Verify feature integrates with existing authentication system",\n        "• Verify feature respects user permissions and access controls",\n        "• Verify data validation and business rule enforcement",\n        \]\)'''
    
    replacement = '''        content_lower = f"{ticket.title} {ticket.description}".lower()
        
        test_cases.extend([
            "**Functional Tests:**",
            "• Verify the main feature works as described in acceptance criteria",
            "• Verify user can complete the primary user journey successfully",
            "• Verify feature integrates with existing authentication system",
            "• Verify feature respects user permissions and access controls",
            "• Verify data validation and business rule enforcement",
        ])'''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed indentation error in jira_figma_analyzer.py")

if __name__ == "__main__":
    fix_indentation()
