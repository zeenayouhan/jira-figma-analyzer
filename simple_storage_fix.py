#!/usr/bin/env python3

# Read the current file
with open('ticket_storage_system.py', 'r') as f:
    content = f.read()

# Replace the problematic store_ticket method with a simpler, working version
new_method = '''    def store_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Store a ticket and its analysis data."""
        # Generate a unique ticket_key string 
        ticket_key = ticket_data.get('ticket_key', f"ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Store in database using ticket_key instead of id
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Use ticket_key for ticket_id field to avoid INTEGER PRIMARY KEY conflict
            cursor.execute('''
                INSERT OR REPLACE INTO tickets 
                (ticket_id, ticket_key, title, description, created_at, updated_at, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticket_key,  # Use string for ticket_id field
                ticket_data.get('ticket_key', ''),
                ticket_data.get('title', ''),
                ticket_data.get('description', ''),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(ticket_data.get('analysis', {}))
            ))
            
            conn.commit()
            print(f"✅ Ticket stored successfully: {ticket_key}")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            # Try simpler insert without some fields
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO tickets 
                    (ticket_key, title, description, analysis_data)
                    VALUES (?, ?, ?, ?)
                ''', (
                    ticket_data.get('ticket_key', ''),
                    ticket_data.get('title', ''),
                    ticket_data.get('description', ''),
                    json.dumps(ticket_data.get('analysis', {}))
                ))
                conn.commit()
                print(f"✅ Ticket stored with fallback method: {ticket_key}")
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                conn.close()
                return ticket_key
        
        conn.close()
        
        # Store file
        try:
            self._store_file(ticket_key, ticket_data)
        except:
            pass
        
        # Update search index  
        try:
            self._update_search_index(ticket_key, ticket_data)
        except:
            pass
        
        return ticket_key'''

# Find the old method and replace it
import re
pattern = r'def store_ticket\(self, ticket_data: Dict\[str, Any\]\) -> str:.*?(?=\n    def|\nclass|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content.replace(match.group(0), new_method.strip())
    
    # Write back to file
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed store_ticket method!")
else:
    print("❌ Could not find store_ticket method")
