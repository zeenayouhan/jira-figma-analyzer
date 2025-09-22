#!/usr/bin/env python3
"""
Enhanced Jira Figma Analyzer with Bitbucket Integration

This enhanced version includes:
1. Repository context integration
2. Bitbucket API integration
3. Improved question generation based on code structure
4. Automatic analysis capabilities
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from jira_figma_analyzer import JiraFigmaAnalyzer, JiraTicket, AnalysisResult
from bitbucket_integration import BitbucketIntegration

class EnhancedJiraFigmaAnalyzer(JiraFigmaAnalyzer):
    """Enhanced analyzer with repository context."""
    
    def __init__(self, workspace: str = "sj-ml", repository: str = "habitto"):
        super().__init__()
        self.bitbucket = BitbucketIntegration(workspace, repository)
        self.repository_context = None
        self.load_repository_context()
    
    def load_repository_context(self):
        """Load repository context from Bitbucket or cache."""
        try:
            # Try to load from cache first
            if os.path.exists('repository_context.json'):
                with open('repository_context.json', 'r') as f:
                    self.repository_context = json.load(f)
                print("📁 Loaded repository context from cache")
            else:
                # Fetch fresh context from Bitbucket
                self.repository_context = self.bitbucket.analyze_repository_context()
                if self.repository_context and 'error' not in self.repository_context:
                    # Cache the context
                    with open('repository_context.json', 'w') as f:
                        json.dump(self.repository_context, f, indent=2)
                    print("🔄 Fetched and cached fresh repository context")
                else:
                    print("⚠️  Could not fetch repository context")
        except Exception as e:
            print(f"❌ Error loading repository context: {e}")
            self.repository_context = None
    
    def refresh_repository_context(self):
        """Force refresh repository context from Bitbucket."""
        try:
            self.repository_context = self.bitbucket.analyze_repository_context()
            if self.repository_context and 'error' not in self.repository_context:
                with open('repository_context.json', 'w') as f:
                    json.dump(self.repository_context, f, indent=2)
                print("🔄 Repository context refreshed successfully")
                return True
            else:
                print("❌ Failed to refresh repository context")
                return False
        except Exception as e:
            print(f"❌ Error refreshing repository context: {e}")
            return False
    
    def analyze_ticket_content(self, ticket: JiraTicket) -> AnalysisResult:
        """Enhanced analysis with repository context."""
        
        # Get base analysis
        result = super().analyze_ticket_content(ticket)
        
        # Enhance with repository context if available
        if self.repository_context:
            enhanced_questions = self._enhance_questions_with_context(
                result.suggested_questions, ticket
            )
            enhanced_design_questions = self._enhance_design_questions_with_context(
                result.design_questions, ticket
            )
            enhanced_business_questions = self._enhance_business_questions_with_context(
                result.business_questions, ticket
            )
            enhanced_technical_considerations = self._enhance_technical_considerations_with_context(
                result.technical_considerations, ticket
            )
            enhanced_test_cases = self._enhance_test_cases_with_context(
                result.test_cases, ticket
            )
            enhanced_risk_areas = self._enhance_risk_areas_with_context(
                result.risk_areas, ticket
            )
            
            # Create enhanced result
            enhanced_result = AnalysisResult(
                ticket=ticket,
                suggested_questions=enhanced_questions,
                clarifications_needed=result.clarifications_needed,
                technical_considerations=enhanced_technical_considerations,
                design_questions=enhanced_design_questions,
                business_questions=enhanced_business_questions,
                risk_areas=enhanced_risk_areas,
                test_cases=enhanced_test_cases
            )
            
            return enhanced_result
        
        return result
    
    def _enhance_questions_with_context(self, base_questions: List[str], ticket: JiraTicket) -> List[str]:
        """Enhance general questions with repository context."""
        enhanced = list(base_questions)
        
        if not self.repository_context:
            return enhanced
        
        repo_info = self.repository_context.get('repository', {})
        recent_activity = self.repository_context.get('recent_activity', {})
        codebase_structure = self.repository_context.get('codebase_structure', {})
        
        # Add repository-specific questions
        enhanced.extend([
            f"How does this feature integrate with the existing {repo_info.get('primary_language', 'React Native')} codebase?",
            f"Are there any dependencies on the {len(codebase_structure.get('technology_stack', []))} technologies currently used in the project?",
            f"Should this feature follow the same patterns as the {recent_activity.get('commits_count', 0)} recent commits in the repository?",
            "How will this feature affect the existing component architecture?",
            "Are there any existing components that can be reused for this feature?"
        ])
        
        # Add questions based on recent activity
        if recent_activity.get('active_features'):
            active_features = recent_activity['active_features'][:3]
            enhanced.append(f"How does this feature relate to the currently active features: {', '.join(active_features)}?")
        
        # Add questions based on technology stack
        tech_stack = codebase_structure.get('technology_stack', [])
        if 'React Native Metro' in tech_stack:
            enhanced.append("Will this feature require any Metro bundler configuration changes?")
        if 'iOS' in tech_stack:
            enhanced.append("Are there any iOS-specific considerations for this feature?")
        if 'Android' in tech_stack:
            enhanced.append("Are there any Android-specific requirements for this feature?")
        
        return enhanced
    
    def _enhance_design_questions_with_context(self, base_questions: List[str], ticket: JiraTicket) -> List[str]:
        """Enhance design questions with repository context."""
        enhanced = list(base_questions)
        
        if not self.repository_context:
            return enhanced
        
        codebase_structure = self.repository_context.get('codebase_structure', {})
        
        # Add React Native specific design questions
        enhanced.extend([
            "How should this design adapt to different screen sizes on iOS and Android?",
            "Are there any platform-specific design guidelines (iOS Human Interface Guidelines, Material Design) to follow?",
            "How will this design work with React Native's navigation system?",
            "Are there any gesture interactions that need to be considered for mobile?",
            "How should this feature handle different device orientations?"
        ])
        
        # Add questions based on estimated components
        estimated_components = codebase_structure.get('estimated_components', 0)
        if estimated_components > 50:
            enhanced.append("How can this design reuse existing components to maintain consistency?")
        
        return enhanced
    
    def _enhance_business_questions_with_context(self, base_questions: List[str], ticket: JiraTicket) -> List[str]:
        """Enhance business questions with repository context."""
        enhanced = list(base_questions)
        
        if not self.repository_context:
            return enhanced
        
        repo_info = self.repository_context.get('repository', {})
        recent_activity = self.repository_context.get('recent_activity', {})
        
        # Add Habitto-specific business questions
        enhanced.extend([
            "How does this feature support Habitto's core mission of habit formation and tracking?",
            "What user engagement metrics should this feature impact?",
            "How will this feature differentiate Habitto from other habit tracking apps?",
            "What is the expected user adoption timeline for this feature?",
            "How does this feature contribute to user retention and daily active usage?"
        ])
        
        # Add questions based on development activity
        if recent_activity.get('commits_count', 0) > 10:
            enhanced.append("How does this feature fit into the current development sprint and release cycle?")
        
        return enhanced
    
    def _enhance_technical_considerations_with_context(self, base_considerations: List[str], ticket: JiraTicket) -> List[str]:
        """Enhance technical considerations with repository context."""
        enhanced = list(base_considerations)
        
        if not self.repository_context:
            return enhanced
        
        codebase_structure = self.repository_context.get('codebase_structure', {})
        development_patterns = self.repository_context.get('development_patterns', {})
        
        # Add React Native specific considerations
        enhanced.extend([
            "Consider React Native performance implications for this feature",
            "Evaluate impact on app bundle size and startup time",
            "Assess memory usage implications on mobile devices",
            "Consider offline functionality and data synchronization",
            "Evaluate push notification requirements for this feature"
        ])
        
        # Add considerations based on technology stack
        tech_stack = codebase_structure.get('technology_stack', [])
        if 'Jest Testing' in tech_stack:
            enhanced.append("Ensure comprehensive Jest test coverage for this feature")
        if 'TypeScript React' in tech_stack:
            enhanced.append("Maintain TypeScript type safety throughout the implementation")
        
        # Add considerations based on file types
        common_file_types = development_patterns.get('common_file_types', {})
        if 'tsx' in common_file_types or 'ts' in common_file_types:
            enhanced.append("Follow existing TypeScript patterns and interfaces")
        if 'json' in common_file_types:
            enhanced.append("Consider configuration and data structure impacts")
        
        return enhanced
    
    def _enhance_test_cases_with_context(self, base_test_cases: List[str], ticket: JiraTicket) -> List[str]:
        """Enhance test cases with repository context."""
        enhanced = list(base_test_cases)
        
        if not self.repository_context:
            return enhanced
        
        codebase_structure = self.repository_context.get('codebase_structure', {})
        
        # Add React Native specific test cases
        enhanced.extend([
            "Test feature functionality on iOS simulator",
            "Test feature functionality on Android emulator",
            "Test feature with different screen sizes and resolutions",
            "Test feature performance on low-end devices",
            "Test feature behavior during network connectivity issues",
            "Test feature with React Native hot reload",
            "Test feature integration with existing navigation flows",
            "Test feature accessibility with screen readers",
            "Test feature behavior during app backgrounding/foregrounding",
            "Test feature with different device orientations"
        ])
        
        # Add test cases based on technology stack
        tech_stack = codebase_structure.get('technology_stack', [])
        if 'Jest Testing' in tech_stack:
            enhanced.extend([
                "Write unit tests using Jest framework",
                "Create snapshot tests for React components",
                "Test Redux actions and reducers if applicable"
            ])
        
        return enhanced
    
    def _enhance_risk_areas_with_context(self, base_risks: List[str], ticket: JiraTicket) -> List[str]:
        """Enhance risk areas with repository context."""
        enhanced = list(base_risks)
        
        if not self.repository_context:
            return enhanced
        
        recent_activity = self.repository_context.get('recent_activity', {})
        development_patterns = self.repository_context.get('development_patterns', {})
        
        # Add React Native specific risks
        enhanced.extend([
            "Platform-specific implementation differences between iOS and Android",
            "React Native version compatibility issues",
            "Performance degradation on older mobile devices",
            "App store approval requirements and guidelines",
            "Third-party library compatibility and licensing"
        ])
        
        # Add risks based on activity level
        activity_level = development_patterns.get('commit_frequency', 'Unknown')
        if activity_level == 'High activity':
            enhanced.append("Integration conflicts with concurrent development work")
        elif activity_level == 'Low activity':
            enhanced.append("Knowledge transfer gaps due to reduced development activity")
        
        # Add risks based on open PRs
        open_prs = recent_activity.get('open_prs_count', 0)
        if open_prs > 5:
            enhanced.append("Merge conflicts with multiple concurrent pull requests")
        
        return enhanced
    
    def generate_enhanced_report(self, result: AnalysisResult) -> str:
        """Generate enhanced report including repository context."""
        
        # Start with base report
        base_report = self.generate_report(result)
        
        if not self.repository_context:
            return base_report
        
        # Add repository context section
        repo_section = self._generate_repository_context_section()
        
        # Insert repository context after the ticket information
        lines = base_report.split('\n')
        insert_index = -1
        
        for i, line in enumerate(lines):
            if line.strip() == "---" and i > 10:  # Find first separator after header
                insert_index = i + 1
                break
        
        if insert_index > 0:
            lines.insert(insert_index, repo_section)
            lines.insert(insert_index + 1, "")
        
        return '\n'.join(lines)
    
    def _generate_repository_context_section(self) -> str:
        """Generate repository context section for reports."""
        if not self.repository_context:
            return ""
        
        repo_info = self.repository_context.get('repository', {})
        recent_activity = self.repository_context.get('recent_activity', {})
        codebase_structure = self.repository_context.get('codebase_structure', {})
        development_patterns = self.repository_context.get('development_patterns', {})
        
        section = f"""
