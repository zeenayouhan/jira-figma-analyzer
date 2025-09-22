#!/usr/bin/env python3
"""
Fix SQL error in ticket storage system
"""

def fix_sql_error():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Add error handling to get_all_tickets method
    old_line = "        cursor.execute('''"
    new_line = '''        try:
            # Check if tickets table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
            if not cursor.fetchone():
                conn.close()
                return []
            
            cursor.execute(''''''
    
    content = content.replace(old_line, new_line)
    
    # Add exception handling at the end of get_all_tickets
    old_end = "        } for row in rows]"
    new_end = '''        } for row in rows]
        except Exception as e:
            print(f"Error in get_all_tickets: {e}")
            return []'''
    
    content = content.replace(old_end, new_end)
    
    # Write the fixed content
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed SQL error in ticket_storage_system.py")

if __name__ == "__main__":
    fix_sql_error()
