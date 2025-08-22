#!/usr/bin/env python3
"""
Jira Figma Analyzer Tool

This tool analyzes Jira tickets that contain Figma links and suggests
questions and clarifications that can be asked from the client.
"""

import re
import json
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class JiraTicket:
    """Represents a Jira ticket with its metadata."""
    ticket_id: str
    title: str
    description: str
    figma_links: List[str]
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    labels: List[str] = None
    components: List[str] = None

@dataclass
class AnalysisResult:
    """Represents the analysis result with suggested questions."""
    ticket: JiraTicket
    suggested_questions: List[str]
    clarifications_needed: List[str]
    technical_considerations: List[str]
    design_questions: List[str]
    business_questions: List[str]
    risk_areas: List[str]
    test_cases: List[str]

class JiraFigmaAnalyzer:
    """Main analyzer class for Jira tickets with Figma links."""
    
    def __init__(self):
        self.figma_patterns = [
            r'https://www\.figma\.com/file/[a-zA-Z0-9]+',
            r'https://figma\.com/file/[a-zA-Z0-9]+',
            r'https://www\.figma\.com/proto/[a-zA-Z0-9]+',
            r'https://figma\.com/proto/[a-zA-Z0-9]+'
        ]
        
        # Common question templates
        self.question_templates = {
            'design': [
                "What is the target screen size/resolution for this design?",
                "Are there any accessibility requirements we need to consider?",
                "What is the expected user flow for this feature?",
                "Are there any specific animations or transitions required?",
                "What should happen in error states or edge cases?",
                "Are there any brand guidelines or design system constraints?",
                "What is the mobile/tablet experience requirements?",
                "Are there any internationalization (i18n) requirements?"
            ],
            'technical': [
                "What is the expected performance requirements?",
                "Are there any browser compatibility requirements?",
                "What is the expected load time for this feature?",
                "Are there any security considerations we should be aware of?",
                "What is the expected user load/scale requirements?",
                "Are there any third-party integrations required?",
                "What is the deployment environment (staging, production)?",
                "Are there any API rate limiting considerations?"
            ],
            'business': [
                "What is the business value/ROI expected from this feature?",
                "Who are the primary users of this feature?",
                "What is the success metric for this feature?",
                "Are there any compliance or legal requirements?",
                "What is the timeline and priority for this feature?",
                "Are there any dependencies on other teams or systems?",
                "What is the expected maintenance and support level?",
                "Are there any budget constraints we should be aware of?"
            ]
        }
    
    def extract_figma_links(self, text: str) -> List[str]:
        """Extract Figma links from text."""
        links = []
        for pattern in self.figma_patterns:
            matches = re.findall(pattern, text)
            links.extend(matches)
        return list(set(links))  # Remove duplicates
    
    def parse_jira_ticket(self, ticket_data: Dict) -> JiraTicket:
        """Parse Jira ticket data into a structured format."""
        # Extract Figma links from description and comments
        description = ticket_data.get('description', '')
        comments = ticket_data.get('comments', [])
        
        all_text = description + ' ' + ' '.join([c.get('body', '') for c in comments])
        figma_links = self.extract_figma_links(all_text)
        
        return JiraTicket(
            ticket_id=ticket_data.get('key', ''),
            title=ticket_data.get('summary', ''),
            description=description,
            figma_links=figma_links,
            priority=ticket_data.get('priority', {}).get('name', ''),
            assignee=ticket_data.get('assignee', {}).get('displayName', ''),
            reporter=ticket_data.get('reporter', {}).get('displayName', ''),
            labels=ticket_data.get('labels', []),
            components=[c.get('name', '') for c in ticket_data.get('components', [])]
        )
    
    def analyze_ticket_content(self, ticket: JiraTicket) -> AnalysisResult:
        """Analyze ticket content and generate suggestions."""
        
        # Analyze ticket content for keywords and context
        content_analysis = self._analyze_content_keywords(ticket)
        
        # Generate questions based on content analysis
        suggested_questions = self._generate_questions(ticket, content_analysis)
        clarifications_needed = self._identify_clarifications(ticket, content_analysis)
        technical_considerations = self._identify_technical_considerations(ticket, content_analysis)
        design_questions = self._generate_design_questions(ticket, content_analysis)
        business_questions = self._generate_business_questions(ticket, content_analysis)
        risk_areas = self._identify_risk_areas(ticket, content_analysis)
        test_cases = self._generate_test_cases(ticket, content_analysis)
        
        return AnalysisResult(
            ticket=ticket,
            suggested_questions=suggested_questions,
            clarifications_needed=clarifications_needed,
            technical_considerations=technical_considerations,
            design_questions=design_questions,
            business_questions=business_questions,
            risk_areas=risk_areas,
            test_cases=test_cases
        )
    
    def _analyze_content_keywords(self, ticket: JiraTicket) -> Dict:
        """Analyze ticket content for relevant keywords and patterns."""
        text = f"{ticket.title} {ticket.description}".lower()
        
        analysis = {
            'has_mobile': any(word in text for word in ['mobile', 'responsive', 'tablet', 'ios', 'android']),
            'has_performance': any(word in text for word in ['performance', 'speed', 'load', 'optimization']),
            'has_accessibility': any(word in text for word in ['accessibility', 'a11y', 'wcag', 'screen reader']),
            'has_integration': any(word in text for word in ['api', 'integration', 'third-party', 'external']),
            'has_security': any(word in text for word in ['security', 'authentication', 'authorization', 'encryption']),
            'has_internationalization': any(word in text for word in ['i18n', 'internationalization', 'localization', 'multi-language']),
            'has_animation': any(word in text for word in ['animation', 'transition', 'motion', 'interaction']),
            'has_error_handling': any(word in text for word in ['error', 'exception', 'fallback', 'edge case']),
            'has_data': any(word in text for word in ['data', 'database', 'storage', 'cache']),
            'has_user_flow': any(word in text for word in ['user flow', 'workflow', 'process', 'journey']),
            'figma_count': len(ticket.figma_links),
            'priority_level': ticket.priority,
            'has_labels': len(ticket.labels) > 0,
            'has_components': len(ticket.components) > 0
        }
        
        return analysis
    
    def _generate_questions(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate general questions based on ticket analysis."""
        questions = []
        
        # Context-specific questions based on ticket content
        content_lower = f"{ticket.title} {ticket.description}".lower()
        
        # Habitto-specific general questions for any feature
        questions.extend([
            "How does this feature align with Habitto's user engagement and retention strategy?",
            "What user research or feedback led to this feature request?",
            "How does this feature integrate with Habitto's existing user journey?",
            "What are the expected business metrics this feature should impact?",
            "Are there any Habitto-specific compliance or data privacy considerations?",
            "How should this feature handle Habitto's multi-platform experience (web, mobile)?",
            "What is the expected user adoption rate for this feature?",
            "How does this feature support Habitto's advisor-client relationship model?"
        ])
        
        # Feature-specific contextual questions
        if any(word in content_lower for word in ['profile', 'user', 'occupation', 'country', 'residence', 'edit', 'update']):
            questions.extend([
                "What predefined lists or options should be available for user selections?",
                "Should the options match exactly what was used in the onboarding flow?",
                "Are there any restrictions on who can edit these fields?",
                "How should this integrate with Habitto's user verification system?"
            ])
        
        if any(word in content_lower for word in ['booking', 'session', 'advisor', 'availability', 'slot', 'schedule']):
            questions.extend([
                "How should the system handle real-time availability updates?",
                "What happens if data changes while the user is in the flow?",
                "How should the system handle capacity limits and overbooking?",
                "What is the expected response time for data queries?",
                "How should the system handle timezone differences?"
            ])
        
        if any(word in content_lower for word in ['payment', 'billing', 'subscription', 'purchase']):
            questions.extend([
                "How should this integrate with Habitto's payment processing system?",
                "What happens if payment processing fails?",
                "How should the system handle refunds or cancellations?",
                "What compliance requirements apply to financial transactions?"
            ])
        
        if any(word in content_lower for word in ['notification', 'email', 'sms', 'push', 'alert']):
            questions.extend([
                "How should this integrate with Habitto's notification system?",
                "What are the user preferences for notification frequency?",
                "How should the system handle notification failures?",
                "What compliance requirements apply to communications?"
            ])
        
        if any(word in content_lower for word in ['report', 'analytics', 'dashboard', 'metrics']):
            questions.extend([
                "How should this integrate with Habitto's analytics system?",
                "What data privacy considerations apply to reporting?",
                "How should the system handle data aggregation and caching?",
                "What are the performance requirements for data queries?"
            ])
        
        if any(word in content_lower for word in ['chat', 'message', 'communication', 'support']):
            questions.extend([
                "How should this integrate with Habitto's communication system?",
                "What are the moderation requirements for user communications?",
                "How should the system handle message delivery failures?",
                "What compliance requirements apply to message storage?"
            ])
        
        # Withdrawal/Money specific questions
        if any(word in content_lower for word in ['withdraw', 'withdrawal', 'payout', 'cash out', 'money', 'funds']):
            questions.extend([
                "What are the minimum and maximum withdrawal limits for Habitto users?",
                "How should the system verify user identity for withdrawals?",
                "What payment methods should be supported for withdrawals?",
                "How should the system handle failed withdrawal attempts?",
                "What are the processing timeframes for different withdrawal methods?",
                "How should the system handle withdrawal fees and calculations?",
                "What compliance and regulatory requirements apply to withdrawals?",
                "How should the system handle fraud detection for withdrawals?"
            ])
        
        # Authentication specific questions
        if any(word in content_lower for word in ['login', 'authentication', 'signin', 'signup', 'register']):
            questions.extend([
                "What authentication methods should Habitto support (email, phone, social)?",
                "How should the system handle failed login attempts?",
                "What are the password requirements and security policies?",
                "How should the system handle account lockouts and recovery?",
                "What two-factor authentication options should be available?",
                "How should the system handle social media login integration?"
            ])
        
        # Search/Discovery specific questions
        if any(word in content_lower for word in ['search', 'filter', 'sort', 'browse', 'discover']):
            questions.extend([
                "What search criteria should be available to Habitto users?",
                "How should search results be ranked and displayed?",
                "What filtering options should be provided?",
                "How should the system handle empty search results?",
                "What are the performance requirements for search functionality?",
                "How should search history and suggestions be handled?"
            ])
        
        # Onboarding specific questions
        if any(word in content_lower for word in ['onboarding', 'welcome', 'tutorial', 'getting started']):
            questions.extend([
                "How many steps should the Habitto onboarding process have?",
                "What information is mandatory vs optional during onboarding?",
                "How should the system handle incomplete onboarding flows?",
                "What personalization should happen during onboarding?",
                "How should progress be saved if users exit mid-onboarding?",
                "What success metrics define completed onboarding?"
            ])
        
        # Settings/Preferences specific questions
        if any(word in content_lower for word in ['settings', 'preferences', 'configuration', 'account']):
            questions.extend([
                "What user preferences should be configurable in Habitto?",
                "How should settings changes be validated and saved?",
                "What privacy controls should users have access to?",
                "How should the system handle settings synchronization across devices?",
                "What are the default settings for new Habitto users?",
                "How should sensitive settings changes be authenticated?"
            ])
        
        # Real-time/database specific questions
        if any(word in content_lower for word in ['real time', 'database', 'save']):
            questions.append("What is the expected response time for real-time database updates?")
            questions.append("How should the system handle concurrent edits to the same profile?")
            questions.append("Should there be any validation before saving changes to the database?")
        
        # Analytics/tracking specific questions
        if any(word in content_lower for word in ['mixpanel', 'event', 'track', 'analytics']):
            questions.append("What specific data should be included in the Mixpanel event for profile updates?")
            questions.append("Should the tracking differentiate between Occupation vs Country of Residence changes?")
            questions.append("Are there any user privacy settings that should disable this tracking?")
        
        # Questions based on Figma links
        if analysis['figma_count'] > 0:
            questions.append("Does the Figma design show all necessary states (default, editing, loading, error)?")
            questions.append("Are the dropdown styles consistent with the existing Habitto design system?")
            if analysis['figma_count'] > 1:
                questions.append("How do these multiple Figma designs relate to each other in the user flow?")
        
        # Questions based on priority
        if analysis['priority_level'] in ['High', 'Critical']:
            questions.append("What user pain point or business goal makes this profile editing feature high priority?")
            questions.append("Are there any sprint dependencies that could block this high-priority item?")
        
        # Questions based on content analysis
        if not analysis['has_user_flow']:
            questions.append("What is the complete user journey from profile view to successful edit completion?")
        
        if not analysis['has_error_handling']:
            questions.append("How should the system handle network failures during profile updates?")
        
        return questions
    
    def _identify_clarifications(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Identify areas that need clarification."""
        clarifications = []
        
        # Check for vague descriptions
        if len(ticket.description.strip()) < 50:
            clarifications.append("The ticket description is quite brief. More details about requirements would be helpful.")
        
        # Check for missing technical details
        if not analysis['has_performance'] and 'performance' not in ticket.title.lower():
            clarifications.append("Performance requirements are not specified.")
        
        if not analysis['has_accessibility']:
            clarifications.append("Accessibility requirements are not mentioned.")
        
        # Check for missing business context
        if not any(word in ticket.description.lower() for word in ['user', 'customer', 'business', 'goal']):
            clarifications.append("Business context and user value are not clearly stated.")
        
        return clarifications
    
    def _identify_technical_considerations(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Identify technical considerations that should be discussed."""
        considerations = []
        
        if analysis['has_mobile']:
            considerations.append("Mobile responsiveness and touch interactions")
        
        if analysis['has_integration']:
            considerations.append("API integration and data flow")
        
        if analysis['has_security']:
            considerations.append("Security implementation and data protection")
        
        if analysis['has_data']:
            considerations.append("Data storage and caching strategy")
        
        if analysis['has_internationalization']:
            considerations.append("Internationalization and localization setup")
        
        return considerations
    
    def _generate_design_questions(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate comprehensive UI/UX design questions for Habitto."""
        questions = []
        content_lower = f"{ticket.title} {ticket.description}".lower()
        
        # ===== CORE UI/UX QUESTIONS =====
        questions.append("How does this feature align with Habitto's design system and component library?")
        questions.append("What is the primary user journey and how does this feature fit into it?")
        questions.append("How should the feature handle different screen sizes (mobile, tablet, desktop)?")
        questions.append("What visual hierarchy should be established for this feature?")
        questions.append("How should loading states and transitions be designed?")
        questions.append("What error states and empty states should be considered?")
        questions.append("How should accessibility (WCAG) requirements be met?")
        questions.append("What micro-interactions and animations would enhance the user experience?")
        
        # ===== HABITTO-SPECIFIC DESIGN QUESTIONS =====
        questions.append("How does this feature maintain consistency with Habitto's existing UI patterns?")
        questions.append("What Habitto brand colors, typography, and spacing should be used?")
        questions.append("How should this feature integrate with Habitto's navigation and layout structure?")
        questions.append("What iconography and visual elements align with Habitto's design language?")
        questions.append("How should the feature handle Habitto's light/dark mode preferences?")
        
        # ===== CONTEXT-SPECIFIC UI QUESTIONS =====
        
        # Profile/User Management
        if any(word in content_lower for word in ['profile', 'edit', 'user', 'account']):
            questions.append("How should edit states be visually distinguished from read-only states?")
            questions.append("What visual feedback should users see when changes are being saved?")
            questions.append("How should form validation errors be displayed?")
            questions.append("Should there be confirmation dialogs for important changes?")
            questions.append("How should the profile page handle both mobile and tablet layouts?")
            questions.append("What should the visual flow be for multi-step profile updates?")
            questions.append("How should profile data be displayed in different contexts?")
        
        # Forms and Input
        if any(word in content_lower for word in ['form', 'input', 'field', 'dropdown', 'select']):
            questions.append("What input validation patterns should be used?")
            questions.append("How should form errors be displayed and resolved?")
            questions.append("Should there be auto-save functionality for form fields?")
            questions.append("How should required vs optional fields be visually distinguished?")
            questions.append("What should the tab order and keyboard navigation be?")
            questions.append("How should form fields handle different input types (text, number, date, etc.)?")
            questions.append("Should there be inline help text or tooltips for complex fields?")
        
        # Authentication/Security
        if any(word in content_lower for word in ['login', 'auth', 'otp', 'security', 'password']):
            questions.append("How should security-related UI elements be designed to build trust?")
            questions.append("What visual feedback should users see during authentication processes?")
            questions.append("How should error messages for authentication failures be displayed?")
            questions.append("What should the visual flow be for multi-factor authentication?")
            questions.append("How should session timeouts and re-authentication be handled?")
            questions.append("What visual cues should indicate secure vs insecure states?")
        
        # Notifications/Communication
        if any(word in content_lower for word in ['notification', 'message', 'alert', 'email', 'sms']):
            questions.append("How should different types of notifications be visually distinguished?")
            questions.append("What should the notification hierarchy and priority system be?")
            questions.append("How should users be able to manage notification preferences?")
            questions.append("What should the visual design of notification badges and indicators be?")
            questions.append("How should notification states (read/unread) be displayed?")
            questions.append("What should the notification center or inbox design be?")
        
        # Data Display/Analytics
        if any(word in content_lower for word in ['dashboard', 'chart', 'data', 'report', 'analytics']):
            questions.append("How should data be visualized for different user types?")
            questions.append("What chart types and data representations are most appropriate?")
            questions.append("How should empty states be handled for data displays?")
            questions.append("What should the data filtering and sorting UI be?")
            questions.append("How should data be made accessible and understandable?")
            questions.append("What should the responsive design be for data-heavy screens?")
        
        # Mobile-Specific
        if any(word in content_lower for word in ['mobile', 'app', 'touch', 'swipe']):
            questions.append("How should touch interactions be optimized for mobile users?")
            questions.append("What should the gesture patterns and interactions be?")
            questions.append("How should the feature handle different mobile orientations?")
            questions.append("What should the mobile navigation patterns be?")
            questions.append("How should the feature work with mobile keyboards and input methods?")
            questions.append("What should the mobile-specific loading and error states be?")
        
        # ===== INTERACTION DESIGN QUESTIONS =====
        questions.append("What should the user flow and interaction patterns be?")
        questions.append("How should users navigate to and from this feature?")
        questions.append("What should the feedback mechanisms be for user actions?")
        questions.append("How should the feature handle user errors and recovery?")
        questions.append("What should the success states and confirmation flows be?")
        questions.append("How should the feature handle progressive disclosure of information?")
        
        # ===== PERFORMANCE AND TECHNICAL UI QUESTIONS =====
        questions.append("How should the UI handle slow network connections?")
        questions.append("What should the offline state and sync indicators be?")
        questions.append("How should the feature handle large datasets or slow loading?")
        questions.append("What should the caching and data refresh indicators be?")
        questions.append("How should the UI handle concurrent user actions?")
        
        # ===== ACCESSIBILITY AND INCLUSION =====
        questions.append("How should the feature support screen readers and assistive technologies?")
        questions.append("What should the color contrast and visual accessibility be?")
        questions.append("How should the feature handle different font sizes and zoom levels?")
        questions.append("What should the keyboard navigation and focus management be?")
        questions.append("How should the feature support users with motor impairments?")
        
        # ===== INTERNATIONALIZATION =====
        questions.append("How should the feature handle different languages and text directions?")
        questions.append("What should the date, time, and number formatting be for different locales?")
        questions.append("How should the feature handle cultural differences in UI patterns?")
        
        # ===== TESTING AND VALIDATION =====
        questions.append("What should the design review and approval process be?")
        questions.append("How should user testing be conducted for this feature?")
        questions.append("What metrics should be tracked to measure UI/UX success?")
        questions.append("How should design iterations and feedback be handled?")
        
        return questions
        
        if analysis['has_mobile']:
            questions.append("How should touch interactions work for the dropdown on mobile devices?")
        
        return questions[:7]  # Return top 7 most relevant
    
    def _generate_business_questions(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate business-specific questions."""
        questions = []
        content_lower = f"{ticket.title} {ticket.description}".lower()
        
        # Habitto-specific business questions
        if any(word in content_lower for word in ['profile', 'user', 'occupation', 'country']):
            questions.append("How does enabling profile editing support Habitto's user engagement and retention goals?")
            questions.append("What user research or feedback indicated the need for editable occupation/country fields?")
            questions.append("Will this feature help with user onboarding completion rates or profile completeness metrics?")
            questions.append("Are there any compliance requirements for collecting and updating occupation/country data?")
        
        # Analytics and tracking business questions
        if any(word in content_lower for word in ['mixpanel', 'event', 'track']):
            questions.append("How will the Mixpanel tracking data be used to improve Habitto's user experience?")
            questions.append("What business KPIs should this feature impact (user satisfaction, profile completion, etc.)?")
        
        # General business questions with Habitto context
        questions.append("How does this feature align with Habitto's current product roadmap and user acquisition strategy?")
        questions.append("What is the expected user adoption rate for this profile editing feature?")
        
        # Customize based on analysis
        if analysis['priority_level'] in ['High', 'Critical']:
            questions.append("What specific business impact makes this profile editing feature high priority for Habitto?")
        
        return questions[:7]  # Return top 7 most relevant
    
    def _identify_risk_areas(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Identify potential risk areas."""
        risks = []
        
        if analysis['figma_count'] == 0:
            risks.append("No design reference provided - may lead to misinterpretation")
        
        if analysis['figma_count'] > 3:
            risks.append("Multiple design files may indicate scope creep")
        
        if not analysis['has_user_flow']:
            risks.append("Missing user flow may lead to poor UX")
        
        if analysis['priority_level'] in ['High', 'Critical'] and not analysis['has_performance']:
            risks.append("High priority feature without performance requirements")
        
        return risks
    
    def _generate_test_cases(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate test cases based on ticket content and requirements."""
        test_cases = []
        content_lower = f"{ticket.title} {ticket.description}".lower()
        
        # Generic Habitto test cases for any feature
        test_cases.extend([
            "**Core Functionality Tests:**",
            "- Verify the main feature works as described in acceptance criteria",
            "- Verify user can complete the primary user journey successfully",
            "- Verify feature integrates with Habitto's authentication system",
            "- Verify feature respects user permissions and access controls",
            "- Verify feature works correctly for both new and existing users",
            "",
            "**Error Handling Tests:**",
            "- Verify system handles network failures gracefully",
            "- Verify system shows appropriate error messages",
            "- Verify system allows users to retry failed operations",
            "- Verify system maintains data integrity during errors",
            "",
            "**Performance Tests:**",
            "- Verify feature responds within acceptable time limits (2-3 seconds)",
            "- Verify feature doesn't degrade overall app performance",
            "- Verify feature handles expected user load without issues",
            "",
            "**Accessibility Tests:**",
            "- Verify feature is accessible via keyboard navigation",
            "- Verify feature works with screen readers",
            "- Verify feature meets WCAG accessibility standards",
            "",
            "**Cross-platform Tests:**",
            "- Verify feature works correctly on web browsers",
            "- Verify feature works correctly on mobile devices",
            "- Verify feature maintains consistency across platforms",
            "",
            "**Data Integrity Tests:**",
            "- Verify data is correctly saved and retrieved",
            "- Verify data persists correctly after browser refresh",
            "- Verify data is consistent across different views",
            "",
            "**Integration Tests:**",
            "- Verify feature integrates with Habitto's user management system",
            "- Verify feature integrates with Habitto's analytics system",
            "- Verify feature integrates with Habitto's notification system"
        ])
        
        # Feature-specific test cases
        if any(word in content_lower for word in ['profile', 'edit', 'occupation', 'country', 'residence', 'update']):
            test_cases.extend([
                "**Functional Tests:**",
                "- Verify user can click Edit button next to Occupation field",
                "- Verify user can click Edit button next to Country of Residence field",
                "- Verify dropdown appears with predefined options for Occupation",
                "- Verify dropdown appears with predefined options for Country of Residence",
                "- Verify dropdown options match onboarding flow options exactly",
                "- Verify user can select a new value from Occupation dropdown",
                "- Verify user can select a new value from Country of Residence dropdown",
                "- Verify changes are saved to database in real-time",
                "- Verify user sees confirmation/feedback when changes are saved",
                "",
                "**Validation Tests:**",
                "- Verify dropdown closes when user clicks outside of it",
                "- Verify dropdown closes when user selects an option",
                "- Verify user cannot edit fields if not logged in",
                "- Verify user cannot edit other users' profile fields",
                "",
                "**Error Handling Tests:**",
                "- Verify system handles network failure during save operation",
                "- Verify system shows appropriate error message if save fails",
                "- Verify system retries save operation on network recovery",
                "- Verify user can retry saving if initial attempt fails",
                "",
                "**Concurrent Access Tests:**",
                "- Verify system handles multiple users editing same profile simultaneously",
                "- Verify last-write-wins or conflict resolution works correctly",
                "",
                "**Analytics Tests:**",
                "- Verify Mixpanel event is fired when Occupation is updated",
                "- Verify Mixpanel event is fired when Country of Residence is updated",
                "- Verify Mixpanel event includes correct user ID and timestamp",
                "- Verify Mixpanel event includes old and new values",
                "- Verify tracking respects user privacy settings",
                "",
                "**UI/UX Tests:**",
                "- Verify edit state is visually distinct from read-only state",
                "- Verify dropdown is accessible via keyboard navigation",
                "- Verify dropdown works correctly on mobile devices",
                "- Verify dropdown works correctly on tablet devices",
                "- Verify loading states are shown during save operations",
                "- Verify success states are shown after successful save",
                "",
                "**Performance Tests:**",
                "- Verify dropdown opens within 200ms of clicking Edit button",
                "- Verify save operation completes within 2 seconds",
                "- Verify page performance is not degraded with multiple dropdowns open",
                "",
                "**Accessibility Tests:**",
                "- Verify dropdown is accessible via screen readers",
                "- Verify keyboard navigation works for all dropdown options",
                "- Verify focus management works correctly when dropdown opens/closes",
                "- Verify ARIA labels are properly set for dropdown elements"
            ])
        
        # Booking system specific test cases
        if any(word in content_lower for word in ['booking', 'session', 'advisor', 'availability', 'slot', 'schedule']):
            test_cases.extend([
                "**Functional Tests:**",
                "- Verify system defaults to 'Single Availability' mode on booking screen",
                "- Verify user can toggle between 'Single Availability' and 'Shared Availability'",
                "- Verify only assigned advisor slots are shown in Single Availability mode",
                "- Verify all advisor slots are shown in Shared Availability mode",
                "- Verify slots are sorted by earliest time in Shared Availability mode",
                "- Verify user can book a slot with their assigned advisor",
                "- Verify user can book a slot with a different advisor",
                "- Verify assigned advisor is updated when booking with different advisor",
                "- Verify system prioritizes assigned advisor when multiple advisors available",
                "",
                "**Availability Management Tests:**",
                "- Verify system handles advisor availability changes in real-time",
                "- Verify system prevents double-booking of advisor slots",
                "- Verify system shows appropriate message when no slots available",
                "- Verify system handles timezone differences correctly",
                "- Verify system respects advisor capacity limits",
                "",
                "**Toggle and Refresh Tests:**",
                "- Verify slot list refreshes when switching between availability modes",
                "- Verify booking flow is not restarted when toggling modes",
                "- Verify user selections are preserved when toggling modes",
                "- Verify loading states are shown during slot refresh",
                "",
                "**Edge Case Tests:**",
                "- Verify system handles advisor becoming unavailable during booking",
                "- Verify system handles network failures during slot queries",
                "- Verify system shows fallback to assigned advisor when no shared slots",
                "- Verify system handles multiple users booking same slot simultaneously",
                "",
                "**UI/UX Tests:**",
                "- Verify toggle button is clearly visible and accessible",
                "- Verify slot display is responsive on mobile devices",
                "- Verify advisor information is clearly displayed for each slot",
                "- Verify booking confirmation shows correct advisor assignment",
                "",
                "**Performance Tests:**",
                "- Verify slot queries complete within 3 seconds",
                "- Verify toggle between modes responds within 1 second",
                "- Verify system can handle 100+ advisor slots without performance degradation",
                "",
                "**Data Integrity Tests:**",
                "- Verify advisor assignment is correctly updated in database",
                "- Verify booking history shows correct advisor information",
                "- Verify availability data is consistent across all queries",
                "",
                "**Integration Tests:**",
                "- Verify booking system integrates with advisor management system",
                "- Verify booking system integrates with user profile system",
                "- Verify booking system integrates with notification system",
                "- Verify booking system integrates with analytics tracking"
            ])
        
        # Payment system specific test cases
        if any(word in content_lower for word in ['payment', 'billing', 'subscription', 'purchase', 'transaction']):
            test_cases.extend([
                "**Payment Processing Tests:**",
                "- Verify payment processing works with Habitto's payment gateway",
                "- Verify system handles payment failures gracefully",
                "- Verify refund processing works correctly",
                "- Verify subscription management functions properly",
                "- Verify payment confirmation emails are sent",
                "",
                "**Security Tests:**",
                "- Verify payment data is encrypted and secure",
                "- Verify PCI compliance requirements are met",
                "- Verify sensitive data is not logged or exposed",
                "",
                "**Financial Tests:**",
                "- Verify transaction amounts are calculated correctly",
                "- Verify tax calculations are accurate",
                "- Verify currency conversion works properly",
                "- Verify financial reporting is accurate"
            ])
        
        # Notification system specific test cases
        if any(word in content_lower for word in ['notification', 'email', 'sms', 'push', 'alert', 'message']):
            test_cases.extend([
                "**Notification Delivery Tests:**",
                "- Verify notifications are sent to correct recipients",
                "- Verify notification content is accurate and personalized",
                "- Verify notification timing is appropriate",
                "- Verify users can manage notification preferences",
                "",
                "**Channel Tests:**",
                "- Verify email notifications are delivered successfully",
                "- Verify push notifications work on mobile devices",
                "- Verify SMS notifications are sent correctly",
                "- Verify in-app notifications are displayed properly",
                "",
                "**Compliance Tests:**",
                "- Verify users can opt-out of notifications",
                "- Verify notification frequency respects user preferences",
                "- Verify compliance with email marketing regulations"
            ])
        
        # Analytics/Reporting specific test cases
        if any(word in content_lower for word in ['report', 'analytics', 'dashboard', 'metrics', 'data']):
            test_cases.extend([
                "**Data Accuracy Tests:**",
                "- Verify analytics data is collected accurately",
                "- Verify reports display correct information",
                "- Verify data aggregation calculations are correct",
                "- Verify real-time data updates work properly",
                "",
                "**Performance Tests:**",
                "- Verify reports load within acceptable time limits",
                "- Verify dashboard performance with large datasets",
                "- Verify data export functionality works correctly",
                "",
                "**Privacy Tests:**",
                "- Verify user data privacy is maintained",
                "- Verify data anonymization works correctly",
                "- Verify compliance with data protection regulations"
            ])
        
        # Communication/Chat specific test cases
        if any(word in content_lower for word in ['chat', 'message', 'communication', 'support', 'conversation']):
            test_cases.extend([
                "**Message Tests:**",
                "- Verify messages are sent and received correctly",
                "- Verify message threading works properly",
                "- Verify file attachments work correctly",
                "- Verify message search functionality works",
                "",
                "**Real-time Tests:**",
                "- Verify real-time message delivery works",
                "- Verify typing indicators work correctly",
                "- Verify online/offline status is accurate",
                "",
                "**Moderation Tests:**",
                "- Verify content moderation works properly",
                "- Verify inappropriate content is flagged",
                "- Verify user blocking functionality works"
            ])
        
        # Withdrawal/Money specific test cases
        if any(word in content_lower for word in ['withdraw', 'withdrawal', 'payout', 'cash out', 'money', 'funds']):
            test_cases.extend([
                "**Withdrawal Processing Tests:**",
                "- Verify user can initiate withdrawal request successfully",
                "- Verify system validates withdrawal amounts against limits",
                "- Verify system processes withdrawal to correct payment method",
                "- Verify withdrawal status updates are accurate",
                "- Verify withdrawal confirmation emails are sent",
                "",
                "**Validation Tests:**",
                "- Verify minimum withdrawal amount is enforced",
                "- Verify maximum withdrawal amount is enforced",
                "- Verify insufficient balance scenarios are handled",
                "- Verify account verification requirements are checked",
                "- Verify withdrawal frequency limits are enforced",
                "",
                "**Security Tests:**",
                "- Verify identity verification for withdrawal requests",
                "- Verify fraud detection systems are triggered appropriately",
                "- Verify suspicious activity is flagged and blocked",
                "- Verify two-factor authentication for withdrawals",
                "",
                "**Payment Method Tests:**",
                "- Verify bank transfer withdrawals work correctly",
                "- Verify digital wallet withdrawals work correctly",
                "- Verify payment method validation works",
                "- Verify failed payment method scenarios are handled",
                "",
                "**Fee Calculation Tests:**",
                "- Verify withdrawal fees are calculated correctly",
                "- Verify fee disclosure is shown to users",
                "- Verify net amount calculations are accurate",
                "",
                "**Compliance Tests:**",
                "- Verify regulatory reporting requirements are met",
                "- Verify anti-money laundering checks are performed",
                "- Verify transaction limits comply with regulations",
                "",
                "**Error Handling Tests:**",
                "- Verify failed withdrawal attempts are handled gracefully",
                "- Verify system retry logic works for failed withdrawals",
                "- Verify error messages are clear and actionable",
                "- Verify rollback procedures work for failed transactions"
            ])
        
        # Authentication specific test cases
        if any(word in content_lower for word in ['login', 'authentication', 'signin', 'signup', 'register']):
            test_cases.extend([
                "**Login Tests:**",
                "- Verify successful login with valid credentials",
                "- Verify login failure with invalid credentials",
                "- Verify account lockout after multiple failed attempts",
                "- Verify password reset functionality works",
                "- Verify social media login integration works",
                "",
                "**Registration Tests:**",
                "- Verify new user registration process works",
                "- Verify email verification process works",
                "- Verify duplicate account prevention works",
                "- Verify password strength requirements are enforced",
                "",
                "**Security Tests:**",
                "- Verify two-factor authentication works correctly",
                "- Verify session management works properly",
                "- Verify password encryption is secure",
                "- Verify account recovery process is secure",
                "",
                "**Multi-platform Tests:**",
                "- Verify login works across web and mobile",
                "- Verify session synchronization across devices",
                "- Verify logout works properly on all platforms"
            ])
        
        # Search/Discovery specific test cases
        if any(word in content_lower for word in ['search', 'filter', 'sort', 'browse', 'discover']):
            test_cases.extend([
                "**Search Functionality Tests:**",
                "- Verify search returns relevant results",
                "- Verify search handles typos and variations",
                "- Verify search autocomplete works correctly",
                "- Verify search history is saved and accessible",
                "",
                "**Filter Tests:**",
                "- Verify filtering options work correctly",
                "- Verify multiple filters can be applied simultaneously",
                "- Verify filter reset functionality works",
                "",
                "**Performance Tests:**",
                "- Verify search results load within acceptable time",
                "- Verify search works with large datasets",
                "- Verify search pagination works correctly",
                "",
                "**Empty Results Tests:**",
                "- Verify appropriate message is shown for no results",
                "- Verify search suggestions are provided for empty results"
            ])
        
        # Onboarding specific test cases
        if any(word in content_lower for word in ['onboarding', 'welcome', 'tutorial', 'getting started']):
            test_cases.extend([
                "**Onboarding Flow Tests:**",
                "- Verify user can complete full onboarding process",
                "- Verify mandatory fields are enforced",
                "- Verify optional fields can be skipped",
                "- Verify progress is saved between steps",
                "",
                "**Navigation Tests:**",
                "- Verify user can go back to previous steps",
                "- Verify user can exit and resume onboarding",
                "- Verify step validation works correctly",
                "",
                "**Personalization Tests:**",
                "- Verify user preferences are captured correctly",
                "- Verify personalized experience is applied after onboarding"
            ])
        
        # Real-time functionality test cases
        if any(word in content_lower for word in ['real time', 'database', 'save']):
            test_cases.extend([
                "**Real-time Tests:**",
                "- Verify changes are immediately reflected in database",
                "- Verify changes are immediately visible to user",
                "- Verify no manual refresh is required to see updated values",
                "- Verify real-time updates work across different browser tabs"
            ])
        
        # Mobile responsiveness test cases
        if analysis['has_mobile']:
            test_cases.extend([
                "**Mobile Tests:**",
                "- Verify dropdown works correctly on iOS Safari",
                "- Verify dropdown works correctly on Android Chrome",
                "- Verify touch interactions work properly on mobile devices",
                "- Verify dropdown positioning is correct on small screens",
                "- Verify dropdown doesn't overflow screen boundaries"
            ])
        
        # General test cases
        test_cases.extend([
            "**Cross-browser Tests:**",
            "- Verify functionality works in Chrome, Firefox, Safari, Edge",
            "- Verify functionality works in latest 2 versions of each browser",
            "",
            "**Data Integrity Tests:**",
            "- Verify profile data is not corrupted after multiple edits",
            "- Verify profile data persists correctly after browser refresh",
            "- Verify profile data is correctly loaded from database on page load"
        ])
        
        return test_cases
    
    def generate_report(self, analysis_result: AnalysisResult) -> str:
        """Generate a formatted report from the analysis."""
        report = f"""
# Jira Ticket Analysis Report

## Ticket Information
- **ID**: {analysis_result.ticket.ticket_id}
- **Title**: {analysis_result.ticket.title}
- **Priority**: {analysis_result.ticket.priority or 'Not specified'}
- **Figma Links**: {len(analysis_result.ticket.figma_links)} found

## Suggested Questions for Client

### General Questions
{chr(10).join(f"- {q}" for q in analysis_result.suggested_questions)}

### Design Questions
{chr(10).join(f"- {q}" for q in analysis_result.design_questions)}

### Business Questions
{chr(10).join(f"- {q}" for q in analysis_result.business_questions)}

## Areas Needing Clarification
{chr(10).join(f"- {c}" for c in analysis_result.clarifications_needed)}

## Technical Considerations
{chr(10).join(f"- {tc}" for tc in analysis_result.technical_considerations)}

## Risk Areas
{chr(10).join(f"- {r}" for r in analysis_result.risk_areas)}

## Suggested Test Cases
{chr(10).join(f"{tc}" for tc in analysis_result.test_cases)}

## Figma Links Found
{chr(10).join(f"- {link}" for link in analysis_result.ticket.figma_links)}
"""
        return report.strip()

def main():
    """Main function for testing the analyzer."""
    analyzer = JiraFigmaAnalyzer()
    
    # Example ticket data
    sample_ticket = {
        'key': 'PROJ-123',
        'summary': 'Implement new user dashboard with responsive design',
        'description': 'Create a new dashboard for users to view their data. Should be mobile-friendly and include charts. Figma link: https://www.figma.com/file/abc123/dashboard-design',
        'priority': {'name': 'High'},
        'assignee': {'displayName': 'John Doe'},
        'reporter': {'displayName': 'Jane Smith'},
        'labels': ['frontend', 'dashboard'],
        'components': [{'name': 'User Interface'}],
        'comments': []
    }
    
    # Parse and analyze
    ticket = analyzer.parse_jira_ticket(sample_ticket)
    result = analyzer.analyze_ticket_content(ticket)
    
    # Generate report
    report = analyzer.generate_report(result)
    print(report)

if __name__ == "__main__":
    main()
