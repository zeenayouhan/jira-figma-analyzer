#!/usr/bin/env python3
"""
Fix delete_ticket method with correct column names
"""

def fix_delete_ticket_correct():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Replace the delete_ticket method with the correct version
    old_delete_method = '''    def delete_ticket(self, ticket_id: str) -> bool:
        """Delete a ticket and all its associated data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete from questions table using ticket_id (foreign key)
            cursor.execute('DELETE FROM questions WHERE ticket_id = ?', (ticket_id,))
            
            # Delete from test_cases table using ticket_id (foreign key)
            cursor.execute('DELETE FROM test_cases WHERE ticket_id = ?', (ticket_id,))
            
            # Delete from tickets table using ticket_id (text field)
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
            
            # Delete from questions table using ticket_id (foreign key)
            cursor.execute('DELETE FROM questions WHERE ticket_id = ?', (ticket_id,))
            
            # Delete from test_cases table using ticket_id (foreign key)
            cursor.execute('DELETE FROM test_cases WHERE ticket_id = ?', (ticket_id,))
            
            # Delete from tickets table using ticket_key (correct column name)
            cursor.execute('DELETE FROM tickets WHERE ticket_key = ?', (ticket_id,))
            
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
    
    print("✅ Fixed delete_ticket method with correct column names")

if __name__ == "__main__":
    fix_delete_ticket_correct()
