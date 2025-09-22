#!/usr/bin/env python3
"""
Database Access Tool for Jira-Figma Analyzer
Provides multiple ways to access and manage the databases
"""

import sqlite3
import json
import os
from pathlib import Path

class DatabaseAccess:
    def __init__(self):
        self.db_paths = {
            'tickets': 'storage/tickets.db',
            'feedback': 'feedback_storage/feedback.db',
            'confluence': 'confluence_knowledge/database/confluence_docs.db'
        }
    
    def list_databases(self):
        """List all available databases"""
        print("📊 Available Databases:")
        print("=" * 40)
        
        for name, path in self.db_paths.items():
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"✅ {name}: {path} ({size:,} bytes)")
            else:
                print(f"❌ {name}: {path} (not found)")
    
    def show_tables(self, db_name):
        """Show all tables in a database"""
        if db_name not in self.db_paths:
            print(f"❌ Unknown database: {db_name}")
            return
        
        db_path = self.db_paths[db_name]
        if not os.path.exists(db_path):
            print(f"❌ Database not found: {db_path}")
            return
        
        print(f"📋 Tables in {db_name} database:")
        print("=" * 40)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"📄 {table_name}: {count} rows")
        
        conn.close()
    
    def query_database(self, db_name, query):
        """Execute a custom SQL query"""
        if db_name not in self.db_paths:
            print(f"❌ Unknown database: {db_name}")
            return
        
        db_path = self.db_paths[db_name]
        if not os.path.exists(db_path):
            print(f"❌ Database not found: {db_path}")
            return
        
        print(f"🔍 Executing query on {db_name}:")
        print(f"Query: {query}")
        print("=" * 40)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results:
                # Get column names
                columns = [description[0] for description in cursor.description]
                print(f"Columns: {', '.join(columns)}")
                print("-" * 40)
                
                for i, row in enumerate(results[:10]):  # Show first 10 rows
                    print(f"Row {i+1}: {row}")
                
                if len(results) > 10:
                    print(f"... and {len(results) - 10} more rows")
            else:
                print("No results found")
                
        except Exception as e:
            print(f"❌ Error executing query: {e}")
        finally:
            conn.close()
    
    def show_ticket_data(self):
        """Show all ticket data in a formatted way"""
        db_path = self.db_paths['tickets']
        if not os.path.exists(db_path):
            print("❌ Tickets database not found. Run the app first to create it.")
            return
        
        print("🎫 Ticket Data:")
        print("=" * 50)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tickets
        cursor.execute("SELECT * FROM tickets")
        tickets = cursor.fetchall()
        
        if not tickets:
            print("No tickets found")
            conn.close()
            return
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        print(f"Columns: {', '.join(columns)}")
        print("-" * 50)
        
        for ticket in tickets:
            print(f"Ticket ID: {ticket[0]}")
            print(f"Key: {ticket[1]}")
            print(f"Title: {ticket[2]}")
            print(f"Description: {ticket[3][:100]}..." if len(ticket[3]) > 100 else f"Description: {ticket[3]}")
            print(f"Created: {ticket[4]}")
            print("-" * 30)
        
        conn.close()
    
    def export_data(self, db_name, format='json'):
        """Export database data to JSON or CSV"""
        if db_name not in self.db_paths:
            print(f"❌ Unknown database: {db_name}")
            return
        
        db_path = self.db_paths[db_name]
        if not os.path.exists(db_path):
            print(f"❌ Database not found: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        export_data = {}
        
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
            
            export_data[table_name] = table_data
        
        conn.close()
        
        # Save to file
        filename = f"{db_name}_export.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Data exported to {filename}")
    
    def interactive_mode(self):
        """Interactive database browser"""
        print("🔧 Interactive Database Browser")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("1. List databases")
            print("2. Show tables")
            print("3. Query database")
            print("4. Show ticket data")
            print("5. Export data")
            print("6. Exit")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                self.list_databases()
            elif choice == '2':
                db_name = input("Enter database name (tickets/feedback/confluence): ").strip()
                self.show_tables(db_name)
            elif choice == '3':
                db_name = input("Enter database name (tickets/feedback/confluence): ").strip()
                query = input("Enter SQL query: ").strip()
                self.query_database(db_name, query)
            elif choice == '4':
                self.show_ticket_data()
            elif choice == '5':
                db_name = input("Enter database name (tickets/feedback/confluence): ").strip()
                self.export_data(db_name)
            elif choice == '6':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")

def main():
    db_access = DatabaseAccess()
    
    print("🗄️  Jira-Figma Analyzer Database Access Tool")
    print("=" * 50)
    
    # Show current status
    db_access.list_databases()
    
    # Start interactive mode
    db_access.interactive_mode()

if __name__ == "__main__":
    main()
