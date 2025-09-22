#!/usr/bin/env python3
"""
Fix database schema issues for Railway production
"""

import sqlite3
import os

def fix_database_schema():
    """Fix database schema issues"""
    
    # Database paths
    db_paths = [
        'storage/tickets.db',
        'ticket_storage/tickets.db',
        'ticket_storage.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Fixing database: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if questions table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
            if not cursor.fetchone():
                print("Creating questions table...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id TEXT,
                        question TEXT,
                        category TEXT,
                        FOREIGN KEY (ticket_id) REFERENCES tickets (id)
                    )
                ''')
            else:
                # Check if question column exists
                cursor.execute("PRAGMA table_info(questions)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'question' not in columns:
                    print("Adding question column...")
                    cursor.execute('ALTER TABLE questions ADD COLUMN question TEXT')
                
                if 'question_text' not in columns:
                    print("Adding question_text column...")
                    cursor.execute('ALTER TABLE questions ADD COLUMN question_text TEXT')
            
            # Check if test_cases table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_cases'")
            if not cursor.fetchone():
                print("Creating test_cases table...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS test_cases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id TEXT,
                        test_case TEXT,
                        category TEXT,
                        FOREIGN KEY (ticket_id) REFERENCES tickets (id)
                    )
                ''')
            else:
                # Check if test_case column exists
                cursor.execute("PRAGMA table_info(test_cases)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'test_case' not in columns:
                    print("Adding test_case column...")
                    cursor.execute('ALTER TABLE test_cases ADD COLUMN test_case TEXT')
                
                if 'test_case_text' not in columns:
                    print("Adding test_case_text column...")
                    cursor.execute('ALTER TABLE test_cases ADD COLUMN test_case_text TEXT')
            
            # Check if tickets table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
            if not cursor.fetchone():
                print("Creating tickets table...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id TEXT UNIQUE,
                        title TEXT,
                        description TEXT,
                        created_at TEXT,
                        updated_at TEXT,
                        analysis_data TEXT
                    )
                ''')
            
            conn.commit()
            conn.close()
            print(f"✅ Fixed database: {db_path}")
        else:
            print(f"Database not found: {db_path}")

if __name__ == "__main__":
    fix_database_schema()
