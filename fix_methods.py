#!/usr/bin/env python3
"""
Fix the problematic methods in ticket_storage_system.py
"""

def fix_methods():
    # Read the file
    with open('ticket_storage_system.py', 'r') as f:
        lines = f.readlines()
    
    # Find the get_all_tickets method and replace it
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is the get_all_tickets method
        if 'def get_all_tickets(self, limit: int = 100) -> List[Dict[str, Any]]:' in line:
            # Replace with clean version
            new_lines.append('    def get_all_tickets(self, limit=50):\n')
            new_lines.append('        """Get all tickets with pagination."""\n')
            new_lines.append('        try:\n')
            new_lines.append('            conn = sqlite3.connect(self.db_path)\n')
            new_lines.append('            cursor = conn.cursor()\n')
            new_lines.append('            \n')
            new_lines.append('            cursor.execute(\'\'\'\n')
            new_lines.append('                SELECT id, ticket_id, title, description, created_at, updated_at\n')
            new_lines.append('                FROM tickets \n')
            new_lines.append('                ORDER BY created_at DESC \n')
            new_lines.append('                LIMIT ?\n')
            new_lines.append('            \'\'\', (limit,))\n')
            new_lines.append('            \n')
            new_lines.append('            rows = cursor.fetchall()\n')
            new_lines.append('            conn.close()\n')
            new_lines.append('            \n')
            new_lines.append('            return [{\n')
            new_lines.append('                \'id\': row[0],\n')
            new_lines.append('                \'ticket_key\': row[1],\n')
            new_lines.append('                \'title\': row[2],\n')
            new_lines.append('                \'description\': row[3],\n')
            new_lines.append('                \'created_at\': row[4],\n')
            new_lines.append('                \'updated_at\': row[5]\n')
            new_lines.append('            } for row in rows]\n')
            new_lines.append('        except Exception as e:\n')
            new_lines.append('            print(f"Error in get_all_tickets: {e}")\n')
            new_lines.append('            return []\n')
            new_lines.append('\n')
            
            # Skip the old method lines
            i += 1
            while i < len(lines) and not lines[i].startswith('    def '):
                i += 1
            i -= 1  # Back up one line to process the next method
            
        # Check if this is the get_recent_tickets method
        elif 'def get_recent_tickets(self, limit: int = 5) -> List[Dict[str, Any]]:' in line:
            # Replace with clean version
            new_lines.append('    def get_recent_tickets(self, limit=10):\n')
            new_lines.append('        """Get recent tickets."""\n')
            new_lines.append('        try:\n')
            new_lines.append('            return self.get_all_tickets(limit=limit)\n')
            new_lines.append('        except Exception as e:\n')
            new_lines.append('            print(f"Error in get_recent_tickets: {e}")\n')
            new_lines.append('            return []\n')
            new_lines.append('\n')
            
            # Skip the old method lines
            i += 1
            while i < len(lines) and not lines[i].startswith('    def '):
                i += 1
            i -= 1  # Back up one line to process the next method
            
        else:
            new_lines.append(line)
        
        i += 1
    
    # Write the fixed file
    with open('ticket_storage_system.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Fixed ticket storage methods")

if __name__ == "__main__":
    fix_methods()
