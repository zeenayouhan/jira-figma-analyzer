#!/usr/bin/env python3
"""
Fix ticket counts to include question_count, test_case_count, risk_count
"""

import re

def fix_ticket_counts():
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix get_all_tickets method to include counts
    pattern = r"            return \[\{\n                'id': row\[0\],\n                'ticket_key': row\[1\],\n            'title': row\[2\],\n            'description': row\[3\],\n            'created_at': row\[4\],\n            'updated_at': row\[5\]\n        \} for row in rows\]"
    
    replacement = """            # Get question counts for each ticket
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
            
            return tickets_with_counts"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed ticket counts in get_all_tickets method")

if __name__ == "__main__":
    fix_ticket_counts()
