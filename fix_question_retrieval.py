#!/usr/bin/env python3
"""
Fix question retrieval to use correct column names
"""

import re

def fix_question_retrieval():
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the question retrieval in get_ticket method
    pattern = r"        # Get questions\n        try:\n            cursor\.execute\('SELECT question FROM questions WHERE ticket_id = \?', \(ticket_id,\)\)\n            questions = \[row\[0\] for row in cursor\.fetchall\(\)\]\n        except sqlite3\.OperationalError:\n            # Fallback if question column doesn't exist\n            try:\n                cursor\.execute\('SELECT question_text FROM questions WHERE ticket_id = \?', \(ticket_id,\)\)\n                questions = \[row\[0\] for row in cursor\.fetchall\(\)\]\n            except sqlite3\.OperationalError:\n                questions = \[\]"
    
    replacement = """        # Get questions
        try:
            cursor.execute('SELECT question_text FROM questions WHERE ticket_id = ?', (ticket_id,))
            questions = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Fallback if question_text column doesn't exist
            try:
                cursor.execute('SELECT question FROM questions WHERE ticket_id = ?', (ticket_id,))
                questions = [row[0] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                questions = []"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Fix test cases retrieval as well
    test_cases_pattern = r"        # Get test cases\n        try:\n            cursor\.execute\('SELECT test_case FROM test_cases WHERE ticket_id = \?', \(ticket_id,\)\)\n            test_cases = \[row\[0\] for row in cursor\.fetchall\(\)\]\n        except sqlite3\.OperationalError:\n            # Fallback if test_case column doesn't exist\n            try:\n                cursor\.execute\('SELECT test_case_text FROM test_cases WHERE ticket_id = \?', \(ticket_id,\)\)\n                test_cases = \[row\[0\] for row in cursor\.fetchall\(\)\]\n            except sqlite3\.OperationalError:\n                test_cases = \[\]"
    
    test_cases_replacement = """        # Get test cases
        try:
            cursor.execute('SELECT test_case_text FROM test_cases WHERE ticket_id = ?', (ticket_id,))
            test_cases = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Fallback if test_case_text column doesn't exist
            try:
                cursor.execute('SELECT test_case FROM test_cases WHERE ticket_id = ?', (ticket_id,))
                test_cases = [row[0] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                test_cases = []"""
    
    content = re.sub(test_cases_pattern, test_cases_replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed question and test case retrieval in ticket_storage_system.py")

if __name__ == "__main__":
    fix_question_retrieval()
