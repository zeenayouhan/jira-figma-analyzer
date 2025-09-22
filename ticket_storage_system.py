#!/usr/bin/env python3
"""
Simple ticket storage system for the Jira-Figma Analyzer.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3
import pickle

class TicketStorageSystem:
    """Simple storage system for tickets and analysis results."""
    
    def __init__(self, storage_dir: str = "ticket_storage"):
        self.storage_dir = storage_dir
        self.db_path = os.path.join(storage_dir, "database", "tickets.db")
        self.index_path = os.path.join(storage_dir, "database", "search_index.pkl")
        
        # Create directories if they don't exist
        os.makedirs(os.path.join(storage_dir, "database"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "files"), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Initialize search index
        self.search_index = self._load_search_index()
    
    def _init_database(self):
        """Initialize SQLite database for ticket storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tickets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                ticket_key TEXT,
                title TEXT,
                description TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                analysis_data TEXT
            )
        ''')
        
        # Create questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT,
                question_text TEXT,
                question_type TEXT,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )
        ''')
        
        # Create test_cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT,
                test_case_text TEXT,
                category TEXT,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )
        ''')
        

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
            # Continue anyway, tables will be created with correct schema
        
        conn.commit()
        conn.close()
    
    def _load_search_index(self) -> Dict:
        """Load search index from pickle file."""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return {}
    
    def _save_search_index(self):
        """Save search index to pickle file."""
        with open(self.index_path, 'wb') as f:
            pickle.dump(self.search_index, f)
    
    def store_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Store a ticket and its analysis data."""
        ticket_id = ticket_data.get('id', f"ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tickets 
            (id, ticket_key, title, description, created_at, updated_at, analysis_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticket_id,
            ticket_id,
            ticket_data.get('title', ''),
            ticket_data.get('description', ''),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            json.dumps(ticket_data.get('analysis', {}))
        ))
        
        # Store questions
        analysis = ticket_data.get("analysis", {})
        questions = []
        
        # Extract questions from different categories
        if "suggested_questions" in analysis:
            questions.extend([(q, "suggested") for q in analysis["suggested_questions"]])
        if "design_questions" in analysis:
            questions.extend([(q, "design") for q in analysis["design_questions"]])
        if "business_questions" in analysis:
            questions.extend([(q, "business") for q in analysis["business_questions"]])
        
        # Also check direct questions field
        direct_questions = ticket_data.get("questions", [])
        questions.extend([(q, "general") for q in direct_questions])
        for question, question_type in questions:
            cursor.execute('''
                INSERT INTO questions (ticket_id, question_text, question_type)
                VALUES (?, ?, ?)
            ''', (ticket_id, question, question_type))
        
        # Store test cases
        test_cases = ticket_data.get('test_cases', [])
        for test_case in test_cases:
            cursor.execute('''
                INSERT INTO test_cases (ticket_id, test_case_text)
                VALUES (?, ?)
            ''', (ticket_id, test_case))
        

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
            # Continue anyway, tables will be created with correct schema
        
        conn.commit()
        conn.close()
        
        # Update search index
        self.search_index[ticket_id] = {
            'title': ticket_data.get('title', ''),
            'description': ticket_data.get('description', ''),
            'ticket_key': ticket_id,
            'created_at': datetime.now().isoformat()
        }
        self._save_search_index()
        
        return ticket_id
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get a ticket by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Get questions
        try:
            cursor.execute('SELECT question_text FROM questions WHERE ticket_id = ?', (ticket_id,))
            questions = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Fallback if question_text column doesn't exist
            try:
                cursor.execute('SELECT question FROM questions WHERE ticket_id = ?', (ticket_id,))
                questions = [row[0] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                questions = []
        
        # Get test cases
        try:
            cursor.execute('SELECT test_case_text FROM test_cases WHERE ticket_id = ?', (ticket_id,))
            test_cases = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Fallback if test_case_text column doesn't exist
            try:
                cursor.execute('SELECT test_case FROM test_cases WHERE ticket_id = ?', (ticket_id,))
                test_cases = [row[0] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                test_cases = []
        
        conn.close()
        
        return {
            'id': row[0],
            'ticket_key': row[1],
            'title': row[2],
            'description': row[3],
            'created_at': row[4],
            'updated_at': row[5],
            'analysis': json.loads(row[6]) if row[6] else {},
            'questions': questions,
            'test_cases': test_cases
        }
    
    def search_tickets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search tickets by query."""
        results = []
        query_lower = query.lower()
        
        for ticket_id, data in self.search_index.items():
            if (query_lower in data['title'].lower() or 
                query_lower in data['description'].lower() or 
                query_lower in data['ticket_key'].lower()):
                results.append({
                    'ticket_id': ticket_id,
                    'ticket_key': data['ticket_key'],
                    'title': data['title'],
                    'created_at': data['created_at']
                })
        
        return results[:limit]
    
    def search_figma_tickets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for tickets with Figma designs."""
        # This is a simplified version - in a real implementation,
        # you'd search for tickets that have Figma links
        return self.search_tickets("figma", limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count tickets
        cursor.execute('SELECT COUNT(*) FROM tickets')
        ticket_count = cursor.fetchone()[0]
        
        # Count questions
        cursor.execute('SELECT COUNT(*) FROM questions')
        question_count = cursor.fetchone()[0]
        
        # Count test cases
        cursor.execute('SELECT COUNT(*) FROM test_cases')
        test_case_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_tickets': ticket_count,
            'total_questions': question_count,
            'total_test_cases': test_case_count,
            'total_risks': 0,  # Mock data - would need risks table
            'total_screens': 0,  # Mock data - would need screens table
            'storage_size': self._get_storage_size()
        }
    
    def _get_storage_size(self) -> int:
        """Get total storage size in bytes."""
        total_size = 0
        for root, dirs, files in os.walk(self.storage_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size
    
    def get_all_tickets(self, limit=50):
        try:
            """Get all tickets with pagination."""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, ticket_key, title, description, created_at, updated_at
                FROM tickets 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'ticket_key': row[1],
            'title': row[2],
            'description': row[3],
            'created_at': row[4],
            'updated_at': row[5]
        } for row in rows]
        except Exception as e:
            print(f"Error in get_all_tickets: {e}")
            return []

    def get_recent_tickets(self, limit=10):
        """Get recent tickets."""
        try:
            return self.get_all_tickets(limit=limit)
        except Exception as e:
            print(f"Error in get_recent_tickets: {e}")
            return []

    def get_tickets_timeline(self) -> List[Dict[str, Any]]:
        """Get tickets timeline data for charts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM tickets 
            GROUP BY DATE(created_at)
            ORDER BY date
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'date': row[0], 'count': row[1]} for row in rows]
    
    
    def delete_ticket(self, ticket_id: str) -> bool:
        """Delete a ticket and all its associated data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete from questions table using ticket_id (foreign key)
            cursor.execute('DELETE FROM questions WHERE ticket_id = ?', (ticket_id,))
            
            # Delete from test_cases table using ticket_id (foreign key)
            cursor.execute('DELETE FROM test_cases WHERE ticket_id = ?', (ticket_id,))
            
            # Delete from tickets table using ticket_key (correct column name)
            cursor.execute('DELETE FROM tickets WHERE ticket_key = ?', (ticket_id,))
            
            # Check if any rows were affected
            rows_affected = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            print(f"Error deleting ticket {ticket_id}: {e}")
            return False
    
    def delete_all_tickets(self) -> bool:
        """Delete all tickets and associated data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete all data
            cursor.execute('DELETE FROM questions')
            cursor.execute('DELETE FROM test_cases')
            cursor.execute('DELETE FROM tickets')
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error deleting all tickets: {e}")
            return False
    
    def get_priority_distribution(self) -> List[Dict[str, Any]]:
        """Get priority distribution data for charts."""
        # Mock data since we don't have priority field yet
        return [
            {'priority': 'High', 'count': 5},
            {'priority': 'Medium', 'count': 12},
            {'priority': 'Low', 'count': 8}
        ]
    
    def get_complexity_distribution(self) -> List[Dict[str, Any]]:
        """Get complexity distribution data for charts."""
        # Mock data since we don't have complexity field yet
        return [
            {'complexity': 'Simple', 'count': 10},
            {'complexity': 'Medium', 'count': 12},
            {'complexity': 'Complex', 'count': 3}
        ]
