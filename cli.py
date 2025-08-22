#!/usr/bin/env python3
"""
Command Line Interface for Jira Figma Analyzer

A CLI tool to analyze Jira tickets with Figma links and get suggestions
for questions and clarifications.
"""

import argparse
import json
import sys
from pathlib import Path
from jira_figma_analyzer import JiraFigmaAnalyzer

def main():
    parser = argparse.ArgumentParser(
        description="Analyze Jira tickets with Figma links and suggest questions for clients",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a ticket from JSON file
  python cli.py --file ticket.json

  # Analyze a ticket with inline JSON
  python cli.py --json '{"key": "PROJ-123", "summary": "Dashboard", "description": "..."}'

  # Interactive mode
  python cli.py --interactive

  # Output to file
  python cli.py --file ticket.json --output report.md
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Path to JSON file containing ticket data'
    )
    
    parser.add_argument(
        '--json', '-j',
        type=str,
        help='Inline JSON string containing ticket data'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path for the analysis report'
    )
    
    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'text'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = JiraFigmaAnalyzer()
    
    # Get ticket data
    ticket_data = None
    
    if args.file:
        ticket_data = load_from_file(args.file)
    elif args.json:
        ticket_data = load_from_json(args.json)
    elif args.interactive:
        ticket_data = interactive_input()
    else:
        parser.print_help()
        sys.exit(1)
    
    if not ticket_data:
        print("Error: No valid ticket data provided.")
        sys.exit(1)
    
    # Analyze ticket
    try:
        ticket = analyzer.parse_jira_ticket(ticket_data)
        result = analyzer.analyze_ticket_content(ticket)
        
        # Generate output
        output = generate_output(result, analyzer, args.format)
        
        # Display or save output
        if args.output:
            save_output(output, args.output)
            if args.verbose:
                print(f"Analysis report saved to: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def load_from_file(file_path):
    """Load ticket data from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{file_path}': {e}")
        return None

def load_from_json(json_string):
    """Load ticket data from JSON string."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON string: {e}")
        return None

def interactive_input():
    """Get ticket data interactively."""
    print("=== Jira Ticket Interactive Input ===\n")
    
    ticket_data = {}
    
    # Basic fields
    ticket_data['key'] = input("Ticket ID (e.g., PROJ-123): ").strip() or 'TICKET-001'
    ticket_data['summary'] = input("Title: ").strip()
    ticket_data['description'] = input("Description: ").strip()
    
    # Priority
    priority = input("Priority (Low/Medium/High/Critical): ").strip()
    if priority:
        ticket_data['priority'] = {'name': priority}
    
    # Assignee and reporter
    assignee = input("Assignee: ").strip()
    if assignee:
        ticket_data['assignee'] = {'displayName': assignee}
    
    reporter = input("Reporter: ").strip()
    if reporter:
        ticket_data['reporter'] = {'displayName': reporter}
    
    # Labels
    labels_input = input("Labels (comma-separated): ").strip()
    if labels_input:
        ticket_data['labels'] = [label.strip() for label in labels_input.split(',')]
    else:
        ticket_data['labels'] = []
    
    # Components
    components_input = input("Components (comma-separated): ").strip()
    if components_input:
        ticket_data['components'] = [{'name': comp.strip()} for comp in components_input.split(',')]
    else:
        ticket_data['components'] = []
    
    # Figma links
    print("\nEnter Figma links (one per line, press Enter twice to finish):")
    figma_links = []
    while True:
        link = input().strip()
        if not link:
            break
        figma_links.append(link)
    
    if figma_links:
        ticket_data['description'] += "\n\nFigma Links:\n" + "\n".join(figma_links)
    
    ticket_data['comments'] = []
    
    return ticket_data

def generate_output(result, analyzer, format_type):
    """Generate output in the specified format."""
    if format_type == 'markdown':
        return analyzer.generate_report(result)
    elif format_type == 'json':
        return json.dumps({
            'ticket': {
                'id': result.ticket.ticket_id,
                'title': result.ticket.title,
                'priority': result.ticket.priority,
                'figma_links': result.ticket.figma_links
            },
            'suggested_questions': result.suggested_questions,
            'clarifications_needed': result.clarifications_needed,
            'technical_considerations': result.technical_considerations,
            'design_questions': result.design_questions,
            'business_questions': result.business_questions,
            'risk_areas': result.risk_areas
        }, indent=2)
    else:  # text
        return generate_text_output(result)

def generate_text_output(result):
    """Generate plain text output."""
    output = []
    output.append("JIRA TICKET ANALYSIS REPORT")
    output.append("=" * 50)
    output.append(f"Ticket ID: {result.ticket.ticket_id}")
    output.append(f"Title: {result.ticket.title}")
    output.append(f"Priority: {result.ticket.priority or 'Not specified'}")
    output.append(f"Figma Links: {len(result.ticket.figma_links)} found")
    output.append("")
    
    output.append("SUGGESTED QUESTIONS FOR CLIENT")
    output.append("-" * 30)
    for i, question in enumerate(result.suggested_questions, 1):
        output.append(f"{i}. {question}")
    output.append("")
    
    output.append("DESIGN QUESTIONS")
    output.append("-" * 20)
    for i, question in enumerate(result.design_questions, 1):
        output.append(f"{i}. {question}")
    output.append("")
    
    output.append("BUSINESS QUESTIONS")
    output.append("-" * 20)
    for i, question in enumerate(result.business_questions, 1):
        output.append(f"{i}. {question}")
    output.append("")
    
    output.append("AREAS NEEDING CLARIFICATION")
    output.append("-" * 30)
    for i, clarification in enumerate(result.clarifications_needed, 1):
        output.append(f"{i}. {clarification}")
    output.append("")
    
    output.append("TECHNICAL CONSIDERATIONS")
    output.append("-" * 25)
    for i, consideration in enumerate(result.technical_considerations, 1):
        output.append(f"{i}. {consideration}")
    output.append("")
    
    output.append("RISK AREAS")
    output.append("-" * 10)
    for i, risk in enumerate(result.risk_areas, 1):
        output.append(f"{i}. {risk}")
    output.append("")
    
    output.append("FIGMA LINKS FOUND")
    output.append("-" * 20)
    for link in result.ticket.figma_links:
        output.append(f"- {link}")
    
    return "\n".join(output)

def save_output(output, file_path):
    """Save output to file."""
    try:
        with open(file_path, 'w') as f:
            f.write(output)
    except Exception as e:
        print(f"Error saving to file '{file_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
