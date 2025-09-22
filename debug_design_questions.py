#!/usr/bin/env python3

from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket

# Create a simple test
analyzer = JiraFigmaAnalyzer()

# Create a test ticket
ticket = JiraTicket(
    ticket_id="TEST-123",
    title="Test Design Questions",
    description="Test description for design questions",
    figma_links=["https://www.figma.com/design/fnCxddHpd5tOcjYxzliAxc/Habitto-App-UI--Sprint-Execution?node-id=137944-173127&t=ODpn76sHLlg6eDUQ-0"],
    priority="Medium",
    assignee="Test User",
    reporter="Test Reporter",
    status="To Do",
    labels=["test"],
    components=["UI"],
    pdf_design_paths=[]
)

# Test the analysis
print("Testing design question generation...")
result = analyzer.analyze_ticket_content(ticket)

# Let's manually test the design question generation
print("\nTesting _generate_design_questions directly...")
analysis = {"figma_designs": result.__dict__.get('figma_designs', [])}
print(f"Analysis figma_designs: {analysis.get('figma_designs')}")

# Test the method directly
design_questions = analyzer._generate_design_questions(ticket, analysis)
print(f"Direct design questions count: {len(design_questions)}")
print(f"Direct design questions: {design_questions}")
