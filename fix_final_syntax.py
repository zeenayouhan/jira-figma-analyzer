#!/usr/bin/env python3
"""
Final fix for ticket storage system syntax errors
"""

def fix_final_syntax():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Fix the get_recent_tickets method completely
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
    
    print("✅ Fixed final syntax errors")

if __name__ == "__main__":
    fix_final_syntax()
