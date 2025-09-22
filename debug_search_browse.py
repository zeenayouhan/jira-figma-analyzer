#!/usr/bin/env python3
"""
Debug search and browse functionality
"""

from ticket_storage_system import TicketStorageSystem

def debug_search_browse():
    print("🔍 Debugging search and browse functionality...")
    
    storage = TicketStorageSystem()
    
    # Test get_all_tickets
    print("\n📊 Testing get_all_tickets:")
    all_tickets = storage.get_all_tickets(limit=10)
    print(f"Found {len(all_tickets)} tickets")
    
    for i, ticket in enumerate(all_tickets, 1):
        print(f"  {i}. {ticket.get('title', 'No title')[:30]}... - Questions: {ticket.get('question_count', 0)}")
    
    # Test get_recent_tickets
    print("\n📊 Testing get_recent_tickets:")
    recent_tickets = storage.get_recent_tickets(limit=10)
    print(f"Found {len(recent_tickets)} tickets")
    
    for i, ticket in enumerate(recent_tickets, 1):
        print(f"  {i}. {ticket.get('title', 'No title')[:30]}... - Questions: {ticket.get('question_count', 0)}")
    
    # Test search functionality
    print("\n🔍 Testing search functionality:")
    search_results = storage.search_tickets("test", limit=5)
    print(f"Found {len(search_results)} search results")
    
    for i, ticket in enumerate(search_results, 1):
        print(f"  {i}. {ticket.get('title', 'No title')[:30]}... - Questions: {ticket.get('question_count', 0)}")
    
    # Check database directly
    print("\n🗄️ Checking database directly:")
    import sqlite3
    conn = sqlite3.connect(storage.db_path)
    cursor = conn.cursor()
    
    # Check tickets table
    cursor.execute('SELECT COUNT(*) FROM tickets')
    ticket_count = cursor.fetchone()[0]
    print(f"Total tickets in database: {ticket_count}")
    
    # Check questions table
    cursor.execute('SELECT COUNT(*) FROM questions')
    question_count = cursor.fetchone()[0]
    print(f"Total questions in database: {question_count}")
    
    # Check a specific ticket's questions
    cursor.execute('SELECT id, title FROM tickets LIMIT 1')
    sample_ticket = cursor.fetchone()
    if sample_ticket:
        ticket_id = sample_ticket[0]
        cursor.execute('SELECT COUNT(*) FROM questions WHERE ticket_id = ?', (ticket_id,))
        ticket_questions = cursor.fetchone()[0]
        print(f"Sample ticket '{sample_ticket[1][:30]}...' has {ticket_questions} questions")
    
    conn.close()

if __name__ == "__main__":
    debug_search_browse()
