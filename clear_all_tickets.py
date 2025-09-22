#!/usr/bin/env python3
"""
Clear all stored tickets from the database
"""

import os
import sqlite3
from ticket_storage_system import TicketStorageSystem

def clear_all_tickets():
    print("🗑️ Clearing all stored tickets...")
    
    # Initialize storage system
    storage = TicketStorageSystem()
    
    try:
        # Get current count
        conn = sqlite3.connect(storage.db_path)
        cursor = conn.cursor()
        
        # Count tickets before deletion
        cursor.execute('SELECT COUNT(*) FROM tickets')
        ticket_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM questions')
        question_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM test_cases')
        test_case_count = cursor.fetchone()[0]
        
        print(f"📊 Current data:")
        print(f"  - Tickets: {ticket_count}")
        print(f"  - Questions: {question_count}")
        print(f"  - Test Cases: {test_case_count}")
        
        if ticket_count == 0:
            print("✅ No tickets to delete")
            return
        
        # Delete all data
        print("🗑️ Deleting all data...")
        cursor.execute('DELETE FROM questions')
        cursor.execute('DELETE FROM test_cases')
        cursor.execute('DELETE FROM tickets')
        
        # Reset auto-increment counters
        cursor.execute('DELETE FROM sqlite_sequence WHERE name IN ("questions", "test_cases", "tickets")')
        
        conn.commit()
        conn.close()
        
        # Clear search index
        storage.search_index = {}
        storage._save_search_index()
        
        print("✅ All tickets, questions, and test cases deleted successfully!")
        print("✅ Search index cleared!")
        
        # Verify deletion
        conn = sqlite3.connect(storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tickets')
        remaining_tickets = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM questions')
        remaining_questions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM test_cases')
        remaining_test_cases = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Verification:")
        print(f"  - Remaining Tickets: {remaining_tickets}")
        print(f"  - Remaining Questions: {remaining_questions}")
        print(f"  - Remaining Test Cases: {remaining_test_cases}")
        
        if remaining_tickets == 0 and remaining_questions == 0 and remaining_test_cases == 0:
            print("🎉 Database completely cleared!")
        else:
            print("⚠️ Some data may still remain")
            
    except Exception as e:
        print(f"❌ Error clearing tickets: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clear_all_tickets()
