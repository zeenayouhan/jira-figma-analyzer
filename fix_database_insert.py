#!/usr/bin/env python3
"""
Fix the database INSERT statement to use correct column names
"""

import re

def fix_database_insert():
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the INSERT statement - remove ticket_id column from INSERT
    pattern = r"INSERT OR REPLACE INTO tickets \n\s+\(ticket_id, ticket_key, title, description, created_at, updated_at, analysis_data\)\n\s+VALUES \(\?, \?, \?, \?, \?, \?, \?\)\n\s+''', \(\n\s+ticket_id,\n\s+ticket_id,"
    
    replacement = """INSERT OR REPLACE INTO tickets 
            (id, ticket_key, title, description, created_at, updated_at, analysis_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticket_id,
            ticket_id,"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed database INSERT statement in ticket_storage_system.py")

if __name__ == "__main__":
    fix_database_insert()
