#!/usr/bin/env python3
"""
Fix database schema issues
"""

import sqlite3
import os

def fix_database_schema():
    print("🔧 Fixing database schema...")
    
    # Database paths to check
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
            
            # Check if questions table exists and has correct schema
            cursor.execute("PRAGMA table_info(questions)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'question' not in columns:
                print("Adding missing 'question' column to questions table")
                cursor.execute('ALTER TABLE questions ADD COLUMN question TEXT')
            
            if 'question_text' not in columns:
                print("Adding missing 'question_text' column to questions table")
                cursor.execute('ALTER TABLE questions ADD COLUMN question_text TEXT')
            
            # Check test_cases table
            cursor.execute("PRAGMA table_info(test_cases)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'test_case' not in columns:
                print("Adding missing 'test_case' column to test_cases table")
                cursor.execute('ALTER TABLE test_cases ADD COLUMN test_case TEXT')
            
            if 'test_case_text' not in columns:
                print("Adding missing 'test_case_text' column to test_cases table")
                cursor.execute('ALTER TABLE test_cases ADD COLUMN test_case_text TEXT')
            
            conn.commit()
            conn.close()
            print(f"✅ Fixed database: {db_path}")
    
    print("✅ Database schema fixes complete!")

if __name__ == "__main__":
    fix_database_schema()
