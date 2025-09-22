#!/usr/bin/env python3
"""
Fix get_all_tickets method to use correct column names
"""

def fix_get_all_tickets():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Fix the get_all_tickets method
    old_method = '''    def get_all_tickets(self, limit=50):
        try:
            """Get all tickets with pagination."""
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
    
    new_method = '''    def get_all_tickets(self, limit=50):
        """Get all tickets with pagination."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, ticket_key, title, description, created_at, updated_at
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
    
    content = content.replace(old_method, new_method)
    
    # Write the updated content
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed get_all_tickets method with correct column names")

if __name__ == "__main__":
    fix_get_all_tickets()
