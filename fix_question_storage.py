#!/usr/bin/env python3
"""
Fix question storage to extract questions from analysis data
"""

def fix_question_storage():
    # Read the current file
    with open('ticket_storage_system.py', 'r') as f:
        content = f.read()
    
    # Fix the store_ticket method to extract questions from analysis
    old_question_storage = '''        # Store questions
        questions = ticket_data.get('questions', [])
        for question in questions:
            cursor.execute('''
                INSERT INTO questions (ticket_id, question_text, question_type)
                VALUES (?, ?, ?)
            ''', (ticket_id, question, "general"))'''
    
    new_question_storage = '''        # Store questions from analysis data
        analysis = ticket_data.get('analysis', {})
        questions = []
        
        # Extract questions from different categories
        if 'suggested_questions' in analysis:
            questions.extend([(q, 'suggested') for q in analysis['suggested_questions']])
        if 'design_questions' in analysis:
            questions.extend([(q, 'design') for q in analysis['design_questions']])
        if 'business_questions' in analysis:
            questions.extend([(q, 'business') for q in analysis['business_questions']])
        
        # Also check direct questions field
        direct_questions = ticket_data.get('questions', [])
        questions.extend([(q, 'general') for q in direct_questions])
        
        for question, question_type in questions:
            cursor.execute('''
                INSERT INTO questions (ticket_id, question_text, question_type)
                VALUES (?, ?, ?)
            ''', (ticket_id, question, question_type))'''
    
    content = content.replace(old_question_storage, new_question_storage)
    
    # Write the updated content
    with open('ticket_storage_system.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed question storage to extract from analysis data")

if __name__ == "__main__":
    fix_question_storage()
