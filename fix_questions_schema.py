#!/usr/bin/env python3
"""
Fix the questions table schema to include question_text and question_type columns
"""

import re

def fix_questions_schema():
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the questions table schema
    pattern = r"CREATE TABLE IF NOT EXISTS questions \(\n\s+id INTEGER PRIMARY KEY AUTOINCREMENT,\n\s+ticket_id TEXT,\n\s+question TEXT,\n\s+category TEXT,\n\s+FOREIGN KEY \(ticket_id\) REFERENCES tickets \(id\)\n\s+\)"
    
    replacement = """CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT,
                question_text TEXT,
                question_type TEXT,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Also fix the test_cases table to use test_case_text
    test_cases_pattern = r"CREATE TABLE IF NOT EXISTS test_cases \(\n\s+id INTEGER PRIMARY KEY AUTOINCREMENT,\n\s+ticket_id TEXT,\n\s+test_case TEXT,"
    
    test_cases_replacement = """CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT,
                test_case_text TEXT,"""
    
    content = re.sub(test_cases_pattern, test_cases_replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed questions and test_cases table schemas in ticket_storage_system.py")

if __name__ == "__main__":
    fix_questions_schema()
