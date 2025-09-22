#!/usr/bin/env python3
"""
Fix method spacing in ticket_storage_system.py
"""

def fix_method_spacing():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Fix the missing newline between methods
    old_content = '''        except Exception as e:
            print(f"Error deleting all tickets: {e}")
            return False
    def get_priority_distribution(self) -> List[Dict[str, Any]]:'''
    
    new_content = '''        except Exception as e:
            print(f"Error deleting all tickets: {e}")
            return False
    
    def get_priority_distribution(self) -> List[Dict[str, Any]]:'''
    
    content = content.replace(old_content, new_content)
    
    # Write the updated content
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed method spacing in ticket_storage_system.py")

if __name__ == "__main__":
    fix_method_spacing()
