#!/usr/bin/env python3
"""
Clean ticket storage methods
"""

def get_all_tickets_method():
    return '''    def get_all_tickets(self, limit=50):
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

def get_recent_tickets_method():
    return '''    def get_recent_tickets(self, limit=10):
        """Get recent tickets."""
        try:
            return self.get_all_tickets(limit=limit)
        except Exception as e:
            print(f"Error in get_recent_tickets: {e}")
            return []'''

if __name__ == "__main__":
    print("Clean methods created")
