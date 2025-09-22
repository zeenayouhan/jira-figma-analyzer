#!/usr/bin/env python3
"""
Test question generation to debug why questions are not showing
"""

from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket

def test_question_generation():
    print("🧪 Testing question generation...")
    
    # Create analyzer
    analyzer = JiraFigmaAnalyzer()
    
    # Create a test ticket
    ticket = JiraTicket(
        ticket_id="TEST-123",
        title="Enable Editing of Occupation, Country of Residence",
        description="Allow users to edit their occupation and country of residence in their profile settings.",
        figma_url="",
        pdf_file=None,
        media_files=[]
    )
    
    # Create mock analysis
    analysis = {
        "figma_designs": [],
        "pdf_designs": [],
        "media_analysis": []
    }
    
    print(f"📝 Testing ticket: {ticket.title}")
    
    # Test design questions generation
    try:
        design_questions = analyzer._generate_design_questions(ticket, analysis)
        print(f"✅ Generated {len(design_questions)} design questions:")
        for i, q in enumerate(design_questions, 1):
            print(f"  {i}. {q}")
    except Exception as e:
        print(f"❌ Design questions generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test business questions generation
    try:
        business_questions = analyzer._generate_business_questions(ticket, analysis)
        print(f"✅ Generated {len(business_questions)} business questions:")
        for i, q in enumerate(business_questions, 1):
            print(f"  {i}. {q}")
    except Exception as e:
        print(f"❌ Business questions generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test suggested questions generation
    try:
        suggested_questions = analyzer._generate_suggested_questions(ticket, analysis)
        print(f"✅ Generated {len(suggested_questions)} suggested questions:")
        for i, q in enumerate(suggested_questions, 1):
            print(f"  {i}. {q}")
    except Exception as e:
        print(f"❌ Suggested questions generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_question_generation()
