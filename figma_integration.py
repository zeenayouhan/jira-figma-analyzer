#!/usr/bin/env python3
"""
Figma Design Integration System

This system integrates with the Figma API to read and analyze Figma designs,
extracting design elements, components, and user interface details to enhance
the Jira ticket analysis with actual design context.

Enhanced with Japanese text detection and processing capabilities.
"""

import os
import json
import re
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import base64
import unicodedata

# Japanese text detection utilities
def detect_japanese_text(text: str) -> bool:
    """Detect if text contains Japanese characters (Hiragana, Katakana, Kanji)."""
    if not text:
        return False
    
    japanese_ranges = [
        (0x3040, 0x309F),  # Hiragana
        (0x30A0, 0x30FF),  # Katakana
        (0x4E00, 0x9FAF),  # Kanji (CJK Unified Ideographs)
        (0x3400, 0x4DBF),  # CJK Extension A
        (0xFF65, 0xFF9F),  # Half-width Katakana
    ]
    
    for char in text:
        char_code = ord(char)
        for start, end in japanese_ranges:
            if start <= char_code <= end:
                return True
    return False

def classify_japanese_text_type(text: str) -> Dict[str, Any]:
    """Classify Japanese text by character types."""
    if not text:
        return {"has_japanese": False}
    
    hiragana_count = 0
    katakana_count = 0
    kanji_count = 0
    latin_count = 0
    number_count = 0
    
    for char in text:
        char_code = ord(char)
        if 0x3040 <= char_code <= 0x309F:  # Hiragana
            hiragana_count += 1
        elif 0x30A0 <= char_code <= 0x30FF or 0xFF65 <= char_code <= 0xFF9F:  # Katakana
            katakana_count += 1
        elif 0x4E00 <= char_code <= 0x9FAF or 0x3400 <= char_code <= 0x4DBF:  # Kanji
            kanji_count += 1
        elif char.isascii() and char.isalpha():
            latin_count += 1
        elif char.isdigit():
            number_count += 1
    
    total_chars = len(text)
    has_japanese = (hiragana_count + katakana_count + kanji_count) > 0
    
    return {
        "has_japanese": has_japanese,
        "hiragana_ratio": hiragana_count / total_chars if total_chars > 0 else 0,
        "katakana_ratio": katakana_count / total_chars if total_chars > 0 else 0,
        "kanji_ratio": kanji_count / total_chars if total_chars > 0 else 0,
        "latin_ratio": latin_count / total_chars if total_chars > 0 else 0,
        "japanese_ratio": (hiragana_count + katakana_count + kanji_count) / total_chars if total_chars > 0 else 0,
        "primary_script": "japanese" if has_japanese and (hiragana_count + katakana_count + kanji_count) > latin_count else "latin",
        "total_japanese_chars": hiragana_count + katakana_count + kanji_count,
        "total_chars": total_chars
    }

@dataclass
class FigmaComponent:
    """Represents a Figma component or element."""
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    children: List['FigmaComponent']
    styles: Dict[str, Any]

@dataclass
class FigmaPage:
    """Represents a Figma page."""
    id: str
    name: str
    type: str
    components: List[FigmaComponent]
    background: Dict[str, Any]

@dataclass
class FigmaDesign:
    """Represents a complete Figma design file."""
    file_key: str
    name: str
    description: str
    pages: List[FigmaPage]
    components: Dict[str, Any]
    styles: Dict[str, Any]
    version: str
    last_modified: str
    
    # Extracted analysis
    ui_components: List[str]
    screens: List[str]
    user_flows: List[str]
    design_tokens: Dict[str, Any]
    interactions: List[str]
    
    # Business insights
    complexity_score: float
    implementation_notes: List[str]
    accessibility_considerations: List[str]
    # New: per-screen details
    screen_details: List[Dict[str, Any]]
    
    # Japanese text analysis
    japanese_text_analysis: Dict[str, Any] = None
    japanese_screens: List[str] = None
    total_japanese_text_nodes: int = 0

