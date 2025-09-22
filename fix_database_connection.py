#!/usr/bin/env python3
"""
Fix database connection issue in get_all_tickets
"""

import re

def fix_database_connection():
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the get_all_tickets method to properly handle database connections
    pattern = r"    def get_all_tickets\(self, limit=50\):\n        try:\n            \"\"\"Get all tickets with pagination\.\"\"\"\n            conn = sqlite3\.connect\(self\.db_path\)\n            cursor = conn\.cursor\(\)\n            \n            cursor\.execute\('''\n                SELECT id, ticket_key, title, description, created_at, updated_at\n                FROM tickets \n                ORDER BY created_at DESC \n                LIMIT \?\n            ''', \(limit,\)\)\n            \n            rows = cursor\.fetchall\(\)\n            conn\.close\(\)\n            \n            # Get question counts for each ticket\n            tickets_with_counts = \[\]\n            for row in rows:\n                ticket_id = row\[0\]\n                \n                # Count questions\n                cursor\.execute\('SELECT COUNT\(\*\) FROM questions WHERE ticket_id = \?', \(ticket_id,\)\)\n                question_count = cursor\.fetchone\(\)\[0\]\n                \n                # Count test cases\n                cursor\.execute\('SELECT COUNT\(\*\) FROM test_cases WHERE ticket_id = \?', \(ticket_id,\)\)\n                test_case_count = cursor\.fetchone\(\)\[0\]\n                \n                tickets_with_counts\.append\(\{\n                    'id': row\[0\],\n                    'ticket_key': row\[1\],\n                    'title': row\[2\],\n                    'description': row\[3\],\n                    'created_at': row\[4\],\n                    'updated_at': row\[5\],\n                    'question_count': question_count,\n                    'test_case_count': test_case_count,\n                    'risk_count': 0  # Mock data - would need risks table\n                \}\)\n            \n            return tickets_with_counts\n        except Exception as e:\n            print\(f\"Error in get_all_tickets: \{e\}\"\)\n            return \[\]"
    
    replacement = """    def get_all_tickets(self, limit=50):
        try:
            \"\"\"Get all tickets with pagination.\"\"\"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, ticket_key, title, description, created_at, updated_at
                FROM tickets 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            # Get question counts for each ticket
            tickets_with_counts = []
            for row in rows:
                ticket_id = row[0]
                
                # Count questions
                cursor.execute('SELECT COUNT(*) FROM questions WHERE ticket_id = ?', (ticket_id,))
                question_count = cursor.fetchone()[0]
                
                # Count test cases
                cursor.execute('SELECT COUNT(*) FROM test_cases WHERE ticket_id = ?', (ticket_id,))
                test_case_count = cursor.fetchone()[0]
                
                tickets_with_counts.append({
                    'id': row[0],
                    'ticket_key': row[1],
                    'title': row[2],
                    'description': row[3],
                    'created_at': row[4],
                    'updated_at': row[5],
                    'question_count': question_count,
                    'test_case_count': test_case_count,
                    'risk_count': 0  # Mock data - would need risks table
                })
            
            conn.close()
            return tickets_with_counts
        except Exception as e:
            print(f"Error in get_all_tickets: {e}")
            return []"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed database connection in get_all_tickets method")

if __name__ == "__main__":
    fix_database_connection()
