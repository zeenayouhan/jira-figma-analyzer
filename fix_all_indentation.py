#!/usr/bin/env python3
"""
Fix all indentation errors in jira_figma_analyzer.py
"""

import re

def fix_all_indentation():
    file_path = 'jira_figma_analyzer.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix multiple indentation issues in the test cases section
    patterns_and_replacements = [
        # Fix the first test_cases.extend block
        (
            r'        content_lower = f"\{ticket\.title\} \{ticket\.description\}"\.lower\(\)\n        \n        test_cases\.extend\(\[\n            "\*\*Functional Tests:\*\*",\n            "• Verify the main feature works as described in acceptance criteria",\n            "• Verify user can complete the primary user journey successfully",\n            "• Verify feature integrates with existing authentication system",\n            "• Verify feature respects user permissions and access controls",\n            "• Verify data validation and business rule enforcement",\n        \]\)\n        \n            test_cases\.extend\(\[\n        "\*\*Security & Compliance Tests:\*\*",\n        "• Verify data encryption in transit and at rest",\n        "• Verify audit logging for financial advisory compliance",\n        "• Verify user session management and timeout handling",\n        \]\)',
            '''        content_lower = f"{ticket.title} {ticket.description}".lower()
        
        test_cases.extend([
            "**Functional Tests:**",
            "• Verify the main feature works as described in acceptance criteria",
            "• Verify user can complete the primary user journey successfully",
            "• Verify feature integrates with existing authentication system",
            "• Verify feature respects user permissions and access controls",
            "• Verify data validation and business rule enforcement",
        ])
        
        test_cases.extend([
            "**Security & Compliance Tests:**",
            "• Verify data encryption in transit and at rest",
            "• Verify audit logging for financial advisory compliance",
            "• Verify user session management and timeout handling",
        ])'''
        ),
        # Fix the performance test_cases.extend block
        (
            r'        # Performance\n        test_cases\.extend\(\[\n        "\*\*Performance Tests:\*\*",',
            '''        # Performance
        test_cases.extend([
            "**Performance Tests:**",'''
        )
    ]
    
    for pattern, replacement in patterns_and_replacements:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed all indentation errors in jira_figma_analyzer.py")

if __name__ == "__main__":
    fix_all_indentation()
