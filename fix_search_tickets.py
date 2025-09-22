#!/usr/bin/env python3
"""
Fix search_tickets method to include question counts
"""

import re

def fix_search_tickets():
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the search_tickets method to include question counts
    pattern = r"    def search_tickets\(self, query: str, limit: int = 10\) -> List\[Dict\[str, Any\]\]:\n        \"\"\"Search tickets by query\.\"\"\"\n        results = \[\]\n        query_lower = query\.lower\(\)\n        \n        for ticket_id, data in self\.search_index\.items\(\):\n            if \(query_lower in data\['title'\]\.lower\(\) or \n                query_lower in data\['description'\]\.lower\(\) or \n                query_lower in data\['ticket_key'\]\.lower\(\)\):\n                results\.append\(\{\n                    'ticket_id': ticket_id,\n                    'ticket_key': data\['ticket_key'\],\n                    'title': data\['title'\],\n                    'created_at': data\['created_at'\]\n                \}\)\n        \n        return results\[:limit\]"
    
    replacement = """    def search_tickets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        \"\"\"Search tickets by query.\"\"\"
        results = []
        query_lower = query.lower()
        
        for ticket_id, data in self.search_index.items():
            if (query_lower in data['title'].lower() or 
                query_lower in data['description'].lower() or 
                query_lower in data['ticket_key'].lower()):
                
                # Get question and test case counts for this ticket
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Count questions
                cursor.execute('SELECT COUNT(*) FROM questions WHERE ticket_id = ?', (ticket_id,))
                question_count = cursor.fetchone()[0]
                
                # Count test cases
                cursor.execute('SELECT COUNT(*) FROM test_cases WHERE ticket_id = ?', (ticket_id,))
                test_case_count = cursor.fetchone()[0]
                
                conn.close()
                
                results.append({
                    'id': ticket_id,
                    'ticket_id': ticket_id,
                    'ticket_key': data['ticket_key'],
                    'title': data['title'],
                    'description': data.get('description', ''),
                    'created_at': data['created_at'],
                    'question_count': question_count,
                    'test_case_count': test_case_count,
                    'risk_count': 0  # Mock data - would need risks table
                })
        
        return results[:limit]"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed search_tickets method to include question counts")

if __name__ == "__main__":
    fix_search_tickets()
