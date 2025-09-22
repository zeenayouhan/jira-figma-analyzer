#!/usr/bin/env python3
"""
Test full analysis to see if questions are generated and stored
"""

from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket
from ticket_storage_system import TicketStorageSystem
import json

def test_full_analysis():
    print("🧪 Testing full analysis and storage...")
    
    # Create analyzer
    analyzer = JiraFigmaAnalyzer()
    
    # Create a test ticket
    ticket = JiraTicket(
        ticket_id="TEST-456",
        title="Enable Editing of Occupation, Country of Residence",
        description="Allow users to edit their occupation and country of residence in their profile settings.",
        figma_links=[],
        pdf_design_paths=[],
        media_files=[]
    )
    
    print(f"📝 Analyzing ticket: {ticket.title}")
    
    # Run full analysis
    try:
        result = analyzer.analyze_ticket_content(ticket)
        print(f"✅ Analysis completed")
        print(f"  - Suggested questions: {len(result.suggested_questions)}")
        print(f"  - Design questions: {len(result.design_questions)}")
        print(f"  - Business questions: {len(result.business_questions)}")
        print(f"  - Test cases: {len(result.test_cases)}")
        print(f"  - Risks: {len(result.risk_areas)}")
        
        # Show some sample questions
        if result.design_questions:
            print(f"\n📋 Sample design questions:")
            for i, q in enumerate(result.design_questions[:3], 1):
                print(f"  {i}. {q}")
        
        if result.business_questions:
            print(f"\n💼 Sample business questions:")
            for i, q in enumerate(result.business_questions[:3], 1):
                print(f"  {i}. {q}")
        
        # Test storage
        storage = TicketStorageSystem()
        
        # Convert result to ticket data format
        ticket_data = {
            'id': ticket.ticket_id,
            'title': ticket.title,
            'description': ticket.description,
            'analysis': {
                'suggested_questions': result.suggested_questions,
                'design_questions': result.design_questions,
                'business_questions': result.business_questions,
                'test_cases': result.test_cases,
                'risk_areas': result.risk_areas
            }
        }
        
        # Store the ticket
        stored_id = storage.store_ticket(ticket_data)
        print(f"✅ Ticket stored with ID: {stored_id}")
        
        # Retrieve the ticket
        retrieved = storage.get_ticket(stored_id)
        if retrieved:
            print(f"✅ Ticket retrieved successfully")
            print(f"  - Stored questions: {len(retrieved.get('questions', []))}")
            print(f"  - Stored test cases: {len(retrieved.get('test_cases', []))}")
            
            if retrieved.get('questions'):
                print(f"\n📋 Retrieved questions:")
                for i, q in enumerate(retrieved['questions'][:3], 1):
                    print(f"  {i}. {q}")
        else:
            print("❌ Failed to retrieve ticket")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_analysis()
