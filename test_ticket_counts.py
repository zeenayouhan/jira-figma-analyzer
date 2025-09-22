#!/usr/bin/env python3
"""
Test ticket counts to see if questions are showing up
"""

from ticket_storage_system import TicketStorageSystem

def test_ticket_counts():
    print("🧪 Testing ticket counts...")
    
    storage = TicketStorageSystem()
    
    # Get recent tickets
    tickets = storage.get_recent_tickets(limit=5)
    
    print(f"📊 Found {len(tickets)} tickets")
    
    for i, ticket in enumerate(tickets, 1):
        print(f"\n🎫 Ticket {i}:")
        print(f"  - ID: {ticket.get('id', 'Unknown')}")
        print(f"  - Title: {ticket.get('title', 'No title')[:50]}...")
        print(f"  - Questions: {ticket.get('question_count', 0)}")
        print(f"  - Test Cases: {ticket.get('test_case_count', 0)}")
        print(f"  - Risks: {ticket.get('risk_count', 0)}")

if __name__ == "__main__":
    test_ticket_counts()