## 🏗️ Repository Context

### 📊 Repository Information
- **Name**: {repo_info.get('name', 'Unknown')}
- **Primary Language**: {repo_info.get('primary_language', 'Unknown')}
- **Repository Size**: {repo_info.get('size', 0):,} bytes
- **Last Updated**: {repo_info.get('last_updated', 'Unknown')[:10]}

### 🔄 Recent Development Activity
- **Recent Commits**: {recent_activity.get('commits_count', 0)}
- **Open Pull Requests**: {recent_activity.get('open_prs_count', 0)}
- **Commit Frequency**: {development_patterns.get('commit_frequency', 'Unknown')}
- **Active Features**: {', '.join(recent_activity.get('active_features', [])[:3]) or 'None identified'}

### 🛠️ Technology Stack
{chr(10).join(f"- {tech}" for tech in codebase_structure.get('technology_stack', []))}

### 📁 Codebase Structure
- **Estimated Components**: {codebase_structure.get('estimated_components', 0)}
- **Directories**: {codebase_structure.get('directories', 0)}
- **Files**: {codebase_structure.get('files', 0)}

### 📈 Development Patterns
- **Common File Types**: {', '.join(f"{ext} ({count})" for ext, count in list(development_patterns.get('common_file_types', {}).items())[:5])}
- **Feature Areas**: {', '.join(development_patterns.get('feature_areas', [])[:5]) or 'None identified'}

