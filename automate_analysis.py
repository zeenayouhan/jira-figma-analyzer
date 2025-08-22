#!/usr/bin/env python3
"""
Habitto Jira Figma Analyzer - Automated Analysis Tool
Automatically generates comprehensive suggestions, questions, and test cases for any Jira ticket.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from jira_figma_analyzer import JiraFigmaAnalyzer

class AutomatedAnalyzer:
    def __init__(self):
        self.analyzer = JiraFigmaAnalyzer()
        self.output_dir = Path("analysis_outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze_from_json(self, json_file_path: str) -> dict:
        """Analyze a Jira ticket from JSON file."""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                ticket_data = json.load(f)
            
            # Parse the ticket
            ticket = self.analyzer.parse_jira_ticket(ticket_data)
            
            # Analyze the ticket
            result = self.analyzer.analyze_ticket_content(ticket)
            
            return {
                'ticket': ticket,
                'analysis': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error analyzing {json_file_path}: {e}")
            return None
    
    def analyze_from_text(self, title: str, description: str, figma_links: list = None) -> dict:
        """Analyze a Jira ticket from text input."""
        try:
            # Create ticket data
            ticket_data = {
                "key": "AUTO-GENERATED",
                "summary": title,
                "description": description,
                "priority": {"name": "Medium"},
                "assignee": {"displayName": "Auto Analysis"},
                "reporter": {"displayName": "User"},
                "labels": [],
                "components": [],
                "comments": [],
                "figma_links": figma_links or []
            }
            
            # Parse and analyze
            ticket = self.analyzer.parse_jira_ticket(ticket_data)
            result = self.analyzer.analyze_ticket_content(ticket)
            
            return {
                'ticket': ticket,
                'analysis': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error analyzing text input: {e}")
            return None
    
    def generate_comprehensive_report(self, analysis_data: dict) -> str:
        """Generate a comprehensive report with all suggestions, questions, and test cases."""
        if not analysis_data:
            return "❌ No analysis data available"
        
        ticket = analysis_data['ticket']
        result = analysis_data['analysis']
        
        report = f"""
# 🎯 Habitto Jira Figma Analysis Report

## 📋 Ticket Information
- **ID**: {getattr(ticket, 'key', 'AUTO-GENERATED')}
- **Title**: {getattr(ticket, 'title', 'No title provided')}
- **Priority**: {getattr(ticket, 'priority', {}).get('name', 'Not specified') if isinstance(getattr(ticket, 'priority', {}), dict) else 'Not specified'}
- **Figma Links**: {len(getattr(ticket, 'figma_links', []))} found
- **Analysis Date**: {analysis_data['timestamp']}

## 🔗 Figma Links Found
{chr(10).join(f"- {link}" for link in getattr(ticket, 'figma_links', [])) if getattr(ticket, 'figma_links', []) else "- No Figma links found"}

---

## ❓ Suggested Questions for Client

### 🎯 General Questions
{chr(10).join(f"- {q}" for q in result.suggested_questions[:10])}

### 🎨 Design Questions
{chr(10).join(f"- {q}" for q in result.design_questions[:15])}

### 💼 Business Questions
{chr(10).join(f"- {q}" for q in result.business_questions[:10])}

---

## ⚠️ Areas Needing Clarification
{chr(10).join(f"- {c}" for c in result.clarifications_needed)}

## 🔧 Technical Considerations
{chr(10).join(f"- {tc}" for tc in result.technical_considerations)}

## 🚨 Risk Areas
{chr(10).join(f"- {r}" for r in result.risk_areas)}

---

## 🧪 Comprehensive Test Cases

### 🔧 Core Functionality Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'Core Functionality' in tc or 'main feature' in tc.lower())}

### ⚠️ Error Handling Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'Error Handling' in tc or 'error' in tc.lower())}

### ⚡ Performance Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'Performance' in tc or 'performance' in tc.lower())}

### ♿ Accessibility Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'Accessibility' in tc or 'accessibility' in tc.lower())}

### 📱 Mobile & Cross-platform Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'Mobile' in tc or 'Cross-platform' in tc or 'mobile' in tc.lower())}

### 🔒 Security & Compliance Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'Security' in tc or 'Compliance' in tc or 'security' in tc.lower())}

### 🎨 UI/UX Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'UI/UX' in tc or 'ui' in tc.lower())}

### 🔗 Integration Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'Integration' in tc or 'integration' in tc.lower())}

### 💾 Data Integrity Tests
{chr(10).join(f"- {tc}" for tc in result.test_cases if 'Data Integrity' in tc or 'data' in tc.lower())}

---

## 📊 Analysis Summary
- **Total Questions Generated**: {len(result.suggested_questions) + len(result.design_questions) + len(result.business_questions)}
- **Total Test Cases Generated**: {len(result.test_cases)}
- **Risk Areas Identified**: {len(result.risk_areas)}
- **Technical Considerations**: {len(result.technical_considerations)}

## 🎯 Next Steps
1. Review all generated questions with the client
2. Prioritize test cases based on business impact
3. Address identified risk areas
4. Plan technical implementation based on considerations
5. Schedule design review for UI/UX questions

