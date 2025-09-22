#!/usr/bin/env python3
"""
Add database migration to handle existing databases with old schema
"""

import re

def add_database_migration():
    file_path = 'ticket_storage_system.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add migration logic after table creation
    migration_code = '''
        # Migrate existing databases to new schema
        try:
            # Check if old columns exist and add new ones if needed
            cursor.execute("PRAGMA table_info(questions)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'question_text' not in columns:
                cursor.execute('ALTER TABLE questions ADD COLUMN question_text TEXT')
                print("✅ Added question_text column to questions table")
            
            if 'question_type' not in columns:
                cursor.execute('ALTER TABLE questions ADD COLUMN question_type TEXT')
                print("✅ Added question_type column to questions table")
            
            if 'question' in columns and 'question_text' in columns:
                # Migrate data from question to question_text
                cursor.execute('UPDATE questions SET question_text = question WHERE question_text IS NULL')
                print("✅ Migrated question data to question_text")
            
            # Check test_cases table
            cursor.execute("PRAGMA table_info(test_cases)")
            test_columns = [column[1] for column in cursor.fetchall()]
            
            if 'test_case_text' not in test_columns:
                cursor.execute('ALTER TABLE test_cases ADD COLUMN test_case_text TEXT')
                print("✅ Added test_case_text column to test_cases table")
            
            if 'test_case' in test_columns and 'test_case_text' in test_columns:
                # Migrate data from test_case to test_case_text
                cursor.execute('UPDATE test_cases SET test_case_text = test_case WHERE test_case_text IS NULL')
                print("✅ Migrated test_case data to test_case_text")
                
        except Exception as e:
            print(f"⚠️ Migration warning: {e}")
            # Continue anyway, tables will be created with correct schema'''
    
    # Find the end of table creation and add migration
    pattern = r"(        conn\.commit\(\)\n        conn\.close\(\)\n    )"
    
    replacement = f"{migration_code}\n        \n        conn.commit()\n        conn.close()\n    "
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Added database migration logic to ticket_storage_system.py")

if __name__ == "__main__":
    add_database_migration()
