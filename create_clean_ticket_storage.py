#!/usr/bin/env python3
"""
Create a clean ticket_storage_system.py file
"""

def create_clean_file():
    # Read the original backup
    with open('ticket_storage_system_backup.py', 'r') as f:
        content = f.read()
    
    # Find the problematic methods and replace them
    import re
    
    # Replace get_all_tickets method
    old_get_all = r'def get_all_tickets\(self, limit: int = 100\) -> List\[Dict\[str, Any\]\]:.*?return \[{.*?} for row in rows\]'
    new_get_all = '''def get_all_tickets(self, limit=50):
        """Get all tickets with pagination."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, ticket_id, title, description, created_at, updated_at
                FROM tickets 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'ticket_key': row[1],
                'title': row[2],
                'description': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            } for row in rows]
        except Exception as e:
            print(f"Error in get_all_tickets: {e}")
            return []'''
    
    content = re.sub(old_get_all, new_get_all, content, flags=re.DOTALL)
    
    # Replace get_recent_tickets method
    old_get_recent = r'def get_recent_tickets\(self, limit: int = 5\) -> List\[Dict\[str, Any\]\]:.*?return self\.get_all_tickets\(limit=limit\)'
    new_get_recent = '''def get_recent_tickets(self, limit=10):
        """Get recent tickets."""
        try:
            return self.get_all_tickets(limit=limit)
        except Exception as e:
            print(f"Error in get_recent_tickets: {e}")
            return []'''
    
    content = re.sub(old_get_recent, new_get_recent, content, flags=re.DOTALL)
    
    # Write the clean file
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Created clean ticket_storage_system.py")

if __name__ == "__main__":
    create_clean_file()