---
*Generated by Habitto Jira Figma Analyzer - Universal Context-Aware Analysis Tool*
"""
        
        return report
    
    def save_report(self, analysis_data: dict, output_filename: str = None) -> str:
        """Save the comprehensive report to a file."""
        if not analysis_data:
            return "❌ No analysis data to save"
        
        # Generate filename if not provided
        if not output_filename:
            ticket_key = getattr(analysis_data['ticket'], 'key', 'AUTO-GENERATED')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{ticket_key}_analysis_{timestamp}.md"
        
        # Generate report
        report = self.generate_comprehensive_report(analysis_data)
        
        # Save to file
        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return f"✅ Report saved to: {output_path}"
    
    def batch_analyze(self, input_dir: str = "examples") -> list:
        """Analyze all JSON files in a directory."""
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"❌ Directory {input_dir} does not exist")
            return []
        
        results = []
        json_files = list(input_path.glob("*.json"))
        
        if not json_files:
            print(f"❌ No JSON files found in {input_dir}")
            return []
        
        print(f"🔍 Found {len(json_files)} JSON files to analyze...")
        
        for json_file in json_files:
            print(f"📋 Analyzing {json_file.name}...")
            result = self.analyze_from_json(str(json_file))
            if result:
                results.append((json_file.name, result))
                print(f"✅ Completed analysis for {json_file.name}")
            else:
                print(f"❌ Failed to analyze {json_file.name}")
        
        return results
    
    def generate_batch_report(self, batch_results: list) -> str:
        """Generate a summary report for batch analysis."""
        if not batch_results:
            return "❌ No batch results to report"
        
        report = f"""
# 📊 Batch Analysis Summary Report

## 📋 Analysis Overview
- **Total Files Analyzed**: {len(batch_results)}
- **Analysis Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📈 Summary Statistics
"""
        
        total_questions = 0
        total_test_cases = 0
        total_risk_areas = 0
        
        for filename, analysis_data in batch_results:
            result = analysis_data['analysis']
            questions_count = len(result.suggested_questions) + len(result.design_questions) + len(result.business_questions)
            test_cases_count = len(result.test_cases)
            risk_areas_count = len(result.risk_areas)
            
            total_questions += questions_count
            total_test_cases += test_cases_count
            total_risk_areas += risk_areas_count
            
            report += f"""
### 📄 {filename}
- **Ticket**: {getattr(analysis_data['ticket'], 'key', 'AUTO-GENERATED')} - {getattr(analysis_data['ticket'], 'title', 'No title')}
- **Questions Generated**: {questions_count}
- **Test Cases Generated**: {test_cases_count}
- **Risk Areas**: {risk_areas_count}
- **Figma Links**: {len(getattr(analysis_data['ticket'], 'figma_links', []))}
"""
        
        report += f"""
## 📊 Total Statistics
- **Total Questions Generated**: {total_questions}
- **Total Test Cases Generated**: {total_test_cases}
- **Total Risk Areas Identified**: {total_risk_areas}
- **Average Questions per Ticket**: {total_questions // len(batch_results) if batch_results else 0}
- **Average Test Cases per Ticket**: {total_test_cases // len(batch_results) if batch_results else 0}

---
*Generated by Habitto Jira Figma Analyzer - Batch Processing Mode*
"""
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Habitto Jira Figma Analyzer - Automated Analysis")
    parser.add_argument("--mode", choices=["single", "batch", "interactive"], default="single",
                       help="Analysis mode: single file, batch directory, or interactive")
    parser.add_argument("--input", "-i", help="Input JSON file or directory")
    parser.add_argument("--output", "-o", help="Output filename (optional)")
    parser.add_argument("--title", help="Ticket title (for interactive mode)")
    parser.add_argument("--description", help="Ticket description (for interactive mode)")
    parser.add_argument("--figma-links", nargs="*", help="Figma links (for interactive mode)")
    
    args = parser.parse_args()
    
    analyzer = AutomatedAnalyzer()
    
    if args.mode == "single":
        if not args.input:
            print("❌ Please provide an input file with --input")
            return
        
        print(f"🔍 Analyzing single file: {args.input}")
        result = analyzer.analyze_from_json(args.input)
        
        if result:
            print("✅ Analysis completed successfully!")
            print(analyzer.save_report(result, args.output))
            print("\n📋 Generated Report Preview:")
            print("=" * 50)
            report = analyzer.generate_comprehensive_report(result)
            print(report[:1000] + "..." if len(report) > 1000 else report)
        else:
            print("❌ Analysis failed")
    
    elif args.mode == "batch":
        input_dir = args.input or "examples"
        print(f"🔍 Starting batch analysis of directory: {input_dir}")
        
        batch_results = analyzer.batch_analyze(input_dir)
        
        if batch_results:
            print(f"✅ Batch analysis completed! Processed {len(batch_results)} files.")
            
            # Save individual reports
            for filename, analysis_data in batch_results:
                output_filename = f"{Path(filename).stem}_analysis.md"
                analyzer.save_report(analysis_data, output_filename)
            
            # Generate batch summary
            batch_report = analyzer.generate_batch_report(batch_results)
            batch_output_path = analyzer.output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(batch_output_path, 'w', encoding='utf-8') as f:
                f.write(batch_report)
            
            print(f"📊 Batch summary saved to: {batch_output_path}")
        else:
            print("❌ Batch analysis failed or no files found")
    
    elif args.mode == "interactive":
        print("🎯 Interactive Mode - Habitto Jira Figma Analyzer")
        print("=" * 50)
        
        title = args.title or input("Enter ticket title: ")
        description = args.description or input("Enter ticket description: ")
        figma_links = args.figma_links or []
        
        if not figma_links:
            links_input = input("Enter Figma links (comma-separated, or press Enter to skip): ")
            if links_input.strip():
                figma_links = [link.strip() for link in links_input.split(",")]
        
        print("\n🔍 Analyzing ticket...")
        result = analyzer.analyze_from_text(title, description, figma_links)
        
        if result:
            print("✅ Analysis completed successfully!")
            print(analyzer.save_report(result, args.output))
            print("\n📋 Generated Report Preview:")
            print("=" * 50)
            report = analyzer.generate_comprehensive_report(result)
            print(report[:1000] + "..." if len(report) > 1000 else report)
        else:
            print("❌ Analysis failed")

if __name__ == "__main__":
    main()