class FigmaIntegration:
    """Main class for Figma API integration and design analysis."""
    
    def __init__(self, figma_token: str = None):
        self.figma_token = figma_token or os.getenv('FIGMA_ACCESS_TOKEN')
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": self.figma_token,
            "Content-Type": "application/json"
        } if self.figma_token else {}
        
        print("🎨 Figma Integration initialized")
    
    def extract_figma_file_key(self, figma_url: str) -> Optional[str]:
        """Extract file key from Figma URL."""
        try:
            # Parse different Figma URL formats
            # https://www.figma.com/file/FILE_KEY/TITLE
            # https://www.figma.com/design/FILE_KEY/TITLE
            # https://figma.com/file/FILE_KEY/TITLE
            
            patterns = [
                r'figma\.com/(?:file|design)/([a-zA-Z0-9]+)',
                r'figma\.com/file/([a-zA-Z0-9]+)',
                r'figma\.com/design/([a-zA-Z0-9]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, figma_url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            print(f"Error extracting Figma file key: {e}")
            return None
    
    def get_figma_file(self, file_key: str) -> Optional[Dict]:
        """Fetch Figma file data from API."""
        if not self.figma_token:
            print("⚠️ Figma access token not provided. Set FIGMA_ACCESS_TOKEN environment variable.")
            return None
        
        try:
            url = f"{self.base_url}/files/{file_key}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                print("❌ Figma API access denied. Check your token or file permissions.")
                return None
            elif response.status_code == 404:
                print("❌ Figma file not found. Check the file key or URL.")
                return None
            else:
                print(f"❌ Figma API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error fetching Figma file: {e}")
            return None
    
    def get_figma_images(self, file_key: str, node_ids: List[str] = None) -> Optional[Dict]:
        """Get image exports of Figma nodes."""
        if not self.figma_token:
            return None
        
        try:
            params = {
                "ids": ",".join(node_ids) if node_ids else "",
                "format": "png",
                "scale": 2
            }
            
            url = f"{self.base_url}/images/{file_key}"
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching Figma images: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching Figma images: {e}")
            return None
    
    def analyze_figma_design(self, figma_url: str) -> Optional[FigmaDesign]:
        """Analyze a Figma design from URL."""
        file_key = self.extract_figma_file_key(figma_url)
        if not file_key:
            print(f"❌ Could not extract file key from URL: {figma_url}")
            return None
        
        print(f"📥 Fetching Figma design: {file_key}")
        file_data = self.get_figma_file(file_key)
        
        if not file_data:
            return None
        
        try:
            # Parse the Figma file structure
            document = file_data.get('document', {})
            
            # Extract pages
            pages = []
            for page_data in document.get('children', []):
                if page_data.get('type') == 'CANVAS':
                    page = self._parse_figma_page(page_data)
                    pages.append(page)
            
            # Extract components and styles
            components = file_data.get('components', {})
            styles = file_data.get('styles', {})
            
            # Analyze design elements
            ui_components = self._extract_ui_components(pages)
            screens = self._extract_screens(pages)
            user_flows = self._extract_user_flows(pages)
            design_tokens = self._extract_design_tokens(styles)
            interactions = self._extract_interactions(pages)
            # New: extract screen details and summaries
            screen_details = self._extract_screen_details(pages, screens)
            
            # Calculate complexity and insights
            complexity_score = self._calculate_complexity_score(pages, ui_components)
            implementation_notes = self._generate_implementation_notes(ui_components, screens)
            accessibility_considerations = self._analyze_accessibility(pages)
            
            # Analyze Japanese text content
            japanese_analysis = self._analyze_japanese_text_in_design(pages)
            
            design = FigmaDesign(
                file_key=file_key,
                name=file_data.get('name', 'Untitled'),
                description=file_data.get('description', ''),
                pages=pages,
                components=components,
                styles=styles,
                version=file_data.get('version', ''),
                last_modified=file_data.get('lastModified', ''),
                
                ui_components=ui_components,
                screens=screens,
                user_flows=user_flows,
                design_tokens=design_tokens,
                interactions=interactions,
                
                complexity_score=complexity_score,
                implementation_notes=implementation_notes,
                accessibility_considerations=accessibility_considerations,
                screen_details=screen_details,
                
                # Japanese text analysis
                japanese_text_analysis=japanese_analysis,
                japanese_screens=japanese_analysis.get('japanese_screens', []),
                total_japanese_text_nodes=len(japanese_analysis.get('japanese_text_nodes', []))
            )
            
            print(f"✅ Figma design analyzed: {design.name}")
            print(f"   📄 Pages: {len(pages)}")
            print(f"   🧩 UI Components: {len(ui_components)}")
            print(f"   📱 Screens: {len(screens)}")
            print(f"   🔄 User Flows: {len(user_flows)}")
            print(f"   ⚡ Complexity Score: {complexity_score:.1f}/10")
            if screen_details:
                print(f"   📝 Screen details extracted: {len(screen_details)}")
            
            # Japanese text analysis summary
            if japanese_analysis.get('has_japanese'):
                print(f"   🇯🇵 Japanese content detected:")
                print(f"      • Japanese text nodes: {len(japanese_analysis.get('japanese_text_nodes', []))}")
                print(f"      • Japanese screens: {len(japanese_analysis.get('japanese_screens', []))}")
                print(f"      • Japanese ratio: {japanese_analysis.get('japanese_ratio', 0):.1%}")
                if japanese_analysis.get('ui_element_analysis'):
                    ui_analysis = japanese_analysis['ui_element_analysis']
                    if ui_analysis['japanese_buttons']:
                        print(f"      • Japanese buttons: {len(ui_analysis['japanese_buttons'])}")
                    if ui_analysis['japanese_navigation']:
                        print(f"      • Japanese navigation: {len(ui_analysis['japanese_navigation'])}")
            else:
                print(f"   🌐 Language: Primarily English/Latin text")
            
            return design
            
        except Exception as e:
            print(f"Error analyzing Figma design: {e}")
            return None
    
    def _parse_figma_page(self, page_data: Dict) -> FigmaPage:
        """Parse a Figma page from API data."""
        components = []
        
        # Recursively parse children
        for child in page_data.get('children', []):
            component = self._parse_figma_component(child)
            components.append(component)
        
        return FigmaPage(
            id=page_data.get('id', ''),
            name=page_data.get('name', ''),
            type=page_data.get('type', ''),
            components=components,
            background=page_data.get('backgroundColor', {})
        )
    
    def _parse_figma_component(self, component_data: Dict) -> FigmaComponent:
        """Parse a Figma component from API data."""
        children = []
        
        # Recursively parse children
        for child in component_data.get('children', []):
            child_component = self._parse_figma_component(child)
            children.append(child_component)
        
        # Capture common fields as properties for downstream extraction
        properties = component_data.get('properties', {}).copy()
        if 'characters' in component_data:
            properties['characters'] = component_data.get('characters')
        if 'componentId' in component_data:
            properties['componentId'] = component_data.get('componentId')
        if 'componentProperties' in component_data:
            properties['componentProperties'] = component_data.get('componentProperties')
        if 'variantProperties' in component_data:
            properties['variantProperties'] = component_data.get('variantProperties')

        return FigmaComponent(
            id=component_data.get('id', ''),
            name=component_data.get('name', ''),
            type=component_data.get('type', ''),
            properties=properties,
            children=children,
            styles=component_data.get('styles', {})
        )
    
    def _extract_ui_components(self, pages: List[FigmaPage]) -> List[str]:
        """Extract UI component names from Figma pages."""
        components = set()
        
        for page in pages:
            self._collect_component_names(page.components, components)
        
        # Filter and clean component names
        ui_components = []
        for comp in components:
            if self._is_ui_component_name(comp):
                ui_components.append(comp)
        
        return sorted(list(set(ui_components)))
    
    def _collect_component_names(self, components: List[FigmaComponent], result: set):
        """Recursively collect component names."""
        for comp in components:
            if comp.name and comp.name.strip():
                result.add(comp.name.strip())
            
            # Recursively collect from children
            self._collect_component_names(comp.children, result)
    
    def _is_ui_component_name(self, name: str) -> bool:
        """Check if a name looks like a UI component."""
        if not name or len(name) < 2:
            return False
        
        # Skip generic names
        generic_names = {
            'frame', 'group', 'rectangle', 'ellipse', 'line', 'vector', 
            'text', 'image', 'mask', 'boolean', 'star', 'polygon'
        }
        
        if name.lower() in generic_names:
            return False
        
        # Look for UI component patterns
        ui_patterns = [
            r'button', r'input', r'field', r'card', r'modal', r'dialog',
            r'header', r'footer', r'nav', r'menu', r'tab', r'form',
            r'list', r'item', r'row', r'column', r'container', r'wrapper',
            r'screen', r'page', r'view', r'panel', r'sidebar', r'toolbar',
            r'avatar', r'badge', r'chip', r'tag', r'label', r'icon'
        ]
        
        name_lower = name.lower()
        for pattern in ui_patterns:
            if pattern in name_lower:
                return True
        
        # Check for component naming conventions (PascalCase, kebab-case)
        if re.match(r'^[A-Z][a-zA-Z0-9]*$', name) or '-' in name:
            return True
        
        return False
    
    def _extract_screens(self, pages: List[FigmaPage]) -> List[str]:
        """Extract screen names from Figma pages."""
        screens = []
        
        for page in pages:
            # Page names often represent screens
            if self._is_screen_name(page.name):
                screens.append(page.name)
            
            # Look for screen-like components
            for comp in page.components:
                if self._is_screen_name(comp.name):
                    screens.append(comp.name)
        
        return sorted(list(set(screens)))
    
    def _is_screen_name(self, name: str) -> bool:
        """Check if a name looks like a screen or page."""
        if not name:
            return False
        
        screen_keywords = [
            'screen', 'page', 'view', 'dashboard', 'home', 'login', 'signup',
            'profile', 'settings', 'detail', 'list', 'form', 'checkout',
            'cart', 'search', 'results', 'overview', 'summary', 'onboarding'
        ]
        
        name_lower = name.lower()
        return any(keyword in name_lower for keyword in screen_keywords)
    
    def _extract_user_flows(self, pages: List[FigmaPage]) -> List[str]:
        """Extract user flow information from Figma pages."""
        flows = []
        
        for page in pages:
            # Look for flow-related naming
            if any(word in page.name.lower() for word in ['flow', 'journey', 'process', 'workflow']):
                flows.append(f"Flow: {page.name}")
            
            # Look for sequential screens
            screen_sequences = self._find_screen_sequences(page.components)
            flows.extend(screen_sequences)
        
        return flows
    
    def _find_screen_sequences(self, components: List[FigmaComponent]) -> List[str]:
        """Find sequences of screens that might represent user flows."""
        sequences = []
        
        # Look for numbered or sequential components
        numbered_screens = []
        for comp in components:
            if re.search(r'\d+', comp.name) and self._is_screen_name(comp.name):
                numbered_screens.append(comp.name)
        
        if len(numbered_screens) > 1:
            sequences.append(f"Sequential Flow: {' → '.join(sorted(numbered_screens))}")
        
        return sequences
    
    def _extract_design_tokens(self, styles: Dict) -> Dict[str, Any]:
        """Extract design tokens (colors, typography, etc.) from Figma styles."""
        tokens = {
            'colors': [],
            'typography': [],
            'spacing': [],
            'effects': []
        }
        
        for style_id, style_data in styles.items():
            style_type = style_data.get('styleType', '').lower()
            
            if style_type == 'fill':
                tokens['colors'].append({
                    'name': style_data.get('name', ''),
                    'description': style_data.get('description', '')
                })
            elif style_type == 'text':
                tokens['typography'].append({
                    'name': style_data.get('name', ''),
                    'description': style_data.get('description', '')
                })
            elif style_type == 'effect':
                tokens['effects'].append({
                    'name': style_data.get('name', ''),
                    'description': style_data.get('description', '')
                })
        
        return tokens
    
    def _extract_interactions(self, pages: List[FigmaPage]) -> List[str]:
        """Extract interaction and prototype information."""
        interactions = []
        
        for page in pages:
            # Look for interaction-related components
            for comp in page.components:
                if any(word in comp.name.lower() for word in ['click', 'tap', 'hover', 'press', 'swipe']):
                    interactions.append(f"Interaction: {comp.name}")
        
        return interactions

    def _extract_screen_details(self, pages: List[FigmaPage], screens: List[str]) -> List[Dict[str, Any]]:
        """Extract detailed screen information including form fields, CTAs, and validation cues."""
        screen_set = set(screens)
        details: List[Dict[str, Any]] = []

        # Helper to deeply analyze a component tree for form elements
        def analyze_component_tree(comp: FigmaComponent, screen_data: Dict[str, Any]):
            # Text nodes - capture all text content
            if comp.type == 'TEXT':
                txt = comp.properties.get('characters') or comp.name
                if txt and len(txt.strip()) > 0:
                    screen_data['all_texts'].append(txt.strip())
                    
                    # Check if it's a label, placeholder, or validation message
                    txt_lower = txt.lower().strip()
                    
                    # Field labels (usually end with colon or are short descriptive text)
                    if any(keyword in txt_lower for keyword in ['email', 'password', 'name', 'phone', 'address', 'username']):
                        screen_data['field_labels'].append(txt.strip())
                    
                    # Validation messages (error patterns)
                    if any(keyword in txt_lower for keyword in ['required', 'invalid', 'error', 'must be', 'please enter', 'cannot be empty']):
                        screen_data['validation_messages'].append(txt.strip())
                    
                    # Placeholders (usually light gray text or hints)
                    if any(keyword in txt_lower for keyword in ['enter your', 'type here', 'placeholder', 'hint']):
                        screen_data['placeholders'].append(txt.strip())

            # Input fields and form elements
            comp_name_lower = comp.name.lower() if comp.name else ''
            
            # Input field detection
            if any(keyword in comp_name_lower for keyword in ['input', 'textfield', 'field', 'form']):
                field_info = {
                    'name': comp.name,
                    'type': self._determine_field_type(comp),
                    'placeholder': self._extract_placeholder(comp),
                    'label': self._extract_field_label(comp),
                    'required': self._is_field_required(comp),
                    'validation': self._extract_validation_rules(comp)
                }
                screen_data['form_fields'].append(field_info)
            
            # Button and CTA detection
            elif any(keyword in comp_name_lower for keyword in ['button', 'btn', 'cta', 'action']):
                cta_info = {
                    'name': comp.name,
                    'text': self._extract_button_text(comp),
                    'type': self._determine_button_type(comp),
                    'style': self._extract_button_style(comp)
                }
                screen_data['ctas'].append(cta_info)
            
            # Navigation elements
            elif any(keyword in comp_name_lower for keyword in ['nav', 'tab', 'menu', 'back', 'next']):
                nav_info = {
                    'name': comp.name,
                    'type': 'navigation',
                    'text': self._extract_component_text(comp)
                }
                screen_data['navigation'].append(nav_info)
            
            # Lists and content areas
            elif any(keyword in comp_name_lower for keyword in ['list', 'item', 'card', 'row']):
                content_info = {
                    'name': comp.name,
                    'type': 'content',
                    'description': self._extract_component_text(comp)
                }
                screen_data['content_areas'].append(content_info)

            # Recursively analyze children
            for child in comp.children:
                analyze_component_tree(child, screen_data)

        # Process each page and screen
        for page in pages:
            # Check if page itself is a screen
            if self._is_screen_name(page.name) and page.name in screen_set:
                screen_data = self._init_screen_data(page.name)
                for comp in page.components:
                    analyze_component_tree(comp, screen_data)
                details.append(self._finalize_screen_analysis(screen_data))

            # Check top-level components that might be screens
            for comp in page.components:
                if self._is_screen_name(comp.name) and comp.name in screen_set:
                    screen_data = self._init_screen_data(comp.name)
                    analyze_component_tree(comp, screen_data)
                    details.append(self._finalize_screen_analysis(screen_data))

        # Deduplicate by screen name
        seen = set()
        unique_details = []
        for d in details:
            screen_name = d.get('screen')
            if screen_name and screen_name not in seen:
                unique_details.append(d)
                seen.add(screen_name)
        
        return unique_details

    def _init_screen_data(self, screen_name: str) -> Dict[str, Any]:
        """Initialize data structure for screen analysis."""
        return {
            'screen': screen_name,
            'all_texts': [],
            'field_labels': [],
            'placeholders': [],
            'validation_messages': [],
            'form_fields': [],
            'ctas': [],
            'navigation': [],
            'content_areas': []
        }
    
    def _determine_field_type(self, comp: FigmaComponent) -> str:
        """Determine the type of form field based on component properties and name."""
        name_lower = comp.name.lower() if comp.name else ''
        
        # Check for specific field types in the name
        if any(keyword in name_lower for keyword in ['email', 'mail']):
            return 'email'
        elif any(keyword in name_lower for keyword in ['password', 'pwd']):
            return 'password'
        elif any(keyword in name_lower for keyword in ['phone', 'mobile', 'tel']):
            return 'phone'
        elif any(keyword in name_lower for keyword in ['number', 'numeric', 'amount']):
            return 'number'
        elif any(keyword in name_lower for keyword in ['date', 'calendar']):
            return 'date'
        elif any(keyword in name_lower for keyword in ['search']):
            return 'search'
        elif any(keyword in name_lower for keyword in ['textarea', 'message', 'comment', 'description']):
            return 'textarea'
        elif any(keyword in name_lower for keyword in ['select', 'dropdown', 'picker']):
            return 'select'
        elif any(keyword in name_lower for keyword in ['checkbox', 'check']):
            return 'checkbox'
        elif any(keyword in name_lower for keyword in ['radio']):
            return 'radio'
        else:
            return 'text'
    
    def _extract_placeholder(self, comp: FigmaComponent) -> str:
        """Extract placeholder text from component."""
        # Look for placeholder in properties or children text
        placeholder_text = ''
        
        # Check component properties for placeholder-like content
        if comp.properties:
            chars = comp.properties.get('characters', '')
            if chars and any(keyword in chars.lower() for keyword in ['enter', 'type', 'placeholder']):
                placeholder_text = chars
        
        # Look in children for placeholder text
        for child in comp.children:
            if child.type == 'TEXT':
                text = child.properties.get('characters', '') or child.name
                if text and any(keyword in text.lower() for keyword in ['enter', 'type', 'placeholder']):
                    placeholder_text = text
                    break
        
        return placeholder_text.strip()
    
    def _extract_field_label(self, comp: FigmaComponent) -> str:
        """Extract label text associated with a form field."""
        # Look for nearby text components that could be labels
        label_text = ''
        
        # Check if the component name itself is descriptive
        if comp.name and not any(word in comp.name.lower() for word in ['input', 'field', 'text']):
            label_text = comp.name
        
        # Look in children for label-like text
        for child in comp.children:
            if child.type == 'TEXT':
                text = child.properties.get('characters', '') or child.name
                if text and len(text.strip()) > 0 and len(text.strip()) < 30:
                    # Likely a label if it's short and descriptive
                    if not any(keyword in text.lower() for keyword in ['enter', 'type', 'placeholder']):
                        label_text = text
                        break
        
        return label_text.strip()
    
    def _is_field_required(self, comp: FigmaComponent) -> bool:
        """Determine if a field is required based on indicators."""
        name_lower = comp.name.lower() if comp.name else ''
        
        # Check for asterisk or "required" in name or nearby text
        if '*' in comp.name or 'required' in name_lower or 'mandatory' in name_lower:
            return True
        
        # Check children for required indicators
        for child in comp.children:
            if child.type == 'TEXT':
                text = child.properties.get('characters', '') or child.name
                if text and ('*' in text or 'required' in text.lower()):
                    return True
        
        return False
    
    def _extract_validation_rules(self, comp: FigmaComponent) -> List[str]:
        """Extract validation rules or error messages for a field."""
        rules = []
        
        # Look for validation-related text in the component hierarchy
        def find_validation_text(component):
            if component.type == 'TEXT':
                text = component.properties.get('characters', '') or component.name
                if text:
                    text_lower = text.lower()
                    if any(keyword in text_lower for keyword in ['required', 'must', 'invalid', 'error', 'minimum', 'maximum']):
                        rules.append(text.strip())
            
            for child in component.children:
                find_validation_text(child)
        
        find_validation_text(comp)
        return rules
    
    def _extract_button_text(self, comp: FigmaComponent) -> str:
        """Extract the text content of a button or CTA."""
        button_text = ''
        
        # Check component name first
        if comp.name and not any(word in comp.name.lower() for word in ['button', 'btn', 'cta']):
            button_text = comp.name
        
        # Look for text in children
        for child in comp.children:
            if child.type == 'TEXT':
                text = child.properties.get('characters', '') or child.name
                if text and len(text.strip()) > 0:
                    button_text = text.strip()
                    break
        
        return button_text
    
    def _determine_button_type(self, comp: FigmaComponent) -> str:
        """Determine the type/purpose of a button."""
        name_lower = comp.name.lower() if comp.name else ''
        text = self._extract_button_text(comp).lower()
        
        # Determine button type based on name and text
        if any(keyword in name_lower or keyword in text for keyword in ['submit', 'send', 'save', 'confirm']):
            return 'primary'
        elif any(keyword in name_lower or keyword in text for keyword in ['cancel', 'back', 'close']):
            return 'secondary'
        elif any(keyword in name_lower or keyword in text for keyword in ['delete', 'remove']):
            return 'destructive'
        elif any(keyword in name_lower or keyword in text for keyword in ['next', 'continue', 'proceed']):
            return 'navigation'
        else:
            return 'default'
    
    def _extract_button_style(self, comp: FigmaComponent) -> str:
        """Extract style information for a button."""
        # This would ideally analyze the actual visual properties
        # For now, infer from name
        name_lower = comp.name.lower() if comp.name else ''
        
        if 'primary' in name_lower:
            return 'primary'
        elif 'secondary' in name_lower or 'outline' in name_lower:
            return 'secondary'
        elif 'text' in name_lower or 'link' in name_lower:
            return 'text'
        else:
            return 'default'
    
    def _extract_component_text(self, comp: FigmaComponent) -> str:
        """Extract all text content from a component."""
        texts = []
        
        def collect_text(component):
            if component.type == 'TEXT':
                text = component.properties.get('characters', '') or component.name
                if text and text.strip():
                    texts.append(text.strip())
            for child in component.children:
                collect_text(child)
        
        collect_text(comp)
        return ' | '.join(texts[:3])  # Limit to first 3 text elements
    
    def _analyze_japanese_text_in_design(self, pages: List[FigmaPage]) -> Dict[str, Any]:
        """Analyze Japanese text content throughout the design."""
        japanese_analysis = {
            "has_japanese": False,
            "japanese_screens": [],
            "japanese_text_nodes": [],
            "total_text_nodes": 0,
            "japanese_ratio": 0.0,
            "character_analysis": {
                "total_hiragana": 0,
                "total_katakana": 0,
                "total_kanji": 0,
                "total_latin": 0
            },
            "ui_element_analysis": {
                "japanese_buttons": [],
                "japanese_labels": [],
                "japanese_navigation": [],
                "japanese_content": []
            },
            "screen_language_breakdown": {}
        }
        
        for page in pages:
            page_japanese_count = 0
            page_total_text = 0
            
            def analyze_component_japanese(comp: FigmaComponent, screen_name: str = None):
                nonlocal page_japanese_count, page_total_text
                
                if comp.type == 'TEXT':
                    text = comp.properties.get('characters', '') or comp.name
                    if text and text.strip():
                        japanese_analysis["total_text_nodes"] += 1
                        page_total_text += 1
                        
                        # Analyze this specific text
                        text_analysis = classify_japanese_text_type(text.strip())
                        
                        if text_analysis["has_japanese"]:
                            page_japanese_count += 1
                            japanese_analysis["japanese_text_nodes"].append({
                                "text": text.strip(),
                                "component_name": comp.name,
                                "screen": screen_name or page.name,
                                "analysis": text_analysis,
                                "ui_element_type": self._classify_ui_element_type(comp, text.strip())
                            })
                            
                            # Update character counts
                            japanese_analysis["character_analysis"]["total_hiragana"] += text_analysis["total_chars"] * text_analysis["hiragana_ratio"]
                            japanese_analysis["character_analysis"]["total_katakana"] += text_analysis["total_chars"] * text_analysis["katakana_ratio"] 
                            japanese_analysis["character_analysis"]["total_kanji"] += text_analysis["total_chars"] * text_analysis["kanji_ratio"]
                            japanese_analysis["character_analysis"]["total_latin"] += text_analysis["total_chars"] * text_analysis["latin_ratio"]
                            
                            # Categorize by UI element type
                            ui_type = self._classify_ui_element_type(comp, text.strip())
                            if ui_type == "button":
                                japanese_analysis["ui_element_analysis"]["japanese_buttons"].append(text.strip())
                            elif ui_type == "label":
                                japanese_analysis["ui_element_analysis"]["japanese_labels"].append(text.strip())
                            elif ui_type == "navigation":
                                japanese_analysis["ui_element_analysis"]["japanese_navigation"].append(text.strip())
                            else:
                                japanese_analysis["ui_element_analysis"]["japanese_content"].append(text.strip())
                
                for child in comp.children:
                    analyze_component_japanese(child, screen_name)
            
            # Analyze all components in this page
            for comp in page.components:
                analyze_component_japanese(comp, page.name)
            
            # Track Japanese content per screen
            if page_total_text > 0:
                screen_japanese_ratio = page_japanese_count / page_total_text
                japanese_analysis["screen_language_breakdown"][page.name] = {
                    "japanese_text_count": page_japanese_count,
                    "total_text_count": page_total_text,
                    "japanese_ratio": screen_japanese_ratio,
                    "is_primarily_japanese": screen_japanese_ratio > 0.5
                }
                
                if screen_japanese_ratio > 0.3:  # If >30% Japanese, consider it a Japanese screen
                    japanese_analysis["japanese_screens"].append(page.name)
        
        # Calculate overall statistics
        if japanese_analysis["total_text_nodes"] > 0:
            japanese_analysis["japanese_ratio"] = len(japanese_analysis["japanese_text_nodes"]) / japanese_analysis["total_text_nodes"]
            japanese_analysis["has_japanese"] = len(japanese_analysis["japanese_text_nodes"]) > 0
        
        return japanese_analysis
    
    def _classify_ui_element_type(self, comp: FigmaComponent, text: str) -> str:
        """Classify what type of UI element this text belongs to."""
        comp_name_lower = comp.name.lower() if comp.name else ''
        text_lower = text.lower()
        
        # Button patterns
        if any(keyword in comp_name_lower for keyword in ['button', 'btn', 'cta', 'submit', 'action']):
            return "button"
        if any(keyword in text_lower for keyword in ['登録', '送信', 'ログイン', '次へ', '戻る', '確認', '完了', 'submit', 'login', 'next', 'back']):
            return "button"
        
        # Navigation patterns  
        if any(keyword in comp_name_lower for keyword in ['nav', 'menu', 'tab', 'breadcrumb']):
            return "navigation"
        if any(keyword in text_lower for keyword in ['ホーム', 'プロフィール', '設定', 'メニュー', 'home', 'profile', 'settings', 'menu']):
            return "navigation"
        
        # Label patterns
        if any(keyword in comp_name_lower for keyword in ['label', 'title', 'heading', 'caption']):
            return "label"
        if text.endswith(':') or text.endswith('：'):
            return "label"
        
        # Default to content
        return "content"
    
    def _finalize_screen_analysis(self, screen_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create final screen analysis with summary and organized data."""
        screen_name = screen_data['screen']
        
        # Generate natural, conversational description
        description = self._generate_natural_description(screen_data)
        
        # Generate summary based on extracted elements
        elements = []
        if screen_data['form_fields']:
            elements.append(f"{len(screen_data['form_fields'])} form fields")
        if screen_data['ctas']:
            elements.append(f"{len(screen_data['ctas'])} buttons/CTAs")
        if screen_data['navigation']:
            elements.append(f"{len(screen_data['navigation'])} navigation elements")
        
        # Create technical summary
        technical_summary = f"{screen_name}: "
        if elements:
            technical_summary += f"Contains {', '.join(elements)}."
        else:
            technical_summary += "UI screen with various interface elements."
        
        # Add key field information
        if screen_data['form_fields']:
            field_types = [f['type'] for f in screen_data['form_fields']]
            technical_summary += f" Field types: {', '.join(set(field_types))}."
        
        # Add key CTA information
        if screen_data['ctas']:
            cta_texts = [c['text'] for c in screen_data['ctas'] if c['text']][:3]
            if cta_texts:
                technical_summary += f" Key actions: {', '.join(cta_texts)}."
        
        return {
            'screen': screen_name,
            'summary': technical_summary,
            'description': description,  # New natural description
            'form_fields': screen_data['form_fields'],
            'ctas': screen_data['ctas'],
            'navigation': screen_data['navigation'],
            'content_areas': screen_data['content_areas'],
            'field_labels': screen_data['field_labels'],
            'placeholders': screen_data['placeholders'],
            'validation_messages': screen_data['validation_messages'],
            'all_texts': screen_data['all_texts'][:100],  # Limit for performance
            'field_count': len(screen_data['form_fields']),
            'cta_count': len(screen_data['ctas']),
            'nav_count': len(screen_data['navigation'])
        }
    
    def _generate_natural_description(self, screen_data: Dict[str, Any]) -> str:
        """Generate natural, conversational description of what user does on this screen."""
        screen_name = screen_data['screen'].lower()
        
        # Start building the description
        parts = []
        
        # Determine the main action/purpose from screen name and content
        main_action = self._determine_main_action(screen_name, screen_data)
        if main_action:
            parts.append(main_action)
        
        # Describe form fields in natural language
        if screen_data['form_fields']:
            field_description = self._describe_form_fields_naturally(screen_data['form_fields'])
            if field_description:
                parts.append(field_description)
        
        # Describe what happens next (CTAs and navigation)
        if screen_data['ctas'] or screen_data['navigation']:
            next_action = self._describe_next_actions(screen_data['ctas'], screen_data['navigation'])
            if next_action:
                parts.append(next_action)
        
        # Add any validation or error handling
        if screen_data['validation_messages']:
            validation_desc = self._describe_validation_naturally(screen_data['validation_messages'])
            if validation_desc:
                parts.append(validation_desc)
        
        # Join parts with appropriate connectors
        if not parts:
            return f"User interacts with {screen_name} interface"
        
        return "... ".join(parts) + "..."
    
    def _determine_main_action(self, screen_name: str, screen_data: Dict[str, Any]) -> str:
        """Determine the main action/purpose of the screen."""
        # Check for common screen patterns
        if any(word in screen_name for word in ['signup', 'sign up', 'register', 'registration']):
            return "User signs up"
        elif any(word in screen_name for word in ['login', 'sign in', 'signin']):
            return "User logs in"
        elif any(word in screen_name for word in ['profile', 'account', 'settings']):
            return "User manages profile"
        elif any(word in screen_name for word in ['payment', 'checkout', 'billing']):
            return "User makes payment"
        elif any(word in screen_name for word in ['search', 'find']):
            return "User searches"
        elif any(word in screen_name for word in ['chat', 'message', 'conversation']):
            return "User chats"
        elif any(word in screen_name for word in ['otp', 'verification', 'verify']):
            return "User verifies identity"
        elif any(word in screen_name for word in ['dashboard', 'home', 'main']):
            return "User views dashboard"
        elif any(word in screen_name for word in ['onboard', 'intro', 'welcome']):
            return "User goes through onboarding"
        else:
            # Try to infer from field types
            if screen_data['form_fields']:
                field_types = [f.get('type', '') for f in screen_data['form_fields']]
                if 'email' in field_types and 'password' in field_types:
                    return "User enters credentials"
                elif len(screen_data['form_fields']) >= 3:
                    return "User fills out form"
            return f"User interacts with {screen_name}"
    
    def _describe_form_fields_naturally(self, form_fields: List[Dict]) -> str:
        """Describe form fields in natural language."""
        if not form_fields:
            return ""
        
        field_descriptions = []
        
        for field in form_fields:
            field_type = field.get('type', 'text')
            label = field.get('label', '')
            name = field.get('name', '')
            required = field.get('required', False)
            
            # Extract meaningful field name
            field_name = label or name or f"{field_type} field"
            field_name = field_name.lower()
            
            # Convert technical names to natural language
            if 'email' in field_name:
                field_descriptions.append("email address")
            elif 'password' in field_name:
                field_descriptions.append("password")
            elif 'first' in field_name and 'name' in field_name:
                field_descriptions.append("first name")
            elif 'last' in field_name and 'name' in field_name:
                field_descriptions.append("last name")
            elif 'kana' in field_name:
                field_descriptions.append("kana name")
            elif 'phone' in field_name or 'mobile' in field_name:
                field_descriptions.append("phone number")
            elif 'address' in field_name:
                field_descriptions.append("address")
            elif 'date' in field_name or 'birth' in field_name:
                field_descriptions.append("date")
            elif 'age' in field_name:
                field_descriptions.append("age")
            elif 'gender' in field_name:
                field_descriptions.append("gender")
            elif 'code' in field_name or 'otp' in field_name:
                field_descriptions.append("verification code")
            elif field_type == 'checkbox':
                field_descriptions.append("agreement checkbox")
            elif field_type == 'select' or field_type == 'dropdown':
                field_descriptions.append(f"selection for {field_name}")
            else:
                # Use the field name as-is but clean it up
                clean_name = field_name.replace('_', ' ').replace('-', ' ')
                field_descriptions.append(clean_name)
        
        # Group similar fields
        if len(field_descriptions) <= 3:
            return f"using {', '.join(field_descriptions)}"
        else:
            # Show first few and summarize
            first_few = field_descriptions[:3]
            return f"using {', '.join(first_few)} and {len(field_descriptions) - 3} other fields"
    
    def _describe_next_actions(self, ctas: List[Dict], navigation: List[Dict]) -> str:
        """Describe what happens next based on CTAs and navigation."""
        actions = []
        
        # Process CTAs
        for cta in ctas:
            cta_text = cta.get('text', '').lower()
            cta_name = cta.get('name', '').lower()
            cta_type = cta.get('type', '')
            
            if any(word in cta_text or word in cta_name for word in ['next', 'continue', 'proceed']):
                actions.append("next step")
            elif any(word in cta_text or word in cta_name for word in ['submit', 'send', 'save']):
                actions.append("submit form")
            elif any(word in cta_text or word in cta_name for word in ['verify', 'confirm']):
                actions.append("verification")
            elif any(word in cta_text or word in cta_name for word in ['login', 'sign in']):
                actions.append("login")
            elif any(word in cta_text or word in cta_name for word in ['signup', 'register']):
                actions.append("registration")
            elif any(word in cta_text or word in cta_name for word in ['pay', 'purchase', 'buy']):
                actions.append("payment")
            elif any(word in cta_text or word in cta_name for word in ['otp', 'code']):
                actions.append("OTP verification")
            elif cta_text:
                actions.append(f"'{cta_text}' action")
        
        # Process navigation
        for nav in navigation:
            nav_text = nav.get('text', '').lower()
            nav_name = nav.get('name', '').lower()
            
            if any(word in nav_text or word in nav_name for word in ['back', 'previous']):
                actions.append("go back")
            elif any(word in nav_text or word in nav_name for word in ['skip']):
                actions.append("skip step")
            elif any(word in nav_text or word in nav_name for word in ['help', 'support']):
                actions.append("get help")
        
        if not actions:
            return ""
        
        if len(actions) == 1:
            return f"then {actions[0]}"
        else:
            return f"options to {' or '.join(actions)}"
    
    def _describe_validation_naturally(self, validation_messages: List[str]) -> str:
        """Describe validation rules in natural language."""
        if not validation_messages:
            return ""
        
        validation_types = []
        for msg in validation_messages:
            msg_lower = msg.lower()
            if 'required' in msg_lower:
                validation_types.append("required fields")
            elif 'email' in msg_lower:
                validation_types.append("email validation")
            elif 'password' in msg_lower:
                validation_types.append("password requirements")
            elif 'invalid' in msg_lower or 'error' in msg_lower:
                validation_types.append("error handling")
        
        if validation_types:
            unique_types = list(set(validation_types))
            return f"includes {', '.join(unique_types)}"
        
        return ""
    
    def _calculate_complexity_score(self, pages: List[FigmaPage], ui_components: List[str]) -> float:
        """Calculate design complexity score (0-10)."""
        score = 0.0
        
        # Base score from number of pages
        score += min(len(pages) * 1.5, 3.0)
        
        # Score from UI components
        score += min(len(ui_components) * 0.2, 4.0)
        
        # Score from component nesting depth
        max_depth = 0
        for page in pages:
            depth = self._calculate_max_depth(page.components)
            max_depth = max(max_depth, depth)
        
        score += min(max_depth * 0.5, 3.0)
        
        return min(score, 10.0)
    
    def _calculate_max_depth(self, components: List[FigmaComponent], current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of components."""
        if not components:
            return current_depth
        
        max_depth = current_depth
        for comp in components:
            depth = self._calculate_max_depth(comp.children, current_depth + 1)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _generate_implementation_notes(self, ui_components: List[str], screens: List[str]) -> List[str]:
        """Generate implementation notes based on design analysis."""
        notes = []
        
        if len(screens) > 5:
            notes.append("Complex multi-screen application - consider navigation architecture")
        
        if any('form' in comp.lower() for comp in ui_components):
            notes.append("Forms detected - implement validation and error handling")
        
        if any('list' in comp.lower() for comp in ui_components):
            notes.append("List components detected - consider pagination and performance")
        
        if any('modal' in comp.lower() or 'dialog' in comp.lower() for comp in ui_components):
            notes.append("Modal dialogs detected - ensure proper focus management")
        
        return notes
    
    def _analyze_accessibility(self, pages: List[FigmaPage]) -> List[str]:
        """Analyze accessibility considerations from design."""
        considerations = []
        
        # Check for common accessibility patterns
        has_buttons = False
        has_forms = False
        has_images = False
        
        for page in pages:
            for comp in page.components:
                name_lower = comp.name.lower()
                
                if 'button' in name_lower:
                    has_buttons = True
                if 'form' in name_lower or 'input' in name_lower:
                    has_forms = True
                if 'image' in name_lower or 'photo' in name_lower:
                    has_images = True
        
        if has_buttons:
            considerations.append("Ensure buttons have accessible labels and keyboard navigation")
        
        if has_forms:
            considerations.append("Form inputs need proper labels and error messaging")
        
        if has_images:
            considerations.append("Images require alt text for screen readers")
        
        considerations.append("Verify color contrast meets WCAG guidelines")
        considerations.append("Ensure touch targets are at least 44px for mobile")
        
        return considerations
    
    def get_design_context_for_analysis(self, figma_design: FigmaDesign) -> Dict[str, Any]:
        """Get design context formatted for analysis integration."""
        # Extract aggregate form field information
        total_form_fields = 0
        total_ctas = 0
        total_nav_elements = 0
        field_types = set()
        cta_types = set()
        
        for screen in figma_design.screen_details:
            # Add type checking to prevent 'str' object has no attribute 'get' error
            if not isinstance(screen, dict):
                continue
                
            total_form_fields += screen.get('field_count', 0)
            total_ctas += screen.get('cta_count', 0)
            total_nav_elements += screen.get('nav_count', 0)
            
            # Collect field types
            for field in screen.get('form_fields', []):
                field_types.add(field.get('type', 'unknown'))
            
            # Collect CTA types
            for cta in screen.get('ctas', []):
                cta_types.add(cta.get('type', 'default'))
        
        return {
            'design_name': figma_design.name,
            'design_complexity': figma_design.complexity_score,
            'screens': figma_design.screens,
            'ui_components': figma_design.ui_components,
            'user_flows': figma_design.user_flows,
            'implementation_notes': figma_design.implementation_notes,
            'accessibility_considerations': figma_design.accessibility_considerations,
            'design_tokens': figma_design.design_tokens,
            'pages_count': len(figma_design.pages),
            'components_count': len(figma_design.ui_components),
            'screen_details': figma_design.screen_details,
            # Enhanced form field context
            'total_form_fields': total_form_fields,
            'total_ctas': total_ctas,
            'total_nav_elements': total_nav_elements,
            'field_types': list(field_types),
            'cta_types': list(cta_types),
            'screens_with_forms': len([s for s in figma_design.screen_details if isinstance(s, dict) and s.get('field_count', 0) > 0]),
            'has_form_screens': total_form_fields > 0,
            'has_complex_forms': any(isinstance(s, dict) and s.get('field_count', 0) >= 5 for s in figma_design.screen_details),
            
            # Japanese text analysis
            'has_japanese_content': figma_design.japanese_text_analysis.get('has_japanese', False) if figma_design.japanese_text_analysis else False,
            'japanese_screens': figma_design.japanese_screens or [],
            'japanese_text_nodes': figma_design.total_japanese_text_nodes or 0,
            'japanese_ratio': figma_design.japanese_text_analysis.get('japanese_ratio', 0) if figma_design.japanese_text_analysis else 0,
            'japanese_ui_elements': figma_design.japanese_text_analysis.get('ui_element_analysis', {}) if figma_design.japanese_text_analysis else {},
            'japanese_character_breakdown': figma_design.japanese_text_analysis.get('character_analysis', {}) if figma_design.japanese_text_analysis else {},
            'screen_language_breakdown': figma_design.japanese_text_analysis.get('screen_language_breakdown', {}) if figma_design.japanese_text_analysis else {},
        }

# Example usage
if __name__ == "__main__":
    figma = FigmaIntegration()
    
    # Test URL parsing
    test_url = "https://www.figma.com/file/abc123def456/Mobile-App-Design"
    file_key = figma.extract_figma_file_key(test_url)
    print(f"Extracted file key: {file_key}")
    
    print("🎨 Figma Integration System Ready")
    print("Set FIGMA_ACCESS_TOKEN environment variable to enable API access")
    def _capture_screen_screenshots(self, file_id: str, screens: List[Dict[str, Any]]) -> Dict[str, str]:
        """Capture screenshots of individual screens for GPT-4 Vision analysis."""
        screenshots = {}
        
        if not self.figma_token:
            print("⚠️ No Figma token available for screenshot capture")
            return screenshots
        
        try:
            # Get the file's images endpoint
            images_url = f"https://api.figma.com/v1/images/{file_id}"
            
            # Prepare node IDs for each screen
            node_ids = []
            screen_names = []
            
            for screen in screens:
                if isinstance(screen, dict) and 'id' in screen:
                    node_ids.append(screen['id'])
                    screen_names.append(screen.get('name', f'Screen_{len(screen_names)}'))
            
            if not node_ids:
                print("⚠️ No valid screen nodes found for screenshot capture")
                return screenshots
            
            # Request images from Figma API
            params = {
                'ids': ','.join(node_ids),
                'format': 'png',
                'scale': 2  # High resolution for better analysis
            }
            
            headers = {
                'X-Figma-Token': self.figma_token
            }
            
            response = requests.get(images_url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                images = data.get('images', {})
                
                # Save screenshots to temporary files
                import tempfile
                import os
                
                temp_dir = tempfile.mkdtemp(prefix='figma_screenshots_')
                
                for i, node_id in enumerate(node_ids):
                    if node_id in images and images[node_id]:
                        image_url = images[node_id]
                        
                        # Download the image
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            # Save to temporary file
                            screen_name = screen_names[i]
                            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', screen_name)
                            screenshot_path = os.path.join(temp_dir, f"{safe_name}.png")
                            
                            with open(screenshot_path, 'wb') as f:
                                f.write(img_response.content)
                            
                            screenshots[screen_name] = screenshot_path
                            print(f"✅ Captured screenshot for {screen_name}")
                        else:
                            print(f"⚠️ Failed to download screenshot for {screen_name}")
                    else:
                        print(f"⚠️ No image URL available for {screen_names[i]}")
                
                print(f"📸 Captured {len(screenshots)} screenshots in {temp_dir}")
                
            else:
                print(f"⚠️ Failed to get screenshots from Figma API: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error capturing screenshots: {e}")
        
        return screenshots
