#!/usr/bin/env python3
"""
Confluence Document Integration System

This system processes Confluence documents to enhance the Jira-Figma Analyzer
with app-specific knowledge and context for better analysis results.
"""

import os
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import pickle
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

@dataclass
class ConfluenceDocument:
    """Represents a processed Confluence document."""
    doc_id: str
    title: str
    content: str
    url: str
    space_key: str
    page_id: str
    created_date: str
    updated_date: str
    author: str
    labels: List[str]
    parent_page: Optional[str]
    
    # Processed content
    extracted_text: str
    headings: List[str]
    code_blocks: List[str]
    links: List[str]
    images: List[str]
    tables: List[Dict]
    
    # Knowledge extraction
    tech_stack_mentions: List[str]
    api_endpoints: List[str]
    component_names: List[str]
    feature_descriptions: List[str]
    business_rules: List[str]
    
    # Metadata
    processing_date: str
    word_count: int
    relevance_score: float

class ConfluenceIntegration:
    """Main class for Confluence document processing and integration."""
    
    def __init__(self, storage_dir: str = "confluence_knowledge"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Storage subdirectories
        self.docs_dir = self.storage_dir / "documents"
        self.processed_dir = self.storage_dir / "processed"
        self.knowledge_dir = self.storage_dir / "knowledge_base"
        self.database_dir = self.storage_dir / "database"
        
        # Create directories
        for directory in [self.docs_dir, self.processed_dir, self.knowledge_dir, self.database_dir]:
            directory.mkdir(exist_ok=True)
        
        # Initialize database
        self.db_path = self.database_dir / "confluence_docs.db"
        self.init_database()
        
        # Knowledge base
        self.knowledge_base = {}
        self.load_knowledge_base()
        
        print("📚 Confluence Integration initialized")
    
    def init_database(self):
        """Initialize SQLite database for Confluence documents."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS confluence_docs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT,
                    space_key TEXT,
                    page_id TEXT,
                    created_date TEXT,
                    updated_date TEXT,
                    author TEXT,
                    processing_date TEXT NOT NULL,
                    word_count INTEGER DEFAULT 0,
                    relevance_score REAL DEFAULT 0.0,
                    file_path TEXT
                )
            ''')
            
            # Document labels
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS doc_labels (
                    doc_id TEXT,
                    label TEXT,
                    FOREIGN KEY (doc_id) REFERENCES confluence_docs (doc_id)
                )
            ''')
            
            # Tech stack mentions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tech_mentions (
                    doc_id TEXT,
                    technology TEXT,
                    mention_count INTEGER DEFAULT 1,
                    FOREIGN KEY (doc_id) REFERENCES confluence_docs (doc_id)
                )
            ''')
            
            # API endpoints
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_endpoints (
                    doc_id TEXT,
                    endpoint TEXT,
                    method TEXT,
                    description TEXT,
                    FOREIGN KEY (doc_id) REFERENCES confluence_docs (doc_id)
                )
            ''')
            
            # Component references
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS component_refs (
                    doc_id TEXT,
                    component_name TEXT,
                    description TEXT,
                    FOREIGN KEY (doc_id) REFERENCES confluence_docs (doc_id)
                )
            ''')
            
            # Feature descriptions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feature_descriptions (
                    doc_id TEXT,
                    feature_name TEXT,
                    description TEXT,
                    priority TEXT,
                    FOREIGN KEY (doc_id) REFERENCES confluence_docs (doc_id)
                )
            ''')
            
            # Business rules
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_rules (
                    doc_id TEXT,
                    rule_text TEXT,
                    category TEXT,
                    FOREIGN KEY (doc_id) REFERENCES confluence_docs (doc_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_docs_title ON confluence_docs (title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_docs_space ON confluence_docs (space_key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_mentions ON tech_mentions (technology)')
            
            conn.commit()
    
    def process_confluence_file(self, file_path: str, metadata: Dict = None) -> str:
        """Process an uploaded Confluence file."""
        try:
            # Determine file type and process accordingly
            if file_path.endswith('.html') or file_path.endswith('.htm'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self._process_html_export(content, metadata)
            elif file_path.endswith('.xml'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self._process_xml_export(content, metadata)
            elif file_path.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self._process_markdown_export(content, metadata)
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self._process_text_export(content, metadata)
            elif file_path.endswith('.pdf'):
                return self._process_pdf_export(file_path, metadata)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing file {file_path}: {e}")
            raise
    
    def _process_html_export(self, content: str, metadata: Dict = None) -> str:
        """Process HTML export from Confluence."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract metadata
        title = self._extract_title(soup, metadata)
        
        # Generate document ID
        doc_id = self._generate_doc_id(title, content)
        
        # Extract content sections
        extracted_text = self._extract_text_content(soup)
        headings = self._extract_headings(soup)
        code_blocks = self._extract_code_blocks(soup)
        links = self._extract_links(soup)
        images = self._extract_images(soup)
        tables = self._extract_tables(soup)
        
        # Extract knowledge
        tech_stack = self._extract_tech_stack_mentions(extracted_text)
        api_endpoints = self._extract_api_endpoints(extracted_text, code_blocks)
        components = self._extract_component_names(extracted_text, headings)
        features = self._extract_feature_descriptions(extracted_text, headings)
        business_rules = self._extract_business_rules(extracted_text)
        
        # Create document object
        doc = ConfluenceDocument(
            doc_id=doc_id,
            title=title,
            content=content,
            url=metadata.get('url', '') if metadata and isinstance(metadata, dict) else '',
            space_key=metadata.get('space_key', '') if metadata and isinstance(metadata, dict) else '',
            page_id=metadata.get('page_id', '') if metadata and isinstance(metadata, dict) else '',
            created_date=metadata.get('created_date', '') if metadata and isinstance(metadata, dict) else '',
            updated_date=metadata.get('updated_date', '') if metadata and isinstance(metadata, dict) else '',
            author=metadata.get('author', '') if metadata and isinstance(metadata, dict) else '',
            labels=metadata.get('labels', []) if metadata and isinstance(metadata, dict) else [],
            parent_page=metadata.get('parent_page', '') if metadata and isinstance(metadata, dict) else '',
            
            extracted_text=extracted_text,
            headings=headings,
            code_blocks=code_blocks,
            links=links,
            images=images,
            tables=tables,
            
            tech_stack_mentions=tech_stack,
            api_endpoints=api_endpoints,
            component_names=components,
            feature_descriptions=features,
            business_rules=business_rules,
            
            processing_date=datetime.now().isoformat(),
            word_count=len(extracted_text.split()),
            relevance_score=self._calculate_relevance_score(extracted_text, tech_stack, components)
        )
        
        # Store document
        self._store_document(doc)
        
        # Update knowledge base
        self._update_knowledge_base(doc)
        
        return doc_id
    
    def _process_markdown_export(self, content: str, metadata: Dict = None) -> str:
        """Process Markdown export."""
        # Extract title from first heading or metadata
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else metadata.get('title', 'Untitled') if metadata and isinstance(metadata, dict) else 'Untitled'
        
        doc_id = self._generate_doc_id(title, content)
        
        # Extract sections
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        # Clean text
        clean_text = re.sub(r'```[\w]*\n.*?\n```', '', content, flags=re.DOTALL)
        clean_text = re.sub(r'[#*`\[\]()]', '', clean_text)
        
        # Extract knowledge
        tech_stack = self._extract_tech_stack_mentions(clean_text)
        api_endpoints = self._extract_api_endpoints(clean_text, code_blocks)
        components = self._extract_component_names(clean_text, headings)
        features = self._extract_feature_descriptions(clean_text, headings)
        business_rules = self._extract_business_rules(clean_text)
        
        doc = ConfluenceDocument(
            doc_id=doc_id,
            title=title,
            content=content,
            url=metadata.get('url', '') if metadata and isinstance(metadata, dict) else '',
            space_key=metadata.get('space_key', '') if metadata and isinstance(metadata, dict) else '',
            page_id=metadata.get('page_id', '') if metadata and isinstance(metadata, dict) else '',
            created_date=metadata.get('created_date', '') if metadata and isinstance(metadata, dict) else '',
            updated_date=metadata.get('updated_date', '') if metadata and isinstance(metadata, dict) else '',
            author=metadata.get('author', '') if metadata and isinstance(metadata, dict) else '',
            labels=metadata.get('labels', []) if metadata and isinstance(metadata, dict) else [],
            parent_page=metadata.get('parent_page', '') if metadata and isinstance(metadata, dict) else '',
            
            extracted_text=clean_text,
            headings=headings,
            code_blocks=code_blocks,
            links=[link[1] for link in links],
            images=[],
            tables=[],
            
            tech_stack_mentions=tech_stack,
            api_endpoints=api_endpoints,
            component_names=components,
            feature_descriptions=features,
            business_rules=business_rules,
            
            processing_date=datetime.now().isoformat(),
            word_count=len(clean_text.split()),
            relevance_score=self._calculate_relevance_score(clean_text, tech_stack, components)
        )
        
        self._store_document(doc)
        self._update_knowledge_base(doc)
        
        return doc_id
    
    def _process_pdf_export(self, file_path: str, metadata: Dict = None) -> str:
        """Process PDF export from Confluence."""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2")
        
        try:
            # Extract text from PDF
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
            
            # Get title from metadata or first line
            title = 'Untitled PDF'
            if metadata and isinstance(metadata, dict):
                title = metadata.get('title', 'Untitled PDF')
            
            if not title or title == 'Untitled PDF':
                # Try to extract title from first line of content
                lines = text_content.strip().split('\n')
                if lines:
                    first_line = lines[0].strip()
                    if len(first_line) < 100 and first_line:  # Reasonable title length
                        title = first_line
            
            doc_id = self._generate_doc_id(title, text_content)
            
            # Extract basic structure from PDF text
            headings = self._extract_headings_from_text(text_content)
            code_blocks = self._extract_code_blocks_from_text(text_content)
            
            # Clean and process text
            clean_text = self._clean_pdf_text(text_content)
            
            # Extract knowledge
            tech_stack = self._extract_tech_stack_mentions(clean_text)
            api_endpoints = self._extract_api_endpoints(clean_text, code_blocks)
            components = self._extract_component_names(clean_text, headings)
            features = self._extract_feature_descriptions(clean_text, headings)
            business_rules = self._extract_business_rules(clean_text)
            
            doc = ConfluenceDocument(
                doc_id=doc_id,
                title=title,
                content=text_content,  # Store original extracted text
                url=metadata.get('url', '') if metadata and isinstance(metadata, dict) else '',
                space_key=metadata.get('space_key', '') if metadata and isinstance(metadata, dict) else '',
                page_id=metadata.get('page_id', '') if metadata and isinstance(metadata, dict) else '',
                created_date=metadata.get('created_date', '') if metadata and isinstance(metadata, dict) else '',
                updated_date=metadata.get('updated_date', '') if metadata and isinstance(metadata, dict) else '',
                author=metadata.get('author', '') if metadata and isinstance(metadata, dict) else '',
                labels=metadata.get('labels', []) if metadata and isinstance(metadata, dict) else [],
                parent_page=metadata.get('parent_page', '') if metadata and isinstance(metadata, dict) else '',
                
                extracted_text=clean_text,
                headings=headings,
                code_blocks=code_blocks,
                links=[],  # PDF links are harder to extract
                images=[],  # PDF images not supported in this version
                tables=[],  # PDF tables not supported in this version
                
                tech_stack_mentions=tech_stack,
                api_endpoints=api_endpoints,
                component_names=components,
                feature_descriptions=features,
                business_rules=business_rules,
                
                processing_date=datetime.now().isoformat(),
                word_count=len(clean_text.split()),
                relevance_score=self._calculate_relevance_score(clean_text, tech_stack, components)
            )
            
            self._store_document(doc)
            self._update_knowledge_base(doc)
            
            return doc_id
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _process_text_export(self, content: str, metadata: Dict = None) -> str:
        """Process plain text export."""
        # Get title from metadata or first line
        title = metadata.get('title', 'Untitled Text') if metadata and isinstance(metadata, dict) else 'Untitled Text'
        if not title or title == 'Untitled Text':
            lines = content.strip().split('\n')
            if lines:
                first_line = lines[0].strip()
                if len(first_line) < 100 and first_line:
                    title = first_line
        
        doc_id = self._generate_doc_id(title, content)
        
        # Extract basic structure
        headings = self._extract_headings_from_text(content)
        code_blocks = self._extract_code_blocks_from_text(content)
        
        # Clean text
        clean_text = content.strip()
        
        # Extract knowledge
        tech_stack = self._extract_tech_stack_mentions(clean_text)
        api_endpoints = self._extract_api_endpoints(clean_text, code_blocks)
        components = self._extract_component_names(clean_text, headings)
        features = self._extract_feature_descriptions(clean_text, headings)
        business_rules = self._extract_business_rules(clean_text)
        
        doc = ConfluenceDocument(
            doc_id=doc_id,
            title=title,
            content=content,
            url=metadata.get('url', '') if metadata and isinstance(metadata, dict) else '',
            space_key=metadata.get('space_key', '') if metadata and isinstance(metadata, dict) else '',
            page_id=metadata.get('page_id', '') if metadata and isinstance(metadata, dict) else '',
            created_date=metadata.get('created_date', '') if metadata and isinstance(metadata, dict) else '',
            updated_date=metadata.get('updated_date', '') if metadata and isinstance(metadata, dict) else '',
            author=metadata.get('author', '') if metadata and isinstance(metadata, dict) else '',
            labels=metadata.get('labels', []) if metadata and isinstance(metadata, dict) else [],
            parent_page=metadata.get('parent_page', '') if metadata and isinstance(metadata, dict) else '',
            
            extracted_text=clean_text,
            headings=headings,
            code_blocks=code_blocks,
            links=[],
            images=[],
            tables=[],
            
            tech_stack_mentions=tech_stack,
            api_endpoints=api_endpoints,
            component_names=components,
            feature_descriptions=features,
            business_rules=business_rules,
            
            processing_date=datetime.now().isoformat(),
            word_count=len(clean_text.split()),
            relevance_score=self._calculate_relevance_score(clean_text, tech_stack, components)
        )
        
        self._store_document(doc)
        self._update_knowledge_base(doc)
        
        return doc_id

    def _extract_title(self, soup: BeautifulSoup, metadata: Dict = None) -> str:
        """Extract document title."""
        if metadata and 'title' in metadata:
            return metadata['title']
        
        # Try various title extraction methods
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Untitled Document"
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[str]:
        """Extract all headings."""
        headings = []
        for i in range(1, 7):  # h1 to h6
            for heading in soup.find_all(f'h{i}'):
                headings.append(heading.get_text().strip())
        return headings
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[str]:
        """Extract code blocks."""
        code_blocks = []
        
        # Pre tags
        for pre in soup.find_all('pre'):
            code_blocks.append(pre.get_text().strip())
        
        # Code tags
        for code in soup.find_all('code'):
            if code.parent.name != 'pre':  # Avoid duplicates
                code_blocks.append(code.get_text().strip())
        
        return code_blocks
    
    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract all links."""
        links = []
        for a in soup.find_all('a', href=True):
            links.append(a['href'])
        return links
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract image references."""
        images = []
        for img in soup.find_all('img', src=True):
            images.append(img['src'])
        return images
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract table data."""
        tables = []
        for table in soup.find_all('table'):
            table_data = {
                'headers': [],
                'rows': []
            }
            
            # Extract headers
            headers = table.find_all('th')
            if headers:
                table_data['headers'] = [th.get_text().strip() for th in headers]
            
            # Extract rows
            for tr in table.find_all('tr'):
                cells = tr.find_all(['td', 'th'])
                if cells:
                    row = [cell.get_text().strip() for cell in cells]
                    table_data['rows'].append(row)
            
            tables.append(table_data)
        
        return tables
    
    def _extract_tech_stack_mentions(self, text: str) -> List[str]:
        """Extract technology stack mentions."""
        # Comprehensive tech stack terms including business/domain terms
        tech_terms = [
            # Mobile Development
            'React Native', 'React', 'TypeScript', 'JavaScript', 'Redux', 'Redux Toolkit',
            'React Navigation', 'Async Storage', 'MMKV', 'Reanimated', 'Gesture Handler',
            'Expo', 'Metro', 'Flipper', 'Hermes', 'Fabric', 'iOS', 'Android', 
            'Xcode', 'Android Studio', 'CocoaPods', 'Gradle', 'Swift', 'Kotlin',
            
            # Backend & APIs
            'GraphQL', 'Apollo', 'REST API', 'Node.js', 'Express', 'MongoDB',
            'PostgreSQL', 'MySQL', 'Firebase', 'AWS', 'Amplify', 'Lambda',
            'API Gateway', 'DynamoDB', 'S3', 'CloudFront', 'Cognito',
            
            # Development Tools
            'Jest', 'Detox', 'Fastlane', 'CodePush', 'App Center', 'Sentry',
            'Mixpanel', 'Segment', 'Analytics', 'Crashlytics', 'TestFlight',
            'Git', 'GitHub', 'Bitbucket', 'CI/CD', 'Docker', 'Kubernetes',
            
            # UI/UX Libraries
            'Lottie', 'Linear Gradient', 'Flash List', 'Styled Components',
            'Native Base', 'UI Kitten', 'Shoutem', 'React Native Elements',
            
            # Business/Financial Terms
            'Financial Advisory', 'Investment', 'Portfolio', 'Assets', 'Advisor',
            'Client Management', 'Appointment', 'Schedule', 'Calendar', 'Meeting',
            'KYC', 'AML', 'Compliance', 'Risk Assessment', 'Due Diligence',
            'Wealth Management', 'Financial Planning', 'Investment Strategy',
            
            # General Business Terms
            'Dashboard', 'Analytics', 'Reporting', 'Notifications', 'Authentication',
            'Authorization', 'User Management', 'Profile', 'Settings', 'Preferences',
            'Search', 'Filter', 'Sort', 'Export', 'Import', 'Backup', 'Sync',
            
            # Integration Terms
            'Webhook', 'SDK', 'API Integration', 'Third Party', 'Plugin',
            'Microservices', 'Serverless', 'Event Driven', 'Message Queue',
            
            # Security Terms
            'OAuth', 'JWT', 'SSL/TLS', 'Encryption', 'Two Factor', '2FA',
            'Biometric', 'Touch ID', 'Face ID', 'Secure Storage', 'Keychain'
        ]
        
        found_tech = []
        text_lower = text.lower()
        
        for tech in tech_terms:
            # Case-insensitive search with word boundaries
            import re
            pattern = r'\b' + re.escape(tech.lower()) + r'\b'
            matches = re.findall(pattern, text_lower)
            found_tech.extend([tech] * len(matches))
        
        return found_tech
    
    def _extract_api_endpoints(self, text: str, code_blocks: List[str]) -> List[str]:
        """Extract API endpoint references."""
        endpoints = []
        
        # Look for URL patterns
        url_patterns = [
            r'https?://[^\s]+',
            r'/api/[^\s]+',
            r'GET\s+/[^\s]+',
            r'POST\s+/[^\s]+',
            r'PUT\s+/[^\s]+',
            r'DELETE\s+/[^\s]+',
            r'PATCH\s+/[^\s]+'
        ]
        
        all_text = text + ' ' + ' '.join(code_blocks)
        
        for pattern in url_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            endpoints.extend(matches)
        
        return list(set(endpoints))  # Remove duplicates
    
    def _extract_component_names(self, text: str, headings: List[str]) -> List[str]:
        """Extract React Native component names and business components."""
        components = []
        
        # Technical component patterns
        component_patterns = [
            r'\b[A-Z][a-zA-Z]*(?:Screen|Component|View|Button|Input|Modal|Header|Footer|Card|List|Item|Form|Field|Picker|Slider|Switch|Tab|Nav|Menu)\b',
            r'\b(?:use[A-Z][a-zA-Z]*|create[A-Z][a-zA-Z]*)\b',  # Hooks and creators
            r'\b[A-Z][a-zA-Z]*(?:Manager|Service|Handler|Controller|Provider|Context|Store|Reducer)\b',  # Service patterns
        ]
        
        # Business/Domain component patterns
        business_patterns = [
            # Financial advisory components
            r'\b(?:Advisor|Client|Portfolio|Investment|Asset|Account|Transaction|Report|Dashboard|Calendar|Appointment|Schedule|Meeting|Profile)\b',
            r'\b(?:Risk|Compliance|KYC|AML|Document|Upload|Verification|Assessment)\b',
            r'\b(?:Search|Filter|Sort|Export|Import|Sync|Backup|Settings|Preferences|Notification)\b',
            # UI Component names
            r'\b(?:Login|Register|Signup|Signin|Auth|Authentication|Home|Main|Detail|Edit|Create|Update|Delete|Add|Remove)\b',
            # Screen/Page names
            r'\b[A-Z][a-zA-Z]*(?:Page|Panel|Widget|Tile|Section|Zone|Area|Block|Container)\b'
        ]
        
        all_text = text + ' ' + ' '.join(headings)
        
        # Extract technical components
        for pattern in component_patterns:
            matches = re.findall(pattern, all_text)
            components.extend(matches)
        
        # Extract business components
        for pattern in business_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            # Capitalize first letter for consistency
            components.extend([match.capitalize() for match in matches])
        
        # Extract from headings (likely to be component/feature names)
        for heading in headings:
            words = heading.split()
            for word in words:
                if len(word) > 3 and word[0].isupper():
                    components.append(word)
        
        # Remove common words that aren't components
        filter_words = {'The', 'And', 'Or', 'But', 'For', 'With', 'From', 'To', 'Of', 'In', 'On', 'At', 'By', 'This', 'That', 'These', 'Those', 'A', 'An'}
        components = [comp for comp in components if comp not in filter_words]
        
        return list(set(components))  # Remove duplicates
    
    def _extract_feature_descriptions(self, text: str, headings: List[str]) -> List[str]:
        """Extract feature descriptions."""
        features = []
        
        # Look for feature-related patterns with more business context
        feature_keywords = [
            'feature', 'functionality', 'requirement', 'user story', 'epic',
            'implementation', 'behavior', 'workflow', 'process', 'flow',
            'capability', 'system', 'module', 'component', 'service',
            'integration', 'automation', 'management', 'tracking', 'monitoring',
            'advisory', 'appointment', 'schedule', 'calendar', 'meeting',
            'client', 'advisor', 'portfolio', 'investment', 'compliance'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30:  # Minimum meaningful length
                sentence_lower = sentence.lower()
                for keyword in feature_keywords:
                    if keyword in sentence_lower:
                        # Clean up the sentence
                        clean_sentence = re.sub(r'\s+', ' ', sentence)
                        if len(clean_sentence) < 300:  # Not too long
                            features.append(clean_sentence)
                        break
        
        # Also extract from headings as features
        for heading in headings:
            if len(heading) > 10 and len(heading) < 100:
                # Skip if it looks like a table of contents entry
                if not heading.lower().startswith('table of contents'):
                    features.append(heading)
        
        # Look for numbered or bulleted lists that might be features
        list_patterns = [
            r'^\d+\.\s+(.+)$',  # Numbered lists
            r'^[-•]\s+(.+)$',   # Bulleted lists
            r'^[a-zA-Z]\.\s+(.+)$'  # Lettered lists
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            for pattern in list_patterns:
                match = re.match(pattern, line)
                if match and len(match.group(1)) > 15:
                    features.append(match.group(1))
        
        # Remove duplicates and limit
        unique_features = []
        for feature in features:
            if feature not in unique_features:
                unique_features.append(feature)
        
        return unique_features[:30]  # Increased limit
    
    def _extract_business_rules(self, text: str) -> List[str]:
        """Extract business rules and constraints."""
        rules = []
        
        # Look for rule-like patterns
        rule_patterns = [
            r'must\s+[^.!?]+[.!?]',
            r'should\s+[^.!?]+[.!?]',
            r'cannot\s+[^.!?]+[.!?]',
            r'only\s+[^.!?]+[.!?]',
            r'always\s+[^.!?]+[.!?]',
            r'never\s+[^.!?]+[.!?]',
            r'required\s+[^.!?]+[.!?]',
            r'mandatory\s+[^.!?]+[.!?]'
        ]
        
        for pattern in rule_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            rules.extend([match.strip() for match in matches])
        
        return list(set(rules))[:15]  # Limit and remove duplicates
    
    def _calculate_relevance_score(self, text: str, tech_mentions: List[str], components: List[str]) -> float:
        """Calculate relevance score for the document."""
        score = 0.0
        
        # Base score from word count
        word_count = len(text.split())
        score += min(word_count / 1000, 1.0) * 20  # Max 20 points for content length
        
        # Tech stack mentions
        score += len(set(tech_mentions)) * 5  # 5 points per unique tech
        
        # Component mentions
        score += len(set(components)) * 3  # 3 points per unique component
        
        # App-specific keywords
        app_keywords = ['habitto', 'habit', 'tracking', 'mobile', 'app', 'user', 'profile']
        for keyword in app_keywords:
            if keyword.lower() in text.lower():
                score += 10
        
        return min(score, 100.0)  # Cap at 100
    
    def _generate_doc_id(self, title: str, content: str) -> str:
        """Generate unique document ID."""
        content_hash = hashlib.md5(f"{title}:{content}".encode()).hexdigest()
        return f"doc_{content_hash[:12]}"
    
    def _store_document(self, doc: ConfluenceDocument):
        """Store document in database and files."""
        # Store JSON file
        doc_file = self.processed_dir / f"{doc.doc_id}.json"
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(doc), f, indent=2, ensure_ascii=False)
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert main record
            cursor.execute('''
                INSERT OR REPLACE INTO confluence_docs 
                (doc_id, title, url, space_key, page_id, created_date, updated_date,
                 author, processing_date, word_count, relevance_score, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc.doc_id, doc.title, doc.url, doc.space_key, doc.page_id,
                doc.created_date, doc.updated_date, doc.author, doc.processing_date,
                doc.word_count, doc.relevance_score, str(doc_file)
            ))
            
            # Clear existing related data
            for table in ['doc_labels', 'tech_mentions', 'api_endpoints', 
                         'component_refs', 'feature_descriptions', 'business_rules']:
                cursor.execute(f'DELETE FROM {table} WHERE doc_id = ?', (doc.doc_id,))
            
            # Insert labels
            for label in doc.labels:
                cursor.execute('INSERT INTO doc_labels (doc_id, label) VALUES (?, ?)',
                             (doc.doc_id, label))
            
            # Insert tech mentions
            tech_counts = {}
            for tech in doc.tech_stack_mentions:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
            
            for tech, count in tech_counts.items():
                cursor.execute('INSERT INTO tech_mentions (doc_id, technology, mention_count) VALUES (?, ?, ?)',
                             (doc.doc_id, tech, count))
            
            # Insert API endpoints
            for endpoint in doc.api_endpoints:
                method = 'GET'  # Default
                if any(m in endpoint.upper() for m in ['POST', 'PUT', 'DELETE', 'PATCH']):
                    method = next(m for m in ['POST', 'PUT', 'DELETE', 'PATCH'] if m in endpoint.upper())
                
                cursor.execute('INSERT INTO api_endpoints (doc_id, endpoint, method, description) VALUES (?, ?, ?, ?)',
                             (doc.doc_id, endpoint, method, ''))
            
            # Insert components
            for component in doc.component_names:
                cursor.execute('INSERT INTO component_refs (doc_id, component_name, description) VALUES (?, ?, ?)',
                             (doc.doc_id, component, ''))
            
            # Insert features
            for feature in doc.feature_descriptions:
                cursor.execute('INSERT INTO feature_descriptions (doc_id, feature_name, description, priority) VALUES (?, ?, ?, ?)',
                             (doc.doc_id, feature[:100], feature, 'Medium'))
            
            # Insert business rules
            for rule in doc.business_rules:
                cursor.execute('INSERT INTO business_rules (doc_id, rule_text, category) VALUES (?, ?, ?)',
                             (doc.doc_id, rule, 'General'))
            
            conn.commit()
        
        print(f"✅ Stored Confluence document: {doc.title} ({doc.doc_id})")
    
    def _update_knowledge_base(self, doc: ConfluenceDocument):
        """Update the knowledge base with document insights."""
        if 'tech_stack' not in self.knowledge_base:
            self.knowledge_base['tech_stack'] = {}
        
        if 'components' not in self.knowledge_base:
            self.knowledge_base['components'] = {}
        
        if 'features' not in self.knowledge_base:
            self.knowledge_base['features'] = []
        
        if 'business_rules' not in self.knowledge_base:
            self.knowledge_base['business_rules'] = []
        
        # Update tech stack knowledge
        for tech in set(doc.tech_stack_mentions):
            if tech not in self.knowledge_base['tech_stack']:
                self.knowledge_base['tech_stack'][tech] = {
                    'count': 0,
                    'documents': []
                }
            self.knowledge_base['tech_stack'][tech]['count'] += doc.tech_stack_mentions.count(tech)
            if doc.doc_id not in self.knowledge_base['tech_stack'][tech]['documents']:
                self.knowledge_base['tech_stack'][tech]['documents'].append(doc.doc_id)
        
        # Update components knowledge
        for component in set(doc.component_names):
            if component not in self.knowledge_base['components']:
                self.knowledge_base['components'][component] = {
                    'documents': [],
                    'description': ''
                }
            if doc.doc_id not in self.knowledge_base['components'][component]['documents']:
                self.knowledge_base['components'][component]['documents'].append(doc.doc_id)
        
        # Add new features and rules
        self.knowledge_base['features'].extend(doc.feature_descriptions)
        self.knowledge_base['business_rules'].extend(doc.business_rules)
        
        # Save knowledge base
        self.save_knowledge_base()
    
    def load_knowledge_base(self):
        """Load knowledge base from file."""
        kb_path = self.knowledge_dir / "knowledge_base.json"
        if kb_path.exists():
            try:
                with open(kb_path, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
            except:
                self.knowledge_base = {}
        else:
            self.knowledge_base = {}
    
    def save_knowledge_base(self):
        """Save knowledge base to file."""
        kb_path = self.knowledge_dir / "knowledge_base.json"
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
    
    def _detect_ticket_topic(self, ticket_content: str) -> List[str]:
        """Detect the primary topic/domain of the ticket for contextual filtering."""
        content_lower = ticket_content.lower()
        
        # Define topic keywords and their associated domains
        topic_mappings = {
            'chat': ['chat', 'messaging', 'conversation', 'message', 'reply', 'send', 'receive', 'communication', 'chatbot', 'dialog', 'talk', 'speak'],
            'profile': ['profile', 'user', 'account', 'personal', 'settings', 'preferences', 'info', 'information', 'details', 'edit', 'update'],
            'payment': ['payment', 'billing', 'invoice', 'transaction', 'money', 'fee', 'cost', 'charge', 'subscription', 'price', 'pay', 'purchase'],
            'authentication': ['login', 'signup', 'register', 'auth', 'authentication', 'password', 'credential', 'signin', 'logout', 'session'],
            'calendar': ['calendar', 'appointment', 'schedule', 'booking', 'date', 'time', 'availability', 'meeting', 'slot', 'agenda'],
            'notification': ['notification', 'alert', 'reminder', 'push', 'email', 'sms', 'notify', 'announcement', 'update', 'inform'],
            'dashboard': ['dashboard', 'analytics', 'metrics', 'chart', 'graph', 'report', 'statistics', 'data', 'visualization', 'overview'],
            'onboarding': ['onboarding', 'welcome', 'tutorial', 'guide', 'introduction', 'setup', 'walkthrough', 'getting started'],
            'search': ['search', 'filter', 'find', 'lookup', 'query', 'browse', 'explore', 'discover'],
            'navigation': ['navigation', 'menu', 'tab', 'sidebar', 'header', 'footer', 'link', 'route', 'page'],
            'form': ['form', 'input', 'field', 'validation', 'submit', 'dropdown', 'select', 'checkbox', 'radio'],
            'advisor': ['advisor', 'consultant', 'expert', 'professional', 'counselor', 'guidance', 'advice'],
            'client': ['client', 'customer', 'user', 'contact', 'relationship', 'management']
        }
        
        detected_topics = []
        topic_scores = {}
        
        # Calculate topic relevance scores
        for topic, keywords in topic_mappings.items():
            score = 0
            for keyword in keywords:
                if keyword in content_lower:
                    # Higher score for exact matches, lower for partial
                    if f" {keyword} " in content_lower or content_lower.startswith(keyword) or content_lower.endswith(keyword):
                        score += 2  # Exact word match
                    else:
                        score += 1  # Partial match
            
            if score > 0:
                topic_scores[topic] = score
        
        # Sort topics by relevance score and return top 3
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        detected_topics = [topic for topic, score in sorted_topics[:3] if score >= 2]  # Minimum score threshold
        
        # If no specific topics detected, use general topics
        if not detected_topics:
            detected_topics = ['general']
        
        return detected_topics

    def _calculate_topic_relevance(self, doc_data: Dict, ticket_topics: List[str]) -> float:
        """Calculate how relevant a document is to the detected ticket topics."""
        if 'general' in ticket_topics:
            return 1.0  # All documents are relevant for general topics
        
        doc_content = (doc_data.get('title', '') + ' ' + doc_data.get('extracted_text', '')).lower()
        
        # Define the same topic mappings for document analysis
        topic_mappings = {
            'chat': ['chat', 'messaging', 'conversation', 'message', 'reply', 'send', 'receive', 'communication', 'chatbot', 'dialog', 'talk', 'speak'],
            'profile': ['profile', 'user', 'account', 'personal', 'settings', 'preferences', 'info', 'information', 'details', 'edit', 'update'],
            'payment': ['payment', 'billing', 'invoice', 'transaction', 'money', 'fee', 'cost', 'charge', 'subscription', 'price', 'pay', 'purchase'],
            'authentication': ['login', 'signup', 'register', 'auth', 'authentication', 'password', 'credential', 'signin', 'logout', 'session'],
            'calendar': ['calendar', 'appointment', 'schedule', 'booking', 'date', 'time', 'availability', 'meeting', 'slot', 'agenda'],
            'notification': ['notification', 'alert', 'reminder', 'push', 'email', 'sms', 'notify', 'announcement', 'update', 'inform'],
            'dashboard': ['dashboard', 'analytics', 'metrics', 'chart', 'graph', 'report', 'statistics', 'data', 'visualization', 'overview'],
            'onboarding': ['onboarding', 'welcome', 'tutorial', 'guide', 'introduction', 'setup', 'walkthrough', 'getting started'],
            'search': ['search', 'filter', 'find', 'lookup', 'query', 'browse', 'explore', 'discover'],
            'navigation': ['navigation', 'menu', 'tab', 'sidebar', 'header', 'footer', 'link', 'route', 'page'],
            'form': ['form', 'input', 'field', 'validation', 'submit', 'dropdown', 'select', 'checkbox', 'radio'],
            'advisor': ['advisor', 'consultant', 'expert', 'professional', 'counselor', 'guidance', 'advice'],
            'client': ['client', 'customer', 'user', 'contact', 'relationship', 'management']
        }
        
        max_relevance = 0.0
        
        for topic in ticket_topics:
            if topic in topic_mappings:
                topic_keywords = topic_mappings[topic]
                topic_matches = sum(1 for keyword in topic_keywords if keyword in doc_content)
                topic_relevance = topic_matches / len(topic_keywords)
                max_relevance = max(max_relevance, topic_relevance)
        
        return max_relevance

    def get_relevant_context(self, ticket_content: str, limit: int = 5) -> Dict[str, Any]:
        """Get relevant context from Confluence docs for a ticket with topic-based filtering."""
        # Detect ticket topics for smart filtering
        ticket_topics = self._detect_ticket_topic(ticket_content)
        print(f"🎯 Detected ticket topics: {', '.join(ticket_topics)}")
        
        # Simple relevance matching based on keywords
        ticket_words = set(ticket_content.lower().split())
        
        relevant_docs = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT doc_id, title, relevance_score FROM confluence_docs ORDER BY relevance_score DESC')
            
            for doc_id, title, score in cursor.fetchall():
                # Load document for analysis
                doc_file = self.processed_dir / f"{doc_id}.json"
                if doc_file.exists():
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            doc_data = json.load(f)
                        
                        # Calculate topic-based relevance
                        topic_relevance = self._calculate_topic_relevance(doc_data, ticket_topics)
                        
                        # Only include documents with good topic relevance
                        if topic_relevance > 0.1 or 'general' in ticket_topics:  # Relaxed threshold for topic relevance
                            # Calculate keyword-based relevance
                            doc_words = set(doc_data['extracted_text'].lower().split())
                            common_words = ticket_words.intersection(doc_words)
                            
                            if len(common_words) > 2:  # Minimum relevance threshold
                                keyword_relevance = len(common_words) / len(ticket_words) * score
                                
                                # Combined relevance score (weighted)
                                combined_relevance = (topic_relevance * 0.7) + (keyword_relevance * 0.3)
                                
                                relevant_docs.append({
                                    'doc_id': doc_id,
                                    'title': title,
                                    'relevance': combined_relevance,
                                    'topic_relevance': topic_relevance,
                                    'keyword_relevance': keyword_relevance,
                                    'tech_stack': doc_data.get('tech_stack_mentions', []),
                                    'components': doc_data.get('component_names', []),
                                    'features': doc_data.get('feature_descriptions', [])[:3],
                                    'business_rules': doc_data.get('business_rules', [])[:2]
                                })
                    except:
                        continue
        
        # Sort by combined relevance and return top results
        relevant_docs.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Filter for high-relevance documents only
        if ticket_topics != ['general']:
            relevant_docs = [doc for doc in relevant_docs if doc['topic_relevance'] > 0.15]
        
        filtered_docs = relevant_docs[:limit]
        
        # Log which documents were selected
        if filtered_docs:
            print(f"📚 Selected {len(filtered_docs)} topic-relevant documents:")
            for doc in filtered_docs:
                print(f"   • {doc['title']} (topic: {doc['topic_relevance']:.2f}, keyword: {doc['keyword_relevance']:.2f})")
        else:
            print(f"⚠️ No topic-relevant documents found for topics: {', '.join(ticket_topics)}")
        
        return {
            'relevant_documents': filtered_docs,
            'detected_topics': ticket_topics,
            'knowledge_base_summary': {
                'total_docs': len(self.get_all_documents()),
                'filtered_docs': len(filtered_docs),
                'tech_stack': list(self.knowledge_base.get('tech_stack', {}).keys())[:10],
                'components': list(self.knowledge_base.get('components', {}).keys())[:10]
            }
        }
    
    def get_all_documents(self) -> List[Dict]:
        """Get all stored documents."""
        docs = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT doc_id, title, word_count, relevance_score, processing_date 
                FROM confluence_docs 
                ORDER BY relevance_score DESC
            ''')
            
            for row in cursor.fetchall():
                docs.append({
                    'doc_id': row[0],
                    'title': row[1],
                    'word_count': row[2],
                    'relevance_score': row[3],
                    'processing_date': row[4]
                })
        
        return docs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Confluence integration statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM confluence_docs')
            total_docs = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT technology) FROM tech_mentions')
            unique_tech = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM component_refs')
            total_components = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(word_count) FROM confluence_docs')
            avg_words = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT AVG(relevance_score) FROM confluence_docs')
            avg_relevance = cursor.fetchone()[0] or 0
        
        return {
            'total_documents': total_docs,
            'unique_technologies': unique_tech,
            'total_components': total_components,
            'average_word_count': round(avg_words, 1),
            'average_relevance_score': round(avg_relevance, 1),
            'knowledge_base_size': len(self.knowledge_base)
        }

    def _extract_headings_from_text(self, text: str) -> List[str]:
        """Extract headings from plain text using common patterns."""
        headings = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            
            # Look for lines that might be headings
            if len(line) > 0 and len(line) < 100:  # Reasonable heading length
                # All caps might be a heading
                if line.isupper() and len(line.split()) <= 8:
                    headings.append(line)
                # Lines ending with colon might be headings
                elif line.endswith(':') and len(line.split()) <= 8:
                    headings.append(line[:-1])  # Remove colon
                # Lines that are standalone and short might be headings
                elif len(line.split()) <= 6 and not line.endswith('.'):
                    # Check if next line is empty or starts with content
                    idx = lines.index(line) if line in lines else -1
                    if idx >= 0 and idx < len(lines) - 1:
                        next_line = lines[idx + 1].strip()
                        if not next_line or next_line.startswith('-') or next_line.startswith('•'):
                            headings.append(line)
        
        return headings[:20]  # Limit to reasonable number

    def _extract_code_blocks_from_text(self, text: str) -> List[str]:
        """Extract code blocks from plain text."""
        code_blocks = []
        
        # Look for common code patterns
        code_patterns = [
            r'```[\s\S]*?```',  # Markdown code blocks
            r'`[^`]+`',  # Inline code
            r'^\s{4,}.+$',  # Indented code (multiline)
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            code_blocks.extend([match.strip('`').strip() for match in matches])
        
        return code_blocks[:50]  # Limit to reasonable number

    def _clean_pdf_text(self, text: str) -> str:
        """Clean text extracted from PDF."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page numbers and headers/footers (basic patterns)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip likely page numbers
            if re.match(r'^\d+$', line):
                continue
            
            # Skip very short lines that might be artifacts
            if len(line) < 3:
                continue
                
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

# Example usage
if __name__ == "__main__":
    confluence = ConfluenceIntegration()
    
    print("📚 Confluence Integration System Ready")
    print(f"📊 Current statistics: {confluence.get_statistics()}") 