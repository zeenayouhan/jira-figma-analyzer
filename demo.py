#!/usr/bin/env python3
"""
Demo script for Jira Figma Analyzer

This script demonstrates the tool's capabilities with various example tickets.
"""

from jira_figma_analyzer import JiraFigmaAnalyzer

def demo_basic_usage():
    """Demonstrate basic usage of the analyzer."""
    print("=" * 60)
    print("🎯 JIRA FIGMA ANALYZER DEMO")
    print("=" * 60)
    
    analyzer = JiraFigmaAnalyzer()
    
    # Example 1: Simple dashboard ticket
    print("\n📋 Example 1: Dashboard Implementation")
    print("-" * 40)
    
    ticket1 = {
        'key': 'DASH-001',
        'summary': 'Implement new user dashboard with responsive design',
        'description': 'Create a new dashboard for users to view their data, charts, and analytics. Should be mobile-friendly and include real-time updates. Figma link: https://www.figma.com/file/abc123/dashboard-design',
        'priority': {'name': 'High'},
        'labels': ['frontend', 'dashboard', 'responsive'],
        'components': [{'name': 'User Interface'}],
        'comments': []
    }
    
    result1 = analyzer.analyze_ticket_content(analyzer.parse_jira_ticket(ticket1))
    
    print(f"Ticket: {result1.ticket.ticket_id} - {result1.ticket.title}")
    print(f"Figma Links: {len(result1.ticket.figma_links)}")
    print(f"Questions Generated: {len(result1.suggested_questions)}")
    print(f"Clarifications Needed: {len(result1.clarifications_needed)}")
    print(f"Risk Areas: {len(result1.risk_areas)}")
    
    # Example 2: Mobile app feature
    print("\n📱 Example 2: Mobile App Feature")
    print("-" * 40)
    
    ticket2 = {
        'key': 'MOBILE-001',
        'summary': 'Add push notification feature to mobile app',
        'description': 'Implement push notifications for user engagement. Should work on both iOS and Android. Include settings for users to manage notification preferences. Figma link: https://www.figma.com/file/def456/notification-ui',
        'priority': {'name': 'Medium'},
        'labels': ['mobile', 'notifications', 'ios', 'android'],
        'components': [{'name': 'Mobile App'}],
        'comments': []
    }
    
    result2 = analyzer.analyze_ticket_content(analyzer.parse_jira_ticket(ticket2))
    
    print(f"Ticket: {result2.ticket.ticket_id} - {result2.ticket.title}")
    print(f"Figma Links: {len(result2.ticket.figma_links)}")
    print(f"Questions Generated: {len(result2.suggested_questions)}")
    print(f"Clarifications Needed: {len(result2.clarifications_needed)}")
    print(f"Risk Areas: {len(result2.risk_areas)}")
    
    # Example 3: API integration
    print("\n🔌 Example 3: API Integration")
    print("-" * 40)
    
    ticket3 = {
        'key': 'API-001',
        'summary': 'Integrate third-party payment API',
        'description': 'Integrate Stripe payment API for processing transactions. Include error handling, webhook support, and security measures. Figma link: https://www.figma.com/file/ghi789/payment-flow',
        'priority': {'name': 'Critical'},
        'labels': ['backend', 'api', 'security', 'payments'],
        'components': [{'name': 'Backend Services'}],
        'comments': []
    }
    
    result3 = analyzer.analyze_ticket_content(analyzer.parse_jira_ticket(ticket3))
    
    print(f"Ticket: {result3.ticket.ticket_id} - {result3.ticket.title}")
    print(f"Figma Links: {len(result3.ticket.figma_links)}")
    print(f"Questions Generated: {len(result3.suggested_questions)}")
    print(f"Clarifications Needed: {len(result3.clarifications_needed)}")
    print(f"Risk Areas: {len(result3.risk_areas)}")
    
    # Example 4: Ticket without Figma links
    print("\n⚠️ Example 4: Ticket Without Figma Links")
    print("-" * 40)
    
    ticket4 = {
        'key': 'BUG-001',
        'summary': 'Fix login page responsive issues',
        'description': 'The login page is not displaying correctly on mobile devices. Need to fix the responsive design issues.',
        'priority': {'name': 'High'},
        'labels': ['bug', 'frontend', 'responsive'],
        'components': [{'name': 'Authentication'}],
        'comments': []
    }
    
    result4 = analyzer.analyze_ticket_content(analyzer.parse_jira_ticket(ticket4))
    
    print(f"Ticket: {result4.ticket.ticket_id} - {result4.ticket.title}")
    print(f"Figma Links: {len(result4.ticket.figma_links)}")
    print(f"Questions Generated: {len(result4.suggested_questions)}")
    print(f"Clarifications Needed: {len(result4.clarifications_needed)}")
    print(f"Risk Areas: {len(result4.risk_areas)}")
    
    # Show detailed analysis for one example
    print("\n" + "=" * 60)
    print("📊 DETAILED ANALYSIS EXAMPLE")
    print("=" * 60)
    print("\nAnalyzing Example 1 (Dashboard Implementation):")
    
    report = analyzer.generate_report(result1)
    print(report)
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETED!")
    print("=" * 60)
    print("\nTo try the tool yourself:")
    print("1. Web Interface: streamlit run streamlit_app.py")
    print("2. CLI: python3 cli.py --interactive")
    print("3. Sample file: python3 cli.py --file examples/sample_ticket.json")

if __name__ == "__main__":
    demo_basic_usage()
