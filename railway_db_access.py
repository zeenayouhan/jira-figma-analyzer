#!/usr/bin/env python3
"""
Railway Production Database Access
This script can be run on Railway to access the database
"""

import os
import sqlite3
import json
from datetime import datetime

def railway_db_access():
    """Access database on Railway production"""
    
    print("🚀 Railway Production Database Access")
    print("=" * 50)
    
    # Database paths
    db_paths = {
        'tickets': 'storage/tickets.db',
        'feedback': 'feedback_storage/feedback.db',
        'confluence': 'confluence_knowledge/database/confluence_docs.db'
    }
    
    # Check which databases exist
    print("📊 Database Status:")
    for name, path in db_paths.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name}: {path} ({size:,} bytes)")
        else:
            print(f"❌ {name}: {path} (not found)")
    
    # Access tickets database
    tickets_db = db_paths['tickets']
    if os.path.exists(tickets_db):
        print(f"\n🎫 Tickets Database Analysis:")
        print("-" * 30)
        
        conn = sqlite3.connect(tickets_db)
        cursor = conn.cursor()
        
        # Show tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tables:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")
        
        # Show sample data
        cursor.execute("SELECT id, ticket_key, title, created_at FROM tickets LIMIT 5")
        tickets = cursor.fetchall()
        
        if tickets:
            print("\nSample Tickets:")
            for ticket in tickets:
                print(f"  ID: {ticket[0]}, Key: {ticket[1]}, Title: {ticket[2]}, Created: {ticket[3]}")
        else:
            print("No tickets found")
        
        conn.close()
    
    # Export data
    print(f"\n📤 Exporting data...")
    export_data = {}
    
    for name, path in db_paths.items():
        if os.path.exists(path):
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            db_data = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Convert to list of dictionaries
                table_data = []
                for row in rows:
                    table_data.append(dict(zip(columns, row)))
                
                db_data[table_name] = table_data
            
            export_data[name] = db_data
            conn.close()
    
    # Save export
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"railway_db_export_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"✅ Data exported to {filename}")
    print(f"📁 File size: {os.path.getsize(filename):,} bytes")

if __name__ == "__main__":
    railway_db_access()
