#!/usr/bin/env python3
"""
Add delete method to ticket storage system
"""

def add_delete_method():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Add delete method before the last closing of the class
    delete_method = '''
    def delete_ticket(self, ticket_id: str) -> bool:
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
            return False
    
    def delete_all_tickets(self) -> bool:
        """Delete all tickets and associated data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete all data
            cursor.execute('DELETE FROM questions')
            cursor.execute('DELETE FROM test_cases')
            cursor.execute('DELETE FROM tickets')
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error deleting all tickets: {e}")
            return False'''
    
    # Insert before the last method or at the end of the class
    if 'def get_priority_distribution(self) -> List[Dict[str, Any]]:' in content:
        # Insert before the last method
        content = content.replace(
            'def get_priority_distribution(self) -> List[Dict[str, Any]]:',
            delete_method + '\n    def get_priority_distribution(self) -> List[Dict[str, Any]]:'
        )
    else:
        # Add at the end of the class
        content = content.rstrip() + delete_method + '\n'
    
    # Write the updated content
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Added delete methods to ticket storage system")

if __name__ == "__main__":
    add_delete_method()
