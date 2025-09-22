#!/usr/bin/env python3
"""
Jira Figma Analyzer Tool

This tool analyzes Jira tickets that contain Figma links and suggests
questions and clarifications that can be asked from the client.
"""

import re
import json
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Figma integration
try:
    from figma_integration import FigmaIntegration
    FIGMA_AVAILABLE = True
except ImportError:
    FIGMA_AVAILABLE = False
    print("⚠️ Figma integration not available. Install required dependencies for full Figma analysis.")

# Import feedback learning system
try:
    from feedback_learning_system import FeedbackLearningSystem
    from feedback_system import FeedbackSystem
    FEEDBACK_LEARNING_AVAILABLE = True
except ImportError:
    FEEDBACK_LEARNING_AVAILABLE = False

# Import PDF design analysis
try:
    from pdf_design_analyzer import PDFDesignAnalyzer
    PDF_DESIGN_AVAILABLE = True
except ImportError:
    PDF_DESIGN_AVAILABLE = False
    print("⚠️ PDF design analysis not available. Install PyMuPDF and PyPDF2 for PDF design analysis.")

# Import media analyzer for videos and images

# Import smart routing system
try:
    from smart_routing_system import SmartRoutingSystem
    SMART_ROUTING_AVAILABLE = True
except ImportError:
    SMART_ROUTING_AVAILABLE = False
    print("⚠️ Smart routing not available. Install required dependencies for smart assignment.")
try:
    from media_analyzer import MediaAnalyzer
    MEDIA_ANALYSIS_AVAILABLE = True
except ImportError:
    MEDIA_ANALYSIS_AVAILABLE = False
    print("⚠️ Media analysis not available. Install Pillow and opencv-python for media analysis.")

# Import GPT-4 Vision integration
try:
    from gpt4_vision_integration import GPT4VisionAnalyzer, VisualAnalysisResult
    GPT4_VISION_AVAILABLE = True
except ImportError:
    GPT4_VISION_AVAILABLE = False
    print("⚠️ GPT-4 Vision not available. OpenAI API key required for visual analysis.")

# Import feedback system
try:
    from feedback_system import FeedbackSystem
    FEEDBACK_AVAILABLE = True
except ImportError:
    FEEDBACK_AVAILABLE = False
    print("⚠️ Feedback system not available.")

