#!/usr/bin/env python3
"""
Fix delete_ticket method to handle both id and ticket_id columns
"""

def fix_delete_ticket():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Replace the delete_ticket method with a more robust version
    old_delete_method = '''    def delete_ticket(self, ticket_id: str) -> bool:
        """Delete a ticket and all its associated data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete from questions table
            cursor.execute('DELETE FROM questions WHERE ticket_id = ?', (ticket_id,))
            
            # Delete from test_cases table
            cursor.execute('DELETE FROM test_cases WHERE ticket_id = ?', (ticket_id,))
            
            # Delete from tickets table
            cursor.execute('DELETE FROM tickets WHERE ticket_id = ?', (ticket_id,))
            
            # Check if any rows were affected
            rows_affected = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            print(f"Error deleting ticket {ticket_id}: {e}")
            return False'''
    
    new_delete_method = '''    def delete_ticket(self, ticket_id: str) -> bool:
        """Delete a ticket and all its associated data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First, get the actual ticket ID from the database
            # Try both possible column names
            cursor.execute('SELECT id FROM tickets WHERE ticket_id = ?', (ticket_id,))
            row = cursor.fetchone()
            
            if not row:
                # Try the other way around
                cursor.execute('SELECT ticket_id FROM tickets WHERE id = ?', (ticket_id,))
                row = cursor.fetchone()
                if row:
                    actual_ticket_id = row[0]
                else:
                    print(f"Ticket {ticket_id} not found")
                    return False
            else:
                actual_ticket_id = ticket_id
            
            # Delete from questions table using the actual ticket ID
            cursor.execute('DELETE FROM questions WHERE ticket_id = ?', (actual_ticket_id,))
            
            # Delete from test_cases table using the actual ticket ID
            cursor.execute('DELETE FROM test_cases WHERE ticket_id = ?', (actual_ticket_id,))
            
            # Delete from tickets table using the actual ticket ID
            cursor.execute('DELETE FROM tickets WHERE ticket_id = ?', (actual_ticket_id,))
            
            # Check if any rows were affected
            rows_affected = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            print(f"Error deleting ticket {ticket_id}: {e}")
            return False'''
    
    content = content.replace(old_delete_method, new_delete_method)
    
    # Write the updated content
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed delete_ticket method to handle database schema properly")

if __name__ == "__main__":
    fix_delete_ticket()
