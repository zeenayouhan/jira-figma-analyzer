#!/usr/bin/env python3
"""
Quick Database Access - Simple commands to access the database
"""

import sqlite3
import os

def quick_access():
    """Quick access to the main tickets database"""
    
    # Check if database exists
    db_path = 'storage/tickets.db'
    if not os.path.exists(db_path):
        print("❌ Tickets database not found. Run the app first to create it.")
        return
    
    print("🎫 Quick Database Access")
    print("=" * 30)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Show all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📋 Available tables:")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} rows")
    
    print("\n🔍 Sample data from tickets table:")
    cursor.execute("SELECT id, ticket_key, title, created_at FROM tickets LIMIT 5")
    tickets = cursor.fetchall()
    
    if tickets:
        for ticket in tickets:
            print(f"  ID: {ticket[0]}, Key: {ticket[1]}, Title: {ticket[2]}, Created: {ticket[3]}")
    else:
        print("  No tickets found")
    
    conn.close()

if __name__ == "__main__":
    quick_access()
