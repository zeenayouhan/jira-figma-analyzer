#!/usr/bin/env python3
"""
Fix ticket storage system SQL error
"""

def fix_ticket_storage():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Find and replace the problematic get_all_tickets method
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
    
    # Replace the method
    content = content.replace(old_method, new_method)
    
    # Also fix get_recent_tickets method
    old_recent = '''    def get_recent_tickets(self, limit=10):
        try:
        """Get recent tickets (same as get_all_tickets but with default limit of 5)."""
        return self.get_all_tickets(limit=limit)
        except Exception as e:
            print(f"Error in get_recent_tickets: {e}")
            return []'''
    
    new_recent = '''    def get_recent_tickets(self, limit=10):
        """Get recent tickets."""
        try:
            return self.get_all_tickets(limit=limit)
        except Exception as e:
            print(f"Error in get_recent_tickets: {e}")
            return []'''
    
    content = content.replace(old_recent, new_recent)
    
    # Write the fixed content
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed ticket storage system")

if __name__ == "__main__":
    fix_ticket_storage()
