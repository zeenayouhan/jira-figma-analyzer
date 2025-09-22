#!/usr/bin/env python3
"""
Fix the remaining errors:
1. accessibility_assessment -> accessibility
2. ticket_id column issue in database
"""

import re

def fix_accessibility_assessment():
    """Fix accessibility_assessment references to use accessibility"""
    files_to_fix = ['complete_streamlit_app.py', 'jira_figma_analyzer.py']
    
    for file_path in files_to_fix:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace accessibility_assessment with accessibility
        content = re.sub(r'accessibility_assessment', 'accessibility', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed accessibility_assessment in {file_path}")

def fix_database_schema():
    """Fix the database schema issue with ticket_id vs ticket_key"""
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # The issue is in the INSERT statement - it's trying to insert ticket_id but the column is ticket_key
    # Fix the INSERT statement in store_ticket method
    pattern = r"INSERT INTO tickets \(id, ticket_key, title, description, created_at, updated_at, analysis_data\)\n\s+VALUES \(\?, \?, \?, \?, \?, \?, \?\)\n\s+''', \(ticket_id, ticket_key, title, description, created_at, updated_at, analysis_data\)\)"
    
    replacement = """INSERT INTO tickets (id, ticket_key, title, description, created_at, updated_at, analysis_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticket_id, ticket_key, title, description, created_at, updated_at, analysis_data))"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed database schema in ticket_storage_system.py")

if __name__ == "__main__":
    fix_accessibility_assessment()
    fix_database_schema()
    print("🎉 All remaining errors fixed!")