---"""
        
        return section

def main():
    """Test the enhanced analyzer."""
    print("🚀 Testing Enhanced Jira-Figma Analyzer...")
    
    # Initialize enhanced analyzer
    analyzer = EnhancedJiraFigmaAnalyzer()
    
    # Test with sample data
    sample_ticket = {
        'key': 'HAB-123',
        'summary': 'Add profile editing functionality for occupation and country fields',
        'description': 'Users should be able to edit their occupation and country in their profile. This feature should include validation, analytics tracking with Mixpanel, and proper error handling. Figma design: https://www.figma.com/design/fnCxddHpd5tOcjYxzliAxc/Habitto-App-UI--Sprint-Execution?node-id=25461-58968',
        'priority': {'name': 'High'},
        'assignee': {'displayName': 'John Developer'},
        'reporter': {'displayName': 'Product Manager'},
        'labels': ['frontend', 'profile', 'user-management'],
        'components': [{'name': 'User Interface'}, {'name': 'Profile Management'}],
        'comments': []
    }
    
    # Parse and analyze
    ticket = analyzer.parse_jira_ticket(sample_ticket)
    result = analyzer.analyze_ticket_content(ticket)
    
    # Generate enhanced report
    report = analyzer.generate_enhanced_report(result)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_outputs/ENHANCED_analysis_{timestamp}.md"
    
    os.makedirs("analysis_outputs", exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Enhanced analysis saved to: {filename}")
    print(f"📊 Generated {len(result.suggested_questions)} questions")
    print(f"🧪 Generated {len(result.test_cases)} test cases")
    print(f"⚠️  Identified {len(result.risk_areas)} risk areas")

if __name__ == "__main__":
    main()
