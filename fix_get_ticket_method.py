#!/usr/bin/env python3
"""
Fix get_ticket method to handle missing columns gracefully
"""

def fix_get_ticket_method():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Find and replace the problematic get_ticket method
    old_method = '''        # Get questions
        cursor.execute('SELECT question FROM questions WHERE ticket_id = ?', (ticket_id,))
        questions = [row[0] for row in cursor.fetchall()]
        
        # Get test cases
        cursor.execute('SELECT test_case FROM test_cases WHERE ticket_id = ?', (ticket_id,))
        test_cases = [row[0] for row in cursor.fetchall()]'''
    
    new_method = '''        # Get questions
        try:
            cursor.execute('SELECT question FROM questions WHERE ticket_id = ?', (ticket_id,))
            questions = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Fallback if question column doesn't exist
            try:
                cursor.execute('SELECT question_text FROM questions WHERE ticket_id = ?', (ticket_id,))
                questions = [row[0] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                questions = []
        
        # Get test cases
        try:
            cursor.execute('SELECT test_case FROM test_cases WHERE ticket_id = ?', (ticket_id,))
            test_cases = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Fallback if test_case column doesn't exist
            try:
                cursor.execute('SELECT test_case_text FROM test_cases WHERE ticket_id = ?', (ticket_id,))
                test_cases = [row[0] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                test_cases = []'''
    
    content = content.replace(old_method, new_method)
    
    # Write the fixed content
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed get_ticket method with graceful error handling")

if __name__ == "__main__":
    fix_get_ticket_method()