@dataclass
class JiraTicket:
    """Represents a Jira ticket with extracted information."""
    ticket_id: str
    title: str
    description: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    status: Optional[str] = None
    labels: Optional[List[str]] = None
    components: Optional[List[str]] = None
    figma_links: Optional[List[str]] = None
    pdf_design_paths: Optional[List[str]] = None  # New field for PDF design files
    media_files: Optional[List[str]] = None  # New field for image/video files

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
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.openai_client = None
        self.tech_stack_context = self._load_tech_stack_context()
        
        # Initialize integrations
        try:
            from figma_integration import FigmaIntegration
            self.figma_integration = FigmaIntegration()
            print("🎨 Figma integration initialized")
            FIGMA_AVAILABLE = True
        except ImportError as e:
            print(f"⚠️ Figma integration not available: {e}")
            self.figma_integration = None
            FIGMA_AVAILABLE = False
            
        try:
            from pdf_design_analyzer import PDFDesignAnalyzer
            self.pdf_design_analyzer = PDFDesignAnalyzer()
            print("📄 PDF design analyzer initialized")
            PDF_DESIGN_AVAILABLE = True
        except ImportError as e:
            print(f"⚠️ PDF design analyzer not available: {e}")
            self.pdf_design_analyzer = None
            PDF_DESIGN_AVAILABLE = False

        # Initialize ticket storage for knowledge
        try:
            from ticket_storage_system import TicketStorageSystem
            self.ticket_storage = TicketStorageSystem()
            print("🧠 Ticket knowledge system initialized")
            TICKET_KNOWLEDGE_AVAILABLE = True
        except ImportError as e:
            print(f"⚠️ Ticket knowledge not available: {e}")
            self.ticket_storage = None
            TICKET_KNOWLEDGE_AVAILABLE = False

        # Initialize media analyzer
        try:
            from media_analyzer import MediaAnalyzer
            self.media_analyzer = MediaAnalyzer()
            print("📸 Media analyzer initialized")
            MEDIA_ANALYSIS_AVAILABLE = True
        except ImportError as e:
            print(f"⚠️ Media analyzer not available: {e}")
            self.media_analyzer = None
            MEDIA_ANALYSIS_AVAILABLE = False
            self.feedback_system = FeedbackSystem()
                

        # Initialize feedback system
        try:
            from feedback_system import FeedbackSystem
            self.feedback_system = FeedbackSystem()
            print("📝 Feedback system initialized")
            FEEDBACK_AVAILABLE = True
            
            # Initialize feedback learning system
            if FEEDBACK_LEARNING_AVAILABLE:
                try:
                    self.feedback_learning = FeedbackLearningSystem(self.feedback_system)
                    print("🧠 Feedback Learning System initialized")
                except Exception as e:
                    print(f"⚠️ Feedback learning system initialization failed: {e}")
                    self.feedback_learning = None
            else:
                self.feedback_learning = None
                
        except ImportError as e:
            print(f"⚠️ Feedback system not available: {e}")
            self.feedback_system = None
            self.feedback_learning = None
            FEEDBACK_AVAILABLE = False
        # Initialize GPT-4 Vision analyzer

        # Initialize smart routing system
        if SMART_ROUTING_AVAILABLE:
            try:
                self.smart_routing = SmartRoutingSystem()
                print("🎯 Smart routing system initialized")
            except Exception as e:
                print(f"⚠️ Smart routing system initialization failed: {e}")
                self.smart_routing = None
        else:
            self.smart_routing = None

        if GPT4_VISION_AVAILABLE:
            try:
                self.vision_analyzer = GPT4VisionAnalyzer()
                print("🤖 GPT-4 Vision analyzer initialized")
            except Exception as e:
                print(f"⚠️ GPT-4 Vision analyzer initialization failed: {e}")
                self.vision_analyzer = None
        else:
            self.vision_analyzer = None
        
        self._initialize_openai()
        
        print("🔧 Tech stack context loaded")
        
        self.figma_patterns = [
            r"https://www.figma.com/design/[a-zA-Z0-9]+[^\s]*",
            r"https://figma.com/design/[a-zA-Z0-9]+[^\s]*",
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
        figma_links = ticket_data.get("figma_links_list", []) or self.extract_figma_links(all_text)
        
        # Get PDF design paths if provided
        pdf_design_paths = ticket_data.get('pdf_design_files', [])
        
        # Handle both nested (Jira API) and flat (manual entry) data structures
        priority = ticket_data.get('priority', '')
        if isinstance(priority, dict):
            priority = priority.get('name', '')
        
        assignee = ticket_data.get('assignee', '')
        if isinstance(assignee, dict):
            assignee = assignee.get('displayName', '')
        
        reporter = ticket_data.get('reporter', '')
        if isinstance(reporter, dict):
            reporter = reporter.get('displayName', '')
        
        status = ticket_data.get('status', '')
        if isinstance(status, dict):
            status = status.get('name', '')
        
        # Handle components - can be list of strings or list of dicts
        components = ticket_data.get('components', [])
        if components and isinstance(components[0], dict):
            components = [c.get('name', '') for c in components]
        
        return JiraTicket(
            ticket_id=ticket_data.get('key', ''),
            title=ticket_data.get('summary', ticket_data.get('title', '')),
            description=description,
            figma_links=figma_links,
            priority=priority,
            assignee=assignee,
            reporter=reporter,
            status=status,
            labels=ticket_data.get('labels', []),
            components=components,
            pdf_design_paths=pdf_design_paths
        )
    
    def analyze_ticket_content(self, ticket: JiraTicket) -> AnalysisResult:
        """Analyze ticket content and generate questions and suggestions."""
        
        # Basic content analysis
        analysis = self._analyze_content(ticket)
        
        # Analyze Figma designs if present
        figma_context = None
        if ticket.figma_links and self.figma_integration:
            print(f"🎨 Analyzing {len(ticket.figma_links)} Figma design(s)...")
            figma_context = self._analyze_figma_designs(ticket.figma_links)
            
            # Enhance analysis with Figma context
            if figma_context:
                analysis['figma_designs'] = figma_context
                # Add type checking to prevent 'str' object has no attribute 'get' error
                analysis['has_complex_design'] = any(
                    design.get('complexity_score', 0) > 6 
                    for design in figma_context 
                    if isinstance(design, dict)
                )
                analysis['total_screens'] = sum(
                    len(design.get('screens', [])) 
                    for design in figma_context 
                    if isinstance(design, dict)
                )
                analysis['ui_components_count'] = sum(
                    len(design.get('ui_components', [])) 
                    for design in figma_context 
                    if isinstance(design, dict)
                )
        
        # Analyze PDF designs if present
        pdf_context = None
        if ticket.pdf_design_paths and self.pdf_design_analyzer:
            print(f"📄 Analyzing {len(ticket.pdf_design_paths)} PDF design(s)...")
            pdf_context = self._analyze_pdf_designs(ticket.pdf_design_paths)
            
            # Enhance analysis with PDF context
            if pdf_context:
                analysis['pdf_designs'] = pdf_context
                # Add type checking to prevent 'str' object has no attribute 'get' error
                analysis['has_complex_pdf'] = any(
                    design.get('complexity_score', 0) > 6 
                    for design in pdf_context 
                    if isinstance(design, dict)
                )
                analysis['total_pdf_pages'] = sum(
                    len(design.get('pages', [])) 
                    for design in pdf_context 
                    if isinstance(design, dict)
                )
                analysis['ui_components_count_pdf'] = sum(
                    len(design.get('ui_components', [])) 
                    for design in pdf_context 
                    if isinstance(design, dict)
                )
        
        # Analyze media files if present
        media_context = None
        if ticket.media_files and self.media_analyzer:
            print(f"📸 Analyzing {len(ticket.media_files)} media file(s)...")
            media_context = self._analyze_media_files(ticket.media_files)
            
            # Enhance analysis with media context
            if media_context:
                analysis['media_files'] = media_context
                analysis['has_complex_media'] = any(
                    media.get('complexity_score', 0) > 6 
                    for media in media_context 
                    if isinstance(media, dict)
                )
                analysis['total_media_elements'] = sum(
                    len(media.get('ui_elements', [])) 
                    for media in media_context 
                    if isinstance(media, dict)
                )
                analysis['extracted_text_from_media'] = ' '.join(
                    media.get('extracted_text', '') 
                    for media in media_context 
                    if isinstance(media, dict)
                )
        
        # Get relevant ticket knowledge
        ticket_knowledge = self._get_relevant_ticket_knowledge(ticket)
        analysis = self._enhance_analysis_with_ticket_knowledge(analysis, ticket_knowledge)
        
        # Get Figma design knowledge from past tickets
        figma_knowledge = self._get_figma_design_knowledge(ticket)
        analysis = self._enhance_analysis_with_figma_knowledge(analysis, figma_knowledge, ticket)

        # Generate questions with enhanced context
        questions = self._generate_questions(ticket, analysis)
        clarifications = self._generate_clarifications(ticket, analysis)
        tech_considerations = self._generate_technical_considerations(ticket, analysis)
        design_questions = self._generate_design_questions(ticket, analysis)
        business_questions = self._generate_business_questions(ticket, analysis)
        risks = self._generate_risk_areas(ticket, analysis)
        test_cases = self._generate_test_cases(ticket, analysis)
        
        return AnalysisResult(
            ticket=ticket,
            suggested_questions=questions,
            clarifications_needed=clarifications,
            technical_considerations=tech_considerations,
            design_questions=design_questions,
            business_questions=business_questions,
            risk_areas=risks,
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
    
    def _get_feedback_learning_context(self, detected_topics: List[str]) -> str:
        """Get feedback-driven improvements for question generation."""
        if not self.feedback_learning:
            return ""
        
        try:
            return self.feedback_learning.generate_enhanced_prompt_context(detected_topics)
        except Exception as e:
            print(f"⚠️ Error getting feedback learning context: {e}")
            return ""
    
    def _generate_questions(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate clarifying questions based on ticket content and knowledge."""
        questions = []
        
        # Get confluence context for domain-specific questions
        confluence_context = ""
        detected_topics = []
        if hasattr(self, '_confluence_context') and self._confluence_context.get('relevant_documents'):
            relevant_docs = self._confluence_context['relevant_documents']
            detected_topics = self._confluence_context.get('detected_topics', [])
            tech_stack = []
            features = []
            business_rules = []
            
            for doc in relevant_docs:
                tech_stack.extend(doc.get('tech_stack', []))
                features.extend(doc.get('features', []))
                business_rules.extend(doc.get('business_rules', []))
            
            # Build topic-aware context
            topic_context = f"Detected Topics: {', '.join(detected_topics)}" if detected_topics and detected_topics != ['general'] else "General feature development"
            
            confluence_context = f"""
            
            Topic-Specific Context:
            - {topic_context}
            - Filtered Documents: {len(relevant_docs)} documents relevant to these topics
            - Tech Stack: {', '.join(set(tech_stack[:10]))}
            - Key Features: {', '.join(set(features[:5]))}
            - Business Rules: {', '.join(set(business_rules[:3]))}
            
            Domain: Financial Advisory Platform (Habitto)
            """
        
        # Get ticket knowledge context
        ticket_knowledge_context = ""
        if analysis.get('ticket_knowledge') and analysis['ticket_knowledge'].get('relevant_tickets'):
            knowledge = analysis['ticket_knowledge']
            ticket_knowledge_context = f"""
            
            Knowledge from Similar Past Tickets:
            - {len(knowledge['relevant_tickets'])} similar tickets found in knowledge base
            - Common question patterns: {', '.join(knowledge.get('question_patterns', [])[:3])}
            - Common risk areas: {', '.join(knowledge.get('risk_patterns', [])[:2])}
            - Insights: {', '.join(knowledge.get('insights', [])[:2])}
            """

        # Get Figma design knowledge context
        figma_design_knowledge_context = ""
        if analysis.get('figma_knowledge') and analysis['figma_knowledge'].get('design_patterns'):
            figma_knowledge = analysis['figma_knowledge']
            figma_design_knowledge_context = f"""
            
            Figma Design Knowledge from Past Tickets:
            - {len(figma_knowledge['design_patterns'])} Figma design patterns analyzed
            - Total Figma tickets in knowledge base: {figma_knowledge.get('total_figma_tickets', 0)}
            - Design insights: {', '.join(figma_knowledge.get('figma_insights', [])[:3])}
            - Common components: {', '.join(figma_knowledge.get('component_patterns', [])[:5])}
            - Predicted complexity: {analysis.get('predicted_design_complexity', 'Unknown')} questions
            - Complexity level: {analysis.get('design_complexity_level', 'Unknown')}
            """

        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": f"""You are a senior software architect and business analyst specializing in financial advisory platforms. Generate specific, actionable clarifying questions for this Jira ticket.
                            
                            IMPORTANT: This ticket is specifically about {', '.join(detected_topics) if detected_topics and detected_topics != ['general'] else 'general feature development'}. 
                            Focus your questions ONLY on this topic area and avoid generic or unrelated questions.
                            
                            Focus on:
                - Technical implementation details specific to {', '.join(detected_topics) if detected_topics and detected_topics != ['general'] else 'the feature'}
                            - Business requirements clarity for this specific functionality
                            - Integration points with existing {', '.join(detected_topics) if detected_topics and detected_topics != ['general'] else 'systems'}
                - User experience considerations for {', '.join(detected_topics) if detected_topics and detected_topics != ['general'] else 'the feature'}
                            - Risk mitigation specific to this domain
                            
                            Context: {confluence_context}
                            {ticket_knowledge_context}
                            {figma_design_knowledge_context}
                            
                            {self._get_feedback_learning_context(detected_topics) if self.feedback_learning else ''}
                            
                            Generate 8-12 specific questions that are directly relevant to implementing this {', '.join(detected_topics) if detected_topics and detected_topics != ['general'] else 'feature'} correctly."""
                        },
                        {
                            "role": "user",
                            "content": f"""
                            Ticket: {ticket.title}
                            Description: {ticket.description}
                            Priority: {ticket.priority}
                            Components: {', '.join(ticket.components)}
                            
                            Analysis Context:
                            - Figma Links: {len(ticket.figma_links) if ticket.figma_links else 0}
                            - Media Files: {len(analysis.get('media_files', []))} uploaded images/videos
                            - Has Mobile Elements: {analysis.get('has_mobile', False)}
                            - Has API Integration: {analysis.get('has_integration', False)}
                            - Complexity Indicators: {analysis.get('complexity_indicators', [])}
                            
                            Media Analysis (if available):
                            {self._get_media_context_for_questions(analysis)}
                            """
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                # Extract questions from numbered list
                questions = [q.strip() for q in content.split('\n') if q.strip() and any(q.strip().startswith(f"{i}.") for i in range(1, 21))]
                # Clean up numbered prefixes
                questions = [q.split('.', 1)[1].strip() if '.' in q else q for q in questions]
            
            except Exception as e:
                print(f"⚠️ AI question generation failed: {e}")
                questions = self._get_basic_questions(ticket, analysis)
        else:
            questions = self._get_basic_questions(ticket, analysis)
        
        return questions[:12]

    def _get_basic_questions(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Fallback to basic questions if AI fails or is not available."""
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
        
    def _generate_business_questions(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate business questions based on ticket analysis."""
        # AI-powered business questions
        if self.openai_client:
            try:
                # Build Confluence context if available
                confluence_context = ""
                detected_topics = []
                if hasattr(self, '_confluence_context') and self._confluence_context:
                    ctx = self._confluence_context
                    detected_topics = ctx.get('detected_topics', [])
                    topic_focus = ', '.join(detected_topics).title() if detected_topics and detected_topics != ['general'] else "General Feature Development"
                    
                    confluence_context = f"""
                
                Topic-Specific Knowledge Base Context:
                - Topic Focus: {topic_focus}
                - Available Documents: {len(ctx.get('relevant_documents', []))} (filtered for {topic_focus})
                - Key Business Rules: {len([rule for doc in ctx.get('relevant_documents', []) for rule in doc.get('business_rules', [])])} rules identified
                - Domain: Financial Advisory Platform (Habitto)
                """
                    
                    # Include specific business rules from documents
                    all_business_rules = []
                    for doc in ctx.get('relevant_documents', [])[:2]:
                        all_business_rules.extend(doc.get('business_rules', [])[:3])
                    
                    if all_business_rules:
                        confluence_context += f"""
                
                Relevant Business Rules from Documentation:
                """
                        for i, rule in enumerate(all_business_rules[:5], 1):
                            confluence_context += f"\n{i}. {rule[:100]}{'...' if len(rule) > 100 else ''}"
                
                topic_specific_focus = f"This ticket is specifically about {', '.join(detected_topics)} functionality" if detected_topics and detected_topics != ['general'] else "This is a general feature request"
                
                prompt = f"""You are a product manager for a financial advisory platform analyzing a feature request. Generate specific business questions that address strategic, operational, and value-related concerns.
                
                IMPORTANT: {topic_specific_focus}. Focus your business questions specifically on this domain and avoid generic questions.
                
                Ticket Details:
                - Title: {ticket.title}
                - Description: {ticket.description}
                - Priority: {ticket.priority}
                - Labels: {", ".join(ticket.labels or [])}
                - Components: {", ".join(ticket.components or [])}
                - Has Figma: {analysis.get("figma_count", 0) > 0}
                - Has Mobile: {analysis.get("has_mobile", False)}
                - Has Integration: {analysis.get("has_integration", False)}
                - Has Performance: {analysis.get("has_performance", False)}
                - Has Accessibility: {analysis.get("has_accessibility", False)}
                - Has PDF: {analysis.get("pdf_designs", [])}
                {confluence_context}
                
                Generate 12-15 specific business questions focusing on:
                
                **Financial Services Context:**
                - Revenue impact and monetization opportunities
                - Client acquisition and retention effects
                - Advisor productivity and efficiency gains
                - Compliance and regulatory considerations
                - Risk management and mitigation
                
                **Strategic Business Questions:**
                - Market differentiation and competitive advantage
                - Scalability and operational impact
                - Resource requirements and ROI
                - Integration with existing business processes
                - Success metrics and measurement criteria
                
                Consider the business rules and context from the knowledge base. Make questions specific to financial advisory services, appointment management, and client relationship workflows.
                
                Return only questions, one per line, numbered 1-15."""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                ai_questions = response.choices[0].message.content.strip().split("\n")
                # Clean up questions and remove numbering
                cleaned_questions = []
                for q in ai_questions:
                    q = q.strip()
                    if q:
                        # Remove numbering (1., 2., etc.)
                        q = re.sub(r'^\d+\.\s*', '', q)
                        if q:
                            cleaned_questions.append(q)
                
                return cleaned_questions[:15]
            
            except Exception as e:
                print(f"AI business question generation failed: {e}")
        
        # Fallback business questions
        return self._get_basic_business_questions(ticket, analysis)

    def _get_basic_business_questions(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Fallback to basic business questions if AI fails or is not available."""
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
        # AI-powered test case generation
        if self.openai_client:
            try:
                # Build Confluence context if available
                confluence_context = ""
                if hasattr(self, '_confluence_context') and self._confluence_context:
                    ctx = self._confluence_context
                    confluence_context = f"""
                
                System Context from Knowledge Base:
                - Integration Points: {len([tech for doc in ctx.get('relevant_documents', []) for tech in doc.get('tech_stack', []) if 'api' in tech.lower() or 'integration' in tech.lower()])} identified
                - Key Technologies: {', '.join(ctx.get('knowledge_base_summary', {}).get('tech_stack', [])[:5])}
                - Business Rules: {len([rule for doc in ctx.get('relevant_documents', []) for rule in doc.get('business_rules', [])])} rules to validate
                """
                    
                    # Include specific components that might need testing
                    all_components = []
                    for doc in ctx.get('relevant_documents', [])[:2]:
                        all_components.extend(doc.get('components', [])[:5])
                    
                    if all_components:
                        confluence_context += f"""
                
                Related System Components to Test:
                {', '.join(list(set(all_components))[:8])}
                """
                
                prompt = f"""You are a QA engineer creating comprehensive test cases for a financial advisory platform feature. Generate specific, actionable test cases based on the ticket content and system context.

                Ticket Details:
                - Title: {ticket.title}
                - Description: {ticket.description}
                - Priority: {ticket.priority}
                - Labels: {", ".join(ticket.labels or [])}
                - Components: {", ".join(ticket.components or [])}
                - Has Figma: {analysis.get("figma_count", 0) > 0}
                - Has Mobile: {analysis.get("has_mobile", False)}
                - Has Integration: {analysis.get("has_integration", False)}
                - Has PDF: {analysis.get("pdf_designs", [])}
                - Media Files: {len(analysis.get('media_files', []))} uploaded
                {confluence_context}
                
                Media Analysis Context:
                {self._get_media_context_for_questions(analysis)}
                
                Generate 20-25 specific test cases organized in these categories:
                
                **Functional Tests (8-10 tests):**
                - Core feature functionality validation
                - User workflow and journey testing
                - Integration with existing financial advisory features
                - Business rule validation from knowledge base
                
                **Security & Compliance Tests (4-5 tests):**
                - Data protection and privacy validation
                - Financial services compliance requirements
                - User authentication and authorization
                - Audit trail and logging verification
                
                **Performance & Reliability Tests (4-5 tests):**
                - Response time and load testing
                - System stability under stress
                - Error handling and recovery
                - Data consistency and integrity
                
                **User Experience Tests (4-5 tests):**
                - Accessibility compliance (WCAG)
                - Cross-browser and device compatibility
                - User interface responsiveness
                - Error message clarity and helpfulness
                
                Make test cases specific to financial advisory workflows, appointment scheduling, and client management contexts. Reference system components and business rules from the knowledge base when relevant.
                
                Format: Return test cases as bullet points with clear test objectives and expected outcomes."""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,
                    temperature=0.6
                )
                
                ai_test_cases = response.choices[0].message.content.strip().split("\n")
                # Clean up test cases
                cleaned_test_cases = []
                for tc in ai_test_cases:
                    tc = tc.strip()
                    if tc and len(tc) > 10:  # Filter out empty or very short lines
                        cleaned_test_cases.append(tc)
                
                return cleaned_test_cases[:25]
            
            except Exception as e:
                print(f"AI test case generation failed: {e}")
        
        # Fallback to basic test cases
        return self._get_basic_test_cases(ticket, analysis)
    
    def _get_basic_test_cases(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Fallback to basic test cases if AI fails or is not available."""
        test_cases = []
        content_lower = f"{ticket.title} {ticket.description}".lower()
        
        test_cases.extend([
            "**Functional Tests:**",
            "• Verify the main feature works as described in acceptance criteria",
            "• Verify user can complete the primary user journey successfully",
            "• Verify feature integrates with existing authentication system",
            "• Verify feature respects user permissions and access controls",
            "• Verify data validation and business rule enforcement",
        ])
        
        test_cases.extend([
            "**Security & Compliance Tests:**",
            "• Verify data encryption in transit and at rest",
            "• Verify audit logging for financial advisory compliance",
            "• Verify user session management and timeout handling",
        ])
        
        # Performance
        test_cases.extend([
            "**Performance Tests:**",
        "• Verify feature responds within acceptable time limits (2-3 seconds)",
        "• Verify feature handles expected concurrent user load",
        ])
        
        return test_cases[:25]
    
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

    def _generate_design_questions(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate design-specific questions for the ticket."""
        questions = []
        
        # Extract keywords once at the beginning
        ticket_keywords = self._extract_relevant_keywords(ticket)
        
        # Enhanced Figma design questions using AI with actual design context
        if analysis.get("figma_designs"):
            design_context = ""
            for design in analysis["figma_designs"]:
                # Add type checking to prevent 'str' object has no attribute 'get' error
                if not isinstance(design, dict):
                    continue
                    
                design_name = design.get('design_name', 'Unknown Design')
                screens = design.get('screens', [])
                components = design.get('ui_components', [])
                complexity = design.get('design_complexity', 0)
                user_flows = design.get('user_flows', [])
                
                # Get detailed screen information if available
                screen_details = design.get('screen_details', [])
                detailed_screens = []
                if screen_details:
                    for screen in screen_details:
                        if isinstance(screen, dict):
                            screen_name = screen.get('name', 'Unknown Screen')
                            screen_description = screen.get('description', '')
                            form_fields = screen.get('form_fields', [])
                            ctas = screen.get('ctas', [])
                            
                            detailed_screens.append(f"""
                            Screen: {screen_name}
                            Description: {screen_description}
                            Form Fields: {', '.join([f.get('label', f.get('placeholder', 'Field')) for f in form_fields[:5]])}
                            CTAs: {', '.join([f.get('text', 'Button') for f in ctas[:3]])}
                            """)
                
                # Filter screens and components based on ticket relevance
                relevant_screens = self._filter_relevant_items(screens, ticket_keywords)
                relevant_components = self._filter_relevant_items(components, ticket_keywords)
                
                # Japanese content context
                japanese_context = ""
                if design.get('has_japanese_content'):
                    japanese_screens = design.get('japanese_screens', [])
                    japanese_ratio = design.get('japanese_ratio', 0)
                    japanese_ui_elements = design.get('japanese_ui_elements', {})
                    
                    japanese_context = f"""
                    
                    🇯🇵 JAPANESE CONTENT DETECTED:
                    - Japanese text ratio: {japanese_ratio:.1%}
                    - Japanese screens: {', '.join(japanese_screens[:5])}
                    - Japanese buttons: {', '.join(japanese_ui_elements.get('japanese_buttons', [])[:3])}
                    - Japanese navigation: {', '.join(japanese_ui_elements.get('japanese_navigation', [])[:3])}
                    - Japanese labels: {', '.join(japanese_ui_elements.get('japanese_labels', [])[:3])}
                    
                    IMPORTANT: This design contains Japanese text. Consider localization, text expansion, and Japanese UI patterns when generating questions.
                    """
                
                design_context += f"""
                
                Figma Design: "{design_name}" (Complexity: {complexity:.1f}/10)
                - Relevant Screens: {', '.join(relevant_screens[:8]) if relevant_screens else 'No specific screens identified'}
                - Relevant UI Components: {', '.join(relevant_components[:12]) if relevant_components else 'General UI components'}
                - User Flows: {', '.join(user_flows)}
                - Total Components in Design: {len(components)}
                - Total Screens in Design: {len(screens)}
                {japanese_context}
                
                Detailed Screen Information:
                {''.join(detailed_screens[:3]) if detailed_screens else 'No detailed screen information available'}
                
                Note: Focus specifically on components and screens related to: {', '.join(ticket_keywords)}
                                """
            
            # Always try to generate questions, with fallback
            try:
                if self.openai_client and design_context.strip():
                    response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a senior UX/UI designer and React Native developer with expertise in Japanese localization. Generate highly specific design questions based ONLY on the exact ticket requirements provided.

CRITICAL REQUIREMENTS:
                    1. Read the ticket title and description carefully
2. Generate questions ONLY about the specific feature mentioned in the ticket
3. DO NOT ask about random screens or components from the Figma file
4. Focus on the exact UI elements needed for this specific feature
5. If it's about profile editing, ask ONLY about profile editing screens/forms
6. If it's about dropdowns, ask about dropdown design patterns
7. If no relevant screens are found in Figma, generate implementation questions for the specific feature

JAPANESE CONTENT CONSIDERATIONS:
                    - If Japanese text is detected in the design, include questions about text expansion/contraction
- Consider Japanese typography, character support, and input methods
- Ask about localization strategy for Japanese vs English content
- Consider Japanese UI patterns and user expectations

Generate 6-8 targeted questions about implementing THIS SPECIFIC FEATURE."""
                            },
                            {
                                "role": "user", 
                                "content": f"""
TICKET TO ANALYZE:
                    Title: {ticket.title}
Description: {ticket.description}

SPECIFIC FEATURE TO FOCUS ON: 
                    {ticket.title}

REQUIREMENTS FROM DESCRIPTION:
                    {ticket.description}

MEDIA ANALYSIS (if provided):
    {self._get_media_context_for_questions(analysis)}

FIGMA SCREEN INTERACTIONS (if available):
    {self._get_figma_interaction_context(analysis)}

GPT-4 VISUAL ANALYSIS (if available):
    {self._get_visual_context_for_questions(analysis)}

FEEDBACK-DRIVEN IMPROVEMENTS (if available):
    {self._get_feedback_learning_context(['design']) if self.feedback_learning else ''}

Generate design questions that are DIRECTLY related to implementing this specific feature: "{ticket.title}"

Focus on:
    - UI components needed for this exact feature
- User interaction patterns for this specific functionality  
- Navigation flows and button behaviors from Figma screens
- Success/error states and screen transitions
- Back button functionality and navigation hierarchy
- Form submission flows and validation feedback
- Design system considerations for this feature
- Implementation details based on uploaded images/videos (if any)
- Implementation details for this exact requirement
- Accessibility for this specific feature

DO NOT ask about:
    - Random screens from the Figma file
- Unrelated features or components
- General app design questions

Example good questions for UI interactions and navigation:
    - Where should the "Back" button navigate when pressed?
- What should happen when the user taps the "Submit" button?
- How should the success screen be designed after form submission?
- Where should the "Next" button lead in the user flow?
- What validation feedback should appear for each form field?
- How should error states be displayed on this screen?
- What loading states should be shown during submission?
- How should the navigation hierarchy work between screens?

Example good questions for "Enable Editing of Occupation, Country of Residence":
    - How should the occupation dropdown be designed and positioned in the profile form?
- What validation states should be shown for country selection?
- How should the save/update flow work for these specific fields?
- Where should the back button navigate from the profile editing screen?
- What should happen when the user successfully updates their information?

Generate similar targeted questions for: {ticket.title}

IMPORTANT: Based on the Figma screens and buttons detected above, ask specific questions about:
    1. Button navigation destinations
2. Success/error screen flows  
3. Back button behavior
4. Form submission outcomes
5. Screen transition animations
6. Loading and feedback states
                                """
                            }
                        ],
                        max_tokens=800,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                # Extract questions from numbered list
                ai_questions = [q.strip() for q in content.split('\n') if q.strip() and any(q.strip().startswith(f"{i}.") for i in range(1, 21))]
                # Clean up numbered prefixes
                ai_questions = [q.split('.', 1)[1].strip() if '.' in q else q for q in ai_questions]
                questions.extend(ai_questions)
                
                # If AI didn't generate enough questions, add fallback
                if len(questions) < 3:
                    questions.extend(self._get_basic_design_questions_from_figma(analysis))
                
                print(f"✅ AI generated {len(questions)} design questions")
            
            except Exception as e:
                print(f"⚠️ AI design question generation failed: {e}")
                # Fallback to basic questions if AI fails
                questions = self._get_basic_design_questions_from_figma(analysis)
        else:
            # No Figma designs, use basic questions
            questions = self._get_basic_design_questions()
        
        # Ensure we always have some questions - make them specific to the ticket
        if not questions:
            # Generate contextual fallback questions based on ticket content
            ticket_context = f"{ticket.title} {ticket.description}".lower()
            
            # Specific question templates based on ticket type
            if any(term in ticket_context for term in ['edit', 'update', 'modify', 'change']):
                questions = [
                    f"How should the editing interface be designed for {ticket.title.lower()}?",
                    f"What validation states are needed for the {ticket.title.lower()} feature?",
                    f"How should the save/update flow work for {ticket.title.lower()}?",
                    f"What are the form field requirements for {ticket.title.lower()}?",
                    f"How should error handling be displayed for {ticket.title.lower()}?",
                    f"What accessibility considerations are needed for {ticket.title.lower()}?"
                ]
            elif any(term in ticket_context for term in ['dropdown', 'select', 'picker']):
                questions = [
                    f"How should the dropdown/picker be styled for {ticket.title.lower()}?",
                    f"What are the selection states and animations needed?",
                    f"How should the dropdown options be organized and displayed?",
                    f"What search/filter functionality is needed in the dropdown?",
                    f"How should the selected value be displayed?",
                    f"What accessibility features are needed for the dropdown?"
                ]
            elif any(term in ticket_context for term in ['profile', 'user', 'account']):
                questions = [
                    f"How should the profile section be organized for {ticket.title.lower()}?",
                    f"What form layout works best for profile editing?",
                    f"How should profile changes be saved and confirmed?",
                    f"What validation is needed for profile fields?",
                    f"How should the profile update success state be shown?",
                    f"What accessibility considerations are needed for profile editing?"
                ]
            else:
                # Generic but still contextual
                questions = [
                    f"What are the specific UI components needed for {ticket.title.lower()}?",
                    f"How should the user flow be designed for {ticket.title.lower()}?",
                    f"What validation and error states are needed for {ticket.title.lower()}?",
                    f"How should the success state be displayed for {ticket.title.lower()}?",
                    f"What responsive design considerations are needed for {ticket.title.lower()}?",
                    f"What accessibility features should be implemented for {ticket.title.lower()}?"
                ]
        
        return questions
    def _extract_relevant_keywords(self, ticket: JiraTicket) -> List[str]:
        """Extract relevant keywords from ticket to filter Figma content."""
        content = f"{ticket.title} {ticket.description}".lower()
        
        # Common UI/UX keywords
        keywords = []
        
        # Extract specific feature keywords
        feature_patterns = [
            'rating', 'prompt', 'review', 'session', 'login', 'auth', 'payment', 
            'dashboard', 'profile', 'chat', 'assistant', 'ai', 'intro', 'welcome',
            'form', 'button', 'modal', 'dialog', 'notification', 'alert',
            'navigation', 'menu', 'screen', 'page', 'flow', 'consent', 'permission'
        ]
        
        for pattern in feature_patterns:
            if pattern in content:
                keywords.append(pattern)
        
        # If no specific keywords found, use general terms
        if not keywords:
            keywords = ['screen', 'component', 'interface', 'design']
        
        return keywords[:8]  # Limit to avoid too broad filtering
    
    def _filter_relevant_items(self, items: List[str], keywords: List[str]) -> List[str]:
        """Filter screens/components based on relevance to keywords."""
        if not keywords or not items:
            return items[:5]  # Return first 5 if no filtering possible
        
        relevant_items = []
        
        # First pass: exact keyword matches
        for item in items:
            item_lower = item.lower()
            for keyword in keywords:
                if keyword in item_lower:
                    relevant_items.append(item)
                    break
        
        # If no exact matches, look for partial matches or return general items
        if not relevant_items:
            # Second pass: partial matches with common UI terms
            ui_terms = ['screen', 'button', 'form', 'nav', 'menu', 'modal', 'dialog']
            for item in items:
                item_lower = item.lower()
                for term in ui_terms:
                    if term in item_lower:
                        relevant_items.append(item)
                        break
                if len(relevant_items) >= 8:
                    break
        
        # If still no matches, return the first few items
        if not relevant_items:
            relevant_items = items[:5]
        
        return relevant_items[:8]  # Limit to 8 most relevant items
    
    def _get_basic_design_questions(self) -> List[str]:
        """Generate basic design questions when no Figma context is available."""
        return [
            "What are the specific UI components needed for this feature?",
            "How should the user interface be structured for this functionality?",
            "What are the design system requirements for this feature?",
            "How should the user flow be designed for this functionality?",
            "What responsive design considerations are needed?",
            "What accessibility features should be implemented?",
            "How should the visual hierarchy be established?",
            "What interaction patterns should be used?"
        ]
    
    def _get_basic_design_questions_from_figma(self, analysis: Dict) -> List[str]:
        """Generate basic design questions from Figma analysis when AI is unavailable."""
        questions = []
        
        if analysis.get("figma_designs"):
            for design in analysis["figma_designs"]:
                # Add type checking to prevent 'str' object has no attribute 'get' error
                if not isinstance(design, dict):
                    continue
                    
                design_name = design.get('design_name', 'Unknown Design')
                screens = design.get('screens', [])
                components = design.get('ui_components', [])
                
                # Ask about specific screens
                for screen in screens[:3]:
                    questions.append(f"What are the specific interaction patterns for the '{screen}' shown in the Figma design?")
                
                # Ask about specific components
                for component in components[:3]:
                    questions.append(f"How should the '{component}' component be implemented based on the Figma specifications?")
                
                # General design questions
                questions.extend([
                    f"What are the design system requirements for the {design_name} based on the Figma file?",
                    f"How should the {len(screens)} screens be connected in the user flow?",
                    f"What responsive design considerations are needed for the {len(components)} components?"
                ])
        
        return questions

    def _identify_technical_considerations(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Identify technical considerations based on ticket analysis."""
        # AI-powered technical considerations
        if self.openai_client:
            try:
                prompt = f"""You are a senior software engineer analyzing a Jira ticket. Generate specific, actionable technical considerations based on this ticket content.
                
                Ticket Details:
                - Title: {ticket.title}
                - Description: {ticket.description}
                - Priority: {ticket.priority}
                - Labels: {", ".join(ticket.labels or [])}
                - Components: {", ".join(ticket.components or [])}
                - Has Figma: {analysis.get("figma_count", 0) > 0}
                - Has Mobile: {analysis.get("has_mobile", False)}
                - Has Integration: {analysis.get("has_integration", False)}
                - Has Performance: {analysis.get("has_performance", False)}
                - Has Accessibility: {analysis.get("has_accessibility", False)}
                
                Generate 10-15 specific technical considerations for implementing this feature. Focus on:
                - Architecture and design patterns
                - Performance optimization
                - Security considerations
                - Scalability and reliability
                - Database design
                - API design
                - Error handling
                - Monitoring and logging
                
                Make considerations specific to this ticket content, not generic. Return only considerations, one per line."""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a senior software architect. Generate technical considerations for implementation."
                            },
                            {
                                "role": "user", 
                                "content": f"Ticket: {ticket.title}\nDescription: {ticket.description}"
                            }
                        ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                ai_considerations = response.choices[0].message.content.strip().split("\n")
                return [c.strip() for c in ai_considerations if c.strip()][:15]
            
            except Exception as e:
                print(f"AI technical consideration generation failed: {e}")
        
        # Fallback to hardcoded if AI fails
        return ["Consider performance requirements", "Consider security implications", "Consider scalability needs"]

    def _identify_clarifications(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Identify areas needing clarification based on ticket analysis."""
        # AI-powered clarifications
        if self.openai_client:
            try:
                prompt = f"""You are a project manager analyzing a Jira ticket. Generate specific, actionable clarifications needed based on this ticket content.
                
                Ticket Details:
                - Title: {ticket.title}
                - Description: {ticket.description}
                - Priority: {ticket.priority}
                - Labels: {", ".join(ticket.labels or [])}
                - Components: {", ".join(ticket.components or [])}
                - Has Figma: {analysis.get("figma_count", 0) > 0}
                - Has Mobile: {analysis.get("has_mobile", False)}
                - Has Integration: {analysis.get("has_integration", False)}
                - Has Performance: {analysis.get("has_performance", False)}
                - Has Accessibility: {analysis.get("has_accessibility", False)}
                
                Generate 10-15 specific clarifications that stakeholders should ask about this feature. Focus on:
                - Requirements clarification
                - Scope definition
                - Success criteria
                - Dependencies and blockers
                - Resource requirements
                - Timeline considerations
                - Risk mitigation
                - Acceptance criteria
                
                Make clarifications specific to this ticket content, not generic. Return only clarifications, one per line."""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a senior software architect. Generate technical considerations for implementation."
                            },
                            {
                                "role": "user", 
                                "content": f"Ticket: {ticket.title}\nDescription: {ticket.description}"
                            }
                        ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                ai_clarifications = response.choices[0].message.content.strip().split("\n")
                return [c.strip() for c in ai_clarifications if c.strip()][:15]
            
            except Exception as e:
                print(f"AI clarification generation failed: {e}")
        
        # Fallback to hardcoded if AI fails
        return ["Clarify the exact requirements", "Clarify the success criteria", "Clarify the timeline"]
    def _analyze_figma_design(self, figma_url: str) -> Dict[str, any]:
        """Analyze Figma design to extract implementation context and existing features."""
        try:
            # Extract design ID and node ID from URL
            design_id = self._extract_figma_design_id(figma_url)
            node_id = self._extract_figma_node_id(figma_url)
            
            if not design_id:
                return {"error": "Could not extract design ID from URL"}
            
            # Simulate Figma API analysis (in real implementation, you would call Figma API)
            design_analysis = self._simulate_figma_analysis(design_id, node_id, figma_url)
            
            return design_analysis
            
        except Exception as e:
            print(f"Figma design analysis failed: {e}")
            return {"error": str(e)}

    def _extract_figma_design_id(self, url: str) -> Optional[str]:
        """Extract design ID from Figma URL."""
        try:
            # Pattern: https://www.figma.com/design/DESIGN_ID/...
            match = re.search(r"figma.com/design/([a-zA-Z0-9]+)", url)
            return match.group(1) if match else None
        except:
            return None

    def _extract_figma_node_id(self, url: str) -> Optional[str]:
        """Extract node ID from Figma URL."""
        try:
            # Pattern: ...?node-id=NODE_ID&...
            match = re.search(r"node-id=([a-zA-Z0-9-]+)", url)
            return match.group(1) if match else None
        except:
            return None

    def _simulate_figma_analysis(self, design_id: str, node_id: Optional[str], url: str) -> Dict[str, any]:
        """Simulate Figma design analysis using AI to understand design content."""
        if not self.openai_client:
            return {"error": "OpenAI client not available"}
        
        try:
            # Create a prompt to analyze the Figma design based on URL and context
            prompt = f"""You are a UI/UX design analyst. Analyze this Figma design URL and provide insights about the design content and implementation context.
            
            Figma URL: {url}
            Design ID: {design_id}
            Node ID: {node_id}
            
            Based on the URL structure and common design patterns, analyze what this design likely contains and provide:
            
            1. DESIGN_CONTEXT: What type of feature/screen this design represents
            2. EXISTING_FEATURES: What features appear to already be implemented based on the design
            3. NEW_FEATURES: What new features or changes are being proposed
            4. DESIGN_COMPLEXITY: Simple/Medium/Complex
            5. UI_COMPONENTS: List of UI components likely present
            6. USER_FLOW: Expected user interaction flow
            7. TECHNICAL_REQUIREMENTS: Technical considerations for implementation
            8. DESIGN_SYSTEM_USAGE: How design system components are used
            9. RESPONSIVE_CONSIDERATIONS: Mobile/tablet/desktop considerations
            10. ACCESSIBILITY_FEATURES: Accessibility considerations visible in design
            
            Return your analysis in a structured format that can be used to generate better questions and test cases.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Analyze the Figma design"}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse the AI response into structured data
            return self._parse_figma_analysis(analysis_text, design_id, node_id, url)
            
        except Exception as e:
            print(f"Figma analysis simulation failed: {e}")
            return {"error": str(e)}

    def _parse_figma_analysis(self, analysis_text: str, design_id: str, node_id: Optional[str], url: str) -> Dict[str, any]:
        """Parse AI analysis into structured data."""
        try:
            # Extract key information from the analysis text
            lines = analysis_text.split("\n")
            
            result = {
                "design_id": design_id,
                "node_id": node_id,
                "url": url,
                "design_context": "",
                "existing_features": [],
                "new_features": [],
                "design_complexity": "Medium",
                "ui_components": [],
                "user_flow": "",
                "technical_requirements": [],
                "design_system_usage": "",
                "responsive_considerations": [],
                "accessibility_features": []
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "DESIGN_CONTEXT:" in line:
                    current_section = "design_context"
                    result[current_section] = line.split(":", 1)[1].strip()
                elif "EXISTING_FEATURES:" in line:
                    current_section = "existing_features"
                    result[current_section] = [item.strip() for item in line.split(":", 1)[1].split(",") if item.strip()]
                elif "NEW_FEATURES:" in line:
                    current_section = "new_features"
                    result[current_section] = [item.strip() for item in line.split(":", 1)[1].split(",") if item.strip()]
                elif "DESIGN_COMPLEXITY:" in line:
                    current_section = "design_complexity"
                    result[current_section] = line.split(":", 1)[1].strip()
                elif "UI_COMPONENTS:" in line:
                    current_section = "ui_components"
                    result[current_section] = [item.strip() for item in line.split(":", 1)[1].split(",") if item.strip()]
                elif "USER_FLOW:" in line:
                    current_section = "user_flow"
                    result[current_section] = line.split(":", 1)[1].strip()
                elif "TECHNICAL_REQUIREMENTS:" in line:
                    current_section = "technical_requirements"
                    result[current_section] = [item.strip() for item in line.split(":", 1)[1].split(",") if item.strip()]
                elif "DESIGN_SYSTEM_USAGE:" in line:
                    current_section = "design_system_usage"
                    result[current_section] = line.split(":", 1)[1].strip()
                elif "RESPONSIVE_CONSIDERATIONS:" in line:
                    current_section = "responsive_considerations"
                    result[current_section] = [item.strip() for item in line.split(":", 1)[1].split(",") if item.strip()]
                elif "ACCESSIBILITY_FEATURES:" in line:
                    current_section = "accessibility_features"
                    result[current_section] = [item.strip() for item in line.split(":", 1)[1].split(",") if item.strip()]
                elif current_section and current_section in result:
                    if isinstance(result[current_section], list):
                        result[current_section].append(line)
                    else:
                        result[current_section] += " " + line
            
            return result
            
        except Exception as e:
            print(f"Figma analysis parsing failed: {e}")
            return {"error": str(e)}

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load config: {e}")
        return {}
    
    def _initialize_openai(self):
        """Initialize OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=api_key)
                print("✅ OpenAI client initialized")
            except ImportError:
                print("⚠️ OpenAI library not installed. AI features disabled.")
                self.openai_client = None
        else:
            self.openai_client = None
            print("⚠️ OpenAI API key not found. AI features disabled.")
    
    def _load_tech_stack_context(self) -> Dict:
        """Load tech stack context from file."""
        try:
            tech_stack_file = "habitto_tech_stack.json"
            if os.path.exists(tech_stack_file):
                with open(tech_stack_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load tech stack: {e}")
        return {}

    def _load_tech_stack(self) -> Dict:
        """Load Habitto tech stack information from a JSON file."""
        try:
            with open("habitto_tech_stack.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ habitto_tech_stack.json not found. Using default tech stack.")
            return {"app_name": "the app"}
        except Exception as e:
            print(f"Failed to load tech stack: {e}")
            return {"app_name": "the app"}

    def _analyze_content(self, ticket: JiraTicket) -> Dict:
        """Analyze ticket content for keywords and context."""
        content = f"{ticket.title} {ticket.description}".lower()
        
        analysis = {
            "priority_level": ticket.priority or "Medium",
            "figma_count": len(ticket.figma_links),
            "has_mobile": any(keyword in content for keyword in ['mobile', 'ios', 'android', 'app', 'react native']),
            "has_integration": any(keyword in content for keyword in ['api', 'integration', 'connect', 'sync', 'webhook']),
            "has_performance": any(keyword in content for keyword in ['performance', 'speed', 'optimization', 'cache', 'load']),
            "has_accessibility": any(keyword in content for keyword in ['accessibility', 'a11y', 'screen reader', 'wcag']),
            "has_security": any(keyword in content for keyword in ['security', 'authentication', 'authorization', 'compliance']),
            "has_database": any(keyword in content for keyword in ['database', 'data', 'storage', 'persistence']),
            "has_ui_ux": any(keyword in content for keyword in ['design', 'ui', 'ux', 'interface', 'user experience']),
            "complexity_indicators": self._assess_complexity_indicators(content),
        }
        
        return analysis
    
    def _assess_complexity_indicators(self, content: str) -> List[str]:
        """Assess complexity indicators from ticket content."""
        indicators = []
        
        if any(word in content for word in ['multiple', 'several', 'various', 'complex']):
            indicators.append("Multiple components involved")
        
        if any(word in content for word in ['integration', 'connect', 'sync']):
            indicators.append("System integration required")
        
        if any(word in content for word in ['new', 'create', 'build', 'develop']):
            indicators.append("New development work")
        
        if any(word in content for word in ['refactor', 'redesign', 'rebuild']):
            indicators.append("Significant refactoring needed")
        
        return indicators

    def _analyze_pdf_designs(self, pdf_paths: List[str]) -> List[Dict]:
        """Analyze PDF design files from the provided paths."""
        pdf_designs = []
        
        for pdf_path in pdf_paths:
            try:
                print(f"   📄 Processing: {pdf_path}")
                pdf_analysis = self.pdf_design_analyzer.analyze_pdf_design(pdf_path)
                
                if pdf_analysis:
                    pdf_context = self.pdf_design_analyzer.get_design_context_for_analysis(pdf_analysis)
                    # Rename keys to match expected format
                    pdf_context['pdf_name'] = pdf_context['design_name']
                    pdf_context['pdf_complexity'] = pdf_context['design_complexity']
                    pdf_context['pages'] = [f"Page {i+1}" for i in range(pdf_context['pages_count'])]
                    
                    pdf_designs.append(pdf_context)
                    print(f"   ✅ PDF analyzed: {pdf_context['pdf_name']}")
                    print(f"      📄 Pages: {pdf_context['pages_count']}")
                    print(f"      🧩 Components: {len(pdf_context['ui_components'])}")
                    print(f"      📱 Screens: {len(pdf_context['screens'])}")
                    print(f"      🎨 Type: {pdf_context['design_type']}")
                    print(f"      ⚡ Complexity: {pdf_context['pdf_complexity']:.1f}/10")
                else:
                    print(f"   ❌ Failed to analyze PDF: {pdf_path}")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing PDF design: {e}")
                continue
        
        return pdf_designs
    
    def _analyze_figma_designs(self, figma_links: List[str]) -> List[Dict]:
        """Analyze Figma designs from the provided links."""
        figma_designs = []
        
        for figma_url in figma_links:
            try:
                print(f"   📥 Processing: {figma_url}")
                design = self.figma_integration.analyze_figma_design(figma_url)
                
                if design:
                    design_context = self.figma_integration.get_design_context_for_analysis(design)
                    figma_designs.append(design_context)
                    print(f"   ✅ Design analyzed: {design_context['design_name']}")
                    print(f"      📱 Screens: {len(design_context['screens'])}")
                    print(f"      🧩 Components: {design_context['components_count']}")
                    print(f"      ⚡ Complexity: {design_context['design_complexity']:.1f}/10")
                else:
                    print(f"   ❌ Failed to analyze design from: {figma_url}")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing Figma design: {e}")
                continue
        
        return figma_designs
    
    def _generate_clarifications(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate clarifications needed for the ticket."""
        clarifications = []
        
        # Basic clarifications based on content analysis
        if analysis.get("has_integration"):
            clarifications.append("Which external systems need to be integrated?")
            clarifications.append("What are the API requirements and data formats?")
        
        if analysis.get("has_mobile"):
            clarifications.append("Should this work on both iOS and Android?")
            clarifications.append("Are there specific mobile design guidelines to follow?")
        
        if analysis.get("has_performance"):
            clarifications.append("What are the specific performance requirements?")
            clarifications.append("Are there load testing requirements?")
        
        if len(ticket.figma_links or []) > 0:
            clarifications.append("Are the Figma designs final or still in review?")
            clarifications.append("Should the implementation match the designs exactly?")
        
        if analysis.get("pdf_designs"):
            clarifications.append("Are these PDF designs the final specifications?")
            clarifications.append("Do the PDF wireframes need visual design before implementation?")
        
        # Priority-based clarifications
        if ticket.priority in ["High", "Critical"]:
            clarifications.append("What is the target delivery date?")
            clarifications.append("Are there any dependencies blocking this work?")
        
        return clarifications[:10]  # Limit to top 10
    
    def _generate_technical_considerations(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate technical considerations for the ticket."""
        considerations = []
        
        # Database considerations
        if analysis.get("has_database"):
            considerations.append("Database schema changes may be required")
            considerations.append("Consider data migration strategy")
        
        # Security considerations
        if analysis.get("has_security"):
            considerations.append("Security review required for authentication/authorization")
            considerations.append("Compliance requirements need verification")
        
        # Performance considerations
        if analysis.get("has_performance"):
            considerations.append("Performance testing and optimization needed")
            considerations.append("Caching strategy should be evaluated")
        
        # Integration considerations
        if analysis.get("has_integration"):
            considerations.append("API versioning and backward compatibility")
            considerations.append("Error handling for external service failures")
        
        # Mobile considerations
        if analysis.get("has_mobile"):
            considerations.append("React Native platform-specific implementations")
            considerations.append("App store deployment considerations")
        
        # Design complexity considerations
        if analysis.get("figma_designs"):
            for design in analysis["figma_designs"]:
                # Add type checking to prevent 'str' object has no attribute 'get' error
                if not isinstance(design, dict):
                    continue
                    
                if design.get("design_complexity", 0) > 7:
                    considerations.append(f"High complexity design ({design.get('design_name', 'Unknown')}) may require additional development time")
        
        if analysis.get("pdf_designs"):
            for pdf in analysis["pdf_designs"]:
                if pdf.get("design_type") == "wireframes":
                    considerations.append(f"PDF wireframes ({pdf['pdf_name']}) need visual design before implementation")
        
        return considerations[:8]  # Limit to top 8
    

    
    def _generate_risk_areas(self, ticket: JiraTicket, analysis: Dict) -> List[str]:
        """Generate potential risk areas for the ticket."""
        risks = []
        
        # Complexity risks
        complexity_indicators = analysis.get("complexity_indicators", [])
        if len(complexity_indicators) > 2:
            risks.append("High complexity - multiple components and integrations involved")
        
        # Design risks
        if analysis.get("figma_designs"):
            for design in analysis["figma_designs"]:
                # Add type checking to prevent 'str' object has no attribute 'get' error
                if not isinstance(design, dict):
                    continue
                    
                if design.get("design_complexity", 0) > 8:
                    risks.append(f"Very complex design ({design.get('design_name', 'Unknown')}) may exceed estimated effort")
        
        if analysis.get("pdf_designs"):
            wireframe_count = sum(1 for pdf in analysis["pdf_designs"] if isinstance(pdf, dict) and pdf.get("design_type") == "wireframes")
            if wireframe_count > 0:
                risks.append("Wireframe-only designs may require additional design phase")
        
        # Technical risks
        if analysis.get("has_integration"):
            risks.append("External API dependencies could cause delays")
        
        if analysis.get("has_performance"):
            risks.append("Performance requirements may need additional optimization time")
        
        if analysis.get("has_security"):
            risks.append("Security review and compliance verification required")
        
        # Priority risks
        if ticket.priority in ["High", "Critical"]:
            risks.append("High priority ticket - tight timeline may impact quality")
        
        # Mobile risks
        if analysis.get("has_mobile"):
            risks.append("Cross-platform compatibility testing required")
            risks.append("App store approval process may add timeline risk")
        
        # Data risks
        if analysis.get("has_database"):
            risks.append("Database changes may require careful migration planning")
        
        return risks[:8]  # Limit to top 8

    def _get_relevant_ticket_knowledge(self, ticket: JiraTicket) -> Dict[str, Any]:
        """Get relevant knowledge from previously stored tickets."""
        if not hasattr(self, 'ticket_storage') or not self.ticket_storage:
            return {'relevant_tickets': [], 'insights': []}
        
        try:
            # Search for similar tickets
            search_query = f"{ticket.title} {ticket.description}"
            similar_tickets = self.ticket_storage.search_tickets(search_query, limit=5)
            
            # Get statistics for patterns
            stats = self.ticket_storage.get_statistics()
            
            # Extract insights from similar tickets
            insights = []
            question_patterns = set()
            risk_patterns = set()
                        
            for stored_ticket in similar_tickets:
                # Add type checking to prevent 'str' object has no attribute 'get' error
                if not isinstance(stored_ticket, dict):
                    continue
                
                # Get full ticket details to access analysis data
                ticket_id = stored_ticket.get('ticket_id')
                if ticket_id:
                    full_ticket = self.ticket_storage.get_ticket(ticket_id)
                    if full_ticket and isinstance(full_ticket, dict):
                        # Add unique question patterns from analysis
                        analysis = full_ticket.get('analysis', {})
                        if isinstance(analysis, dict):
                            for q in analysis.get('suggested_questions', [])[:3]:
                                if isinstance(q, str) and len(q) > 20:  # Avoid very short questions
                                    question_patterns.add(q)

                            # Add unique risk patterns  
                            for r in analysis.get('risk_areas', [])[:2]:
                                if isinstance(r, str) and len(r) > 15:  # Avoid very short risks
                                    risk_patterns.add(r)
            
            # Generate insights
            if similar_tickets:
                insights.append(f"Found {len(similar_tickets)} similar tickets in knowledge base")
                
                # Common question themes
                if question_patterns:
                    insights.append(f"Common question themes from past tickets: {', '.join(list(question_patterns)[:2])}")
                
                # Common risk areas
                if risk_patterns:
                    insights.append(f"Common risks from similar tickets: {', '.join(list(risk_patterns)[:2])}")
            
            return {
                'relevant_tickets': similar_tickets[:3],  # Top 3 most relevant
                'insights': insights,
                'total_stored_tickets': stats.get('total_tickets', 0),
                'question_patterns': list(question_patterns)[:5],
                'risk_patterns': list(risk_patterns)[:3]
            }
            
        except Exception as e:
            print(f"⚠️ Could not retrieve ticket knowledge: {e}")
            return {'relevant_tickets': [], 'insights': []}

    def _enhance_analysis_with_ticket_knowledge(self, analysis: Dict, ticket_knowledge: Dict) -> Dict:
        """Enhance analysis with insights from stored tickets."""
        if not ticket_knowledge or not ticket_knowledge.get('relevant_tickets'):
            return analysis
        
        # Add ticket knowledge to analysis context
        analysis['ticket_knowledge'] = ticket_knowledge
        analysis['has_similar_tickets'] = len(ticket_knowledge['relevant_tickets']) > 0
        analysis['knowledge_insights'] = ticket_knowledge.get('insights', [])
        
        # Enhance complexity assessment based on similar tickets
        similar_tickets = ticket_knowledge['relevant_tickets']
        if similar_tickets:
            avg_questions = sum(t.get('question_count', 0) for t in similar_tickets) / len(similar_tickets)
            if avg_questions > 50:
                analysis['predicted_complexity'] = 'High'
            elif avg_questions > 30:
                analysis['predicted_complexity'] = 'Medium'
            else:
                analysis['predicted_complexity'] = 'Low'
        
        return analysis

    def _get_figma_design_knowledge(self, ticket: JiraTicket) -> Dict[str, Any]:
        """Get design knowledge from stored tickets and implemented features knowledge base."""
        knowledge_data = {
            'design_patterns': [],
            'figma_insights': [],
            'implementation_notes': [],
            'component_patterns': [],
            'total_figma_tickets': 0
        }
        
        # 1. Get knowledge from stored tickets with Figma links
        if hasattr(self, 'ticket_storage') and self.ticket_storage:
            try:
                figma_tickets = self.ticket_storage.search_figma_tickets(limit=20)
                
                complexity_patterns = []
                component_patterns = set()
                implementation_notes = set()
                
                for stored_ticket in figma_tickets:
                    if isinstance(stored_ticket, dict):
                        # Get full ticket details
                        ticket_id = stored_ticket.get('ticket_id')
                        if ticket_id:
                            full_ticket = self.ticket_storage.get_ticket(ticket_id)
                            if full_ticket and isinstance(full_ticket, dict):
                                analysis = full_ticket.get('analysis', {})
                                if isinstance(analysis, dict):
                                    figma_designs = analysis.get('figma_designs', [])
                                    if figma_designs and len(figma_designs) > 0:
                                        question_count = len(analysis.get('suggested_questions', []))
                                        if question_count > 0:
                                            complexity_patterns.append({
                                                'figma_count': len(figma_designs),
                                                'question_count': question_count,
                                                'test_case_count': len(analysis.get('test_cases', [])),
                                                'title': full_ticket.get('title', ''),
                                                'components': analysis.get('components', [])
                                            })
                                        
                                        # Get design questions
                                        for question in analysis.get('design_questions', [])[:3]:
                                            if isinstance(question, str) and ('figma' in question.lower() or 'design' in question.lower()):
                                                implementation_notes.add(question)
                                        
                                        # Get components
                                        for comp in analysis.get('components', []):
                                            if comp and isinstance(comp, str):
                                                component_patterns.add(comp)
                
                knowledge_data['design_patterns'].extend(complexity_patterns)
                knowledge_data['component_patterns'].extend(list(component_patterns))
                knowledge_data['implementation_notes'].extend(list(implementation_notes))
                knowledge_data['total_figma_tickets'] = len(figma_tickets)
                
            except Exception as e:
                print(f"⚠️ Could not retrieve ticket-based Figma knowledge: {e}")
        
        # 2. Get knowledge from implemented features knowledge base
        try:
            from pathlib import Path
            import json
            
            knowledge_file = Path("knowledge_base") / "figma_knowledge.json"
            if knowledge_file.exists():
                with open(knowledge_file, 'r') as f:
                    implemented_features = json.load(f)
                
                if implemented_features:
                    # Analyze implemented features for patterns
                    feature_insights = []
                    complexity_mapping = {'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}
                    
                    # Group by complexity
                    by_complexity = {}
                    for feature in implemented_features:
                        complexity = feature.get('complexity_rating', 'Medium')
                        if complexity not in by_complexity:
                            by_complexity[complexity] = []
                        by_complexity[complexity].append(feature)
                    
                    # Generate insights from implemented features
                    for complexity, features in by_complexity.items():
                        avg_dev_time = sum(f.get('development_time', 0) for f in features) / len(features)
                        avg_team_size = sum(f.get('team_size', 0) for f in features) / len(features)
                        
                        if features:
                            feature_insights.append(f"{complexity} complexity features: avg {avg_dev_time:.1f} days, {avg_team_size:.1f} team size")
                    
                    # Most complex implemented feature
                    most_complex = max(implemented_features, key=lambda x: complexity_mapping.get(x.get('complexity_rating', 'Low'), 1))
                    feature_insights.append(f"Most complex implemented: '{most_complex['feature_name']}' ({most_complex['complexity_rating']})")
                    
                    # Technology patterns
                    all_techs = []
                    for feature in implemented_features:
                        all_techs.extend(feature.get('technology_stack', []))
                    
                    tech_counts = {}
                    for tech in all_techs:
                        tech_counts[tech] = tech_counts.get(tech, 0) + 1
                    
                    common_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    if common_techs:
                        feature_insights.append(f"Common technologies: {', '.join([tech for tech, _ in common_techs])}")
                    
                    # Extract implementation patterns
                    implementation_patterns = []
                    for feature in implemented_features:
                        if feature.get('figma_analysis'):
                            analysis = feature['figma_analysis']
                            implementation_patterns.append({
                                'feature_name': feature['feature_name'],
                                'complexity_rating': feature['complexity_rating'],
                                'development_time': feature['development_time'],
                                'team_size': feature['team_size'],
                                'total_screens': analysis.get('total_screens', 0),
                                'total_components': analysis.get('total_components', 0),
                                'complexity_score': analysis.get('complexity_score', 0),
                                'technology_stack': feature.get('technology_stack', [])
                            })
                    
                    # Update knowledge data with implemented features insights
                    knowledge_data['figma_insights'].extend(feature_insights)
                    knowledge_data['design_patterns'].extend(implementation_patterns[:10])
                    knowledge_data['total_implemented_features'] = len(implemented_features)
                    
                    # Extract unique components from implemented features
                    all_components = set()
                    for feature in implemented_features:
                        if feature.get('figma_analysis', {}).get('components'):
                            all_components.update(feature['figma_analysis']['components'][:5])
                    
                    knowledge_data['component_patterns'].extend(list(all_components)[:8])
                    
        except Exception as e:
            print(f"⚠️ Could not retrieve implemented features knowledge: {e}")
        
        # Generate combined insights
        if knowledge_data['design_patterns']:
            total_patterns = len(knowledge_data['design_patterns'])
            knowledge_data['figma_insights'].insert(0, f"Total design patterns analyzed: {total_patterns}")
        
        return knowledge_data

    def _enhance_analysis_with_figma_knowledge(self, analysis: Dict, figma_knowledge: Dict, ticket: JiraTicket) -> Dict:
        """Enhance analysis with Figma design knowledge from past tickets."""
        if not figma_knowledge or not figma_knowledge.get('design_patterns'):
            return analysis
        
        # Add Figma knowledge to analysis context
        analysis['figma_knowledge'] = figma_knowledge
        analysis['has_figma_knowledge'] = len(figma_knowledge['design_patterns']) > 0
        
        # Predict complexity based on Figma design patterns
        if ticket.figma_links and figma_knowledge['design_patterns']:
            figma_count = len(ticket.figma_links)
            
            # Find similar patterns - only check ticket patterns that have figma_count
            similar_patterns = [
                p for p in figma_knowledge['design_patterns'] 
                if 'figma_count' in p and p['figma_count'] == figma_count
            ]
            
            # Also consider implementation patterns for additional insights
            implementation_patterns = [
                p for p in figma_knowledge['design_patterns']
                if 'feature_name' in p  # This identifies implementation patterns
            ]
            
            if similar_patterns:
                avg_complexity = sum(p['question_count'] for p in similar_patterns) / len(similar_patterns)
                analysis['predicted_design_complexity'] = avg_complexity
                
                # Add design insights based on ticket patterns
                if avg_complexity > 45:
                    analysis['design_complexity_level'] = 'High'
                    analysis['design_recommendations'] = [
                        'Consider breaking down into multiple phases',
                        'Plan for extensive design system integration',
                        'Allocate extra time for component testing'
                    ]
                elif avg_complexity > 25:
                    analysis['design_complexity_level'] = 'Medium'
                    analysis['design_recommendations'] = [
                        'Ensure design consistency across components',
                        'Plan for component reusability',
                        'Consider performance implications'
                    ]
                else:
                    analysis['design_complexity_level'] = 'Low'
                    analysis['design_recommendations'] = [
                        'Focus on clean, simple implementation',
                        'Leverage existing design patterns'
                    ]
            
            # Add insights from implementation patterns
            if implementation_patterns:
                # Find complex implementations for comparison
                high_complexity_impl = [p for p in implementation_patterns if p.get('complexity_rating') in ['High', 'Very High']]
                if high_complexity_impl:
                    avg_dev_time = sum(p.get('development_time', 0) for p in high_complexity_impl) / len(high_complexity_impl)
                    analysis['similar_implementation_time'] = f"Similar complex features took {avg_dev_time:.1f} days on average"
                    
                # Extract common technologies from implementations
                all_techs = []
                for impl in implementation_patterns:
                    all_techs.extend(impl.get('technology_stack', []))
                
                if all_techs:
                    from collections import Counter
                    common_techs = Counter(all_techs).most_common(3)
                    analysis['recommended_technologies'] = [tech for tech, _ in common_techs]
        
        return analysis

    def _get_media_context_for_questions(self, analysis: Dict) -> str:
        """Extract media analysis context for AI question generation."""
        if not analysis.get('media_files'):
            return "No media files provided."
        
        media_files = analysis['media_files']
        context_parts = []
        
        # Summarize media analysis
        image_count = sum(1 for m in media_files if isinstance(m, dict) and m.get('media_type') == 'image')
        video_count = sum(1 for m in media_files if isinstance(m, dict) and m.get('media_type') == 'video')
        
        if image_count > 0:
            context_parts.append(f"- {image_count} image(s) analyzed (screenshots, mockups, wireframes)")
        if video_count > 0:
            context_parts.append(f"- {video_count} video(s) analyzed (demos, walkthroughs)")
        
        # Extract key insights from media
        all_ui_elements = []
        all_design_elements = []
        all_user_actions = []
        extracted_text_parts = []
        content_types = []
        
        for media in media_files:
            if isinstance(media, dict):
                all_ui_elements.extend(media.get('ui_elements', []))
                all_design_elements.extend(media.get('design_elements', []))
                all_user_actions.extend(media.get('user_actions', []))
                
                text = media.get('extracted_text', '').strip()
                if text:
                    extracted_text_parts.append(text[:100] + '...' if len(text) > 100 else text)
                
                content_type = media.get('content_type', '')
                if content_type:
                    content_types.append(content_type)
        
        # Deduplicate and summarize
        unique_ui_elements = list(set(all_ui_elements))
        unique_design_elements = list(set(all_design_elements))
        unique_user_actions = list(set(all_user_actions))
        unique_content_types = list(set(content_types))
        
        if unique_ui_elements:
            context_parts.append(f"- UI Elements detected: {', '.join(unique_ui_elements[:5])}")
        if unique_design_elements:
            context_parts.append(f"- Design elements: {', '.join(unique_design_elements[:5])}")
        if unique_user_actions:
            context_parts.append(f"- User actions identified: {', '.join(unique_user_actions[:5])}")
        if unique_content_types:
            context_parts.append(f"- Content types: {', '.join(unique_content_types)}")
        if extracted_text_parts:
            context_parts.append(f"- Text from media: {' | '.join(extracted_text_parts[:2])}")
        
        return '\n'.join(context_parts) if context_parts else "Media files uploaded but analysis pending."

    def _get_figma_interaction_context(self, analysis: Dict) -> str:
        """Extract Figma screen interaction context for detailed UI questions."""
        if not analysis.get('figma_designs'):
            return "No Figma designs available."
        
        figma_designs = analysis['figma_designs']
        interaction_parts = []
        
        all_screens = []
        all_navigation = []
        all_buttons = []
        all_forms = []
        
        # Collect interaction elements from all Figma designs
        for design in figma_designs:
            if isinstance(design, dict) and design.get('screen_details'):
                for screen in design['screen_details']:
                    if isinstance(screen, dict):
                        screen_name = screen.get('screen_name', 'Unknown Screen')
                        all_screens.append(screen_name)
                        
                        # Navigation elements
                        navigation = screen.get('navigation', [])
                        for nav in navigation:
                            if isinstance(nav, dict):
                                nav_text = nav.get('text', nav.get('name', ''))
                                if nav_text:
                                    all_navigation.append(f"{screen_name}: {nav_text}")
                        
                        # CTAs/Buttons
                        ctas = screen.get('ctas', [])
                        for cta in ctas:
                            if isinstance(cta, dict):
                                cta_text = cta.get('text', cta.get('name', ''))
                                cta_type = cta.get('type', 'button')
                                if cta_text:
                                    all_buttons.append(f"{screen_name}: {cta_text} ({cta_type})")
                        
                        # Form fields
                        form_fields = screen.get('form_fields', [])
                        if form_fields:
                            field_names = [f.get('label', f.get('name', '')) for f in form_fields if isinstance(f, dict)]
                            if field_names:
                                all_forms.append(f"{screen_name}: {', '.join(filter(None, field_names))}")
        
        # Generate interaction context
        if all_screens:
            interaction_parts.append(f"Screens detected: {', '.join(all_screens[:5])}")
        
        if all_navigation:
            interaction_parts.append(f"Navigation elements found:")
            for nav in all_navigation[:3]:
                interaction_parts.append(f"  - {nav}")
        
        if all_buttons:
            interaction_parts.append(f"Buttons/CTAs found:")
            for btn in all_buttons[:3]:
                interaction_parts.append(f"  - {btn}")
        
        if all_forms:
            interaction_parts.append(f"Form fields found:")
            for form in all_forms[:2]:
                interaction_parts.append(f"  - {form}")
        
        # Add specific interaction questions context
        if all_navigation or all_buttons:
            interaction_parts.append("\nKey interaction questions to consider:")
            if any('back' in nav.lower() for nav in all_navigation):
                interaction_parts.append("- Back button navigation behavior")
            if any('next' in btn.lower() or 'continue' in btn.lower() for btn in all_buttons):
                interaction_parts.append("- Forward navigation flow")
            if any('submit' in btn.lower() or 'save' in btn.lower() for btn in all_buttons):
                interaction_parts.append("- Form submission and success states")
            if any('login' in btn.lower() or 'sign' in btn.lower() for btn in all_buttons):
                interaction_parts.append("- Authentication flow and error handling")
        
        return '\n'.join(interaction_parts) if interaction_parts else "No specific UI interactions detected in Figma screens."

    def _analyze_media_files(self, media_files: List[str]) -> List[Dict[str, Any]]:
        """Analyze media files (images/videos) for UI insights."""
        if not self.media_analyzer:
            return []
        
        media_analyses = []
        
        for media_file in media_files:
            try:
                print(f"📸 Processing media file: {media_file}")
                
                # Analyze the media file
                analysis = self.media_analyzer.analyze_media_file(media_file)
                
                if analysis:
                    # Convert to dict for JSON serialization
                    media_context = self.media_analyzer.get_analysis_context(analysis)
                    media_context.update({
                        'filename': analysis.filename,
                        'media_id': analysis.media_id,
                        'analysis_date': analysis.analysis_date
                    })
                    
                    media_analyses.append(media_context)
                    print(f"✅ Media analysis complete: {analysis.content_type} ({analysis.media_type})")
                else:
                    print(f"⚠️ Could not analyze media file: {media_file}")
                    
            except Exception as e:
                print(f"❌ Error analyzing media file {media_file}: {e}")
                continue
        
        return media_analyses

    def analyze_ticket_with_media(
        self, 
        ticket_data: Dict[str, str], 
        media_files: List[str] = None
    ) -> AnalysisResult:
        """Analyze a ticket with optional media files."""
        # Parse the ticket data
        ticket = self.parse_jira_ticket(ticket_data)
        
        # Add media files to the ticket
        if media_files:
            ticket.media_files = media_files
        
        # Perform the analysis
        return self.analyze_ticket_content(ticket)

    def analyze_visual_content(self, image_path: str, ticket: JiraTicket = None) -> Optional[VisualAnalysisResult]:
        """Analyze visual content (screenshots, mockups) using GPT-4 Vision."""
        if not self.vision_analyzer:
            print("⚠️ GPT-4 Vision analyzer not available")
            return None
        
        # Prepare context from ticket if available
        context = {}
        if ticket:
            context = {
                'ticket_title': ticket.title,
                'ticket_description': ticket.description,
                'ticket_priority': ticket.priority,
                'focus_areas': [ticket.title.lower()]  # Simple focus extraction
            }
        
        print(f"🤖 Analyzing visual content with GPT-4 Vision: {image_path}")
        
        # Determine analysis type based on filename or context
        if 'figma' in image_path.lower() or 'design' in image_path.lower():
            return self.vision_analyzer.analyze_figma_screenshot(image_path, context)
        else:
            return self.vision_analyzer.analyze_ui_mockup(image_path, context)
    
    def analyze_ticket_with_visual_content(self, ticket: JiraTicket, analysis: Dict, visual_content_paths: List[str] = None) -> Dict:
        """Enhanced ticket analysis including visual content analysis."""
        enhanced_analysis = analysis.copy()
        
        if not visual_content_paths or not self.vision_analyzer:
            return enhanced_analysis
        
        visual_analyses = []
        
        for image_path in visual_content_paths:
            if os.path.exists(image_path):
                visual_result = self.analyze_visual_content(image_path, ticket)
                if visual_result:
                    visual_analyses.append(visual_result)
                    print(f"✅ Visual analysis completed: {visual_result.design_quality_score:.1f}/10 design quality")
            else:
                print(f"⚠️ Visual content not found: {image_path}")
        
        if visual_analyses:
            # Aggregate visual analysis results
            enhanced_analysis['visual_analyses'] = visual_analyses
            enhanced_analysis['has_visual_analysis'] = True
            enhanced_analysis['total_visual_elements'] = sum(len(va.ui_components_identified) for va in visual_analyses)
            enhanced_analysis['average_design_quality'] = sum(va.design_quality_score for va in visual_analyses) / len(visual_analyses)
            enhanced_analysis['japanese_visual_elements'] = []
            enhanced_analysis['visual_improvement_suggestions'] = []
            
            # Collect Japanese elements and suggestions from all analyses
            for va in visual_analyses:
                enhanced_analysis['japanese_visual_elements'].extend(va.japanese_elements_detected)
                enhanced_analysis['visual_improvement_suggestions'].extend(va.improvement_suggestions)
            
            print(f"📊 Visual analysis summary: {len(visual_analyses)} images analyzed")
            print(f"🎯 Average design quality: {enhanced_analysis['average_design_quality']:.1f}/10")
            print(f"🇯🇵 Japanese elements found: {len(enhanced_analysis['japanese_visual_elements'])}")
        
        return enhanced_analysis
    
    def generate_visual_questions(self, visual_analysis: VisualAnalysisResult, ticket: JiraTicket) -> List[str]:
        """Generate specific questions based on GPT-4 Vision analysis."""
        questions = []
        
        if not visual_analysis:
            return questions
        
        # Questions based on design quality
        if visual_analysis.design_quality_score < 7.0:
                questions.extend([
                f"The design quality score is {visual_analysis.design_quality_score:.1f}/10. What specific improvements should be prioritized?",
                "Are there design system guidelines that should be followed more closely?",
                "What are the client's expectations for visual polish and design consistency?"
            ])
        
        # Questions based on Japanese content
        if visual_analysis.japanese_elements_detected:
            questions.extend([
                f"The design contains {len(visual_analysis.japanese_elements_detected)} Japanese elements. Are these translations final?",
                "Should the Japanese text expand or contract differently than shown in the design?",
                "Are there specific Japanese typography requirements or brand guidelines to follow?",
                "Do the Japanese UI patterns match the target user expectations in Japan?"
            ])
        
        # Questions based on accessibility
        if visual_analysis.accessibility:
            accessibility_issues = visual_analysis.accessibility.get('issues', [])
            if accessibility_issues:
                questions.extend([
                    "Accessibility concerns were identified in the design. What are the accessibility requirements?",
                    "Should the design comply with WCAG AA or AAA standards?",
                    "Are there specific accessibility features required for the target user base?"
                ])
        
        # Questions based on implementation complexity
        if visual_analysis.implementation_complexity == 'high':
            questions.extend([
                "The design appears complex to implement. Are all visual elements essential?",
                "Would the client be open to design simplifications for faster development?",
                "Are there existing components that could be reused instead of custom development?"
            ])
        
        # Questions based on improvement suggestions
        if visual_analysis.improvement_suggestions:
            top_suggestions = visual_analysis.improvement_suggestions[:3]
            for suggestion in top_suggestions:
                questions.append(f"Design improvement suggested: {suggestion}. Should this be addressed?")
        
        return questions[:10]  # Limit to 10 most relevant questions
    
    def _get_visual_context_for_questions(self, analysis: Dict) -> str:
        """Get visual analysis context for AI question generation."""
        if not analysis.get('has_visual_analysis'):
            return ""
        
        visual_analyses = analysis.get('visual_analyses', [])
        if not visual_analyses:
            return ""
        
        context_parts = [
            f"\n📊 VISUAL ANALYSIS RESULTS ({len(visual_analyses)} images analyzed):"
        ]
        
        for i, va in enumerate(visual_analyses):
            context_parts.extend([
                f"\nImage {i+1}:",
                f"• Design Quality: {va.design_quality_score:.1f}/10",
                f"• UI Components: {', '.join(va.ui_components_identified[:5])}" + ("..." if len(va.ui_components_identified) > 5 else ""),
                f"• Implementation Complexity: {va.implementation_complexity}",
                f"• Japanese Elements: {len(va.japanese_elements_detected)} detected"
            ])
            
            if va.improvement_suggestions:
                context_parts.append(f"• Key Improvements: {', '.join(va.improvement_suggestions[:2])}")
        
        context_parts.extend([
            f"\n🎯 Overall Visual Summary:",
            f"• Average Design Quality: {analysis.get('average_design_quality', 0):.1f}/10",
            f"• Total Visual Elements: {analysis.get('total_visual_elements', 0)}",
            f"• Japanese Visual Elements: {len(analysis.get('japanese_visual_elements', []))}"
        ])
        
        return "\n".join(context_parts)

    def get_smart_routing_recommendations(self, ticket_data: Dict) -> Optional[Dict]:
        """Get smart routing recommendations for a ticket."""
        if not self.smart_routing:
            return None
        
        try:
            recommendations = self.smart_routing.get_developer_recommendations(ticket_data)
            return recommendations
        except Exception as e:
            print(f"⚠️ Error getting smart routing recommendations: {e}")
            return None
    
    def get_team_analytics(self) -> Optional[Dict]:
        """Get team analytics and workload distribution."""
        if not self.smart_routing:
            return None
        
        try:
            analytics = self.smart_routing.get_team_analytics()
            return analytics
        except Exception as e:
            print(f"⚠️ Error getting team analytics: {e}")
            return None
    
    def assign_ticket_to_developer(self, ticket_id: str, developer_id: str, skill_match_score: float, workload_impact: str, notes: str = ""):
        """Record a ticket assignment for tracking."""
        if not self.smart_routing:
            return False
        
        try:
            self.smart_routing.record_assignment(ticket_id, developer_id, skill_match_score, workload_impact, notes)
            return True
        except Exception as e:
            print(f"⚠️ Error recording assignment: {e}")
            return False
    
    def record_ticket_completion(self, ticket_id: str, success_rating: float, actual_completion_time: float, notes: str = ""):
        """Record ticket completion for performance tracking."""
        if not self.smart_routing:
            return False
        
        try:
            self.smart_routing.record_completion(ticket_id, success_rating, actual_completion_time, notes)
            return True
        except Exception as e:
            print(f"⚠️ Error recording completion: {e}")
            return False
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
        'comments': [],
        'pdf_design_files': [] # Empty for testing
    }
    
    # Parse and analyze
    ticket = analyzer.parse_jira_ticket(sample_ticket)
    result = analyzer.analyze_ticket_content(ticket)
    
    # Generate report
    report = analyzer.generate_report(result)
    print(report)

if __name__ == "__main__":
    main()
