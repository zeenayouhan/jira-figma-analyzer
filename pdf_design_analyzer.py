#!/usr/bin/env python3
"""
PDF Design Analysis System

This system analyzes PDF design files (wireframes, mockups, design exports)
and extracts design elements, screens, and UI components to enhance
the Jira ticket analysis with visual design context.
"""

import os
import json
import re
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile

# PDF processing
try:
    import PyPDF2
    from PIL import Image
    import fitz  # PyMuPDF for better PDF processing
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PDF processing libraries not available. Install with: pip install PyPDF2 PyMuPDF pillow")

# OCR for text extraction from images
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR not available. Install with: pip install pytesseract")

@dataclass
class PDFDesignElement:
    """Represents a design element found in PDF."""
    element_type: str  # 'screen', 'component', 'text', 'image', 'wireframe'
    name: str
    page_number: int
    position: Dict[str, float]  # x, y, width, height
    properties: Dict[str, Any]
    text_content: str
    confidence: float

@dataclass
class PDFDesignPage:
    """Represents a PDF page with design content."""
    page_number: int
    page_size: Dict[str, float]  # width, height
    elements: List[PDFDesignElement]
    extracted_text: str
    has_wireframes: bool
    has_mockups: bool
    screen_count: int

@dataclass
class PDFDesignAnalysis:
    """Represents complete PDF design analysis."""
    file_name: str
    file_path: str
    total_pages: int
    pages: List[PDFDesignPage]
    
    # Extracted design insights
    screens: List[str]
    ui_components: List[str]
    user_flows: List[str]
    wireframes: List[str]
    mockups: List[str]
    
    # Text analysis
    extracted_text: str
    design_notes: List[str]
    requirements: List[str]
    
    # Analysis results
    complexity_score: float
    design_type: str  # 'wireframes', 'mockups', 'mixed', 'documentation'
    implementation_notes: List[str]
    accessibility_considerations: List[str]
    
    processing_date: str

class PDFDesignAnalyzer:
    """Main class for PDF design analysis."""
    
    def __init__(self):
        self.screen_keywords = [
            'login', 'signup', 'dashboard', 'home', 'profile', 'settings',
            'search', 'results', 'detail', 'list', 'form', 'checkout',
            'cart', 'payment', 'account', 'overview', 'summary', 'onboarding',
            'advisor', 'client', 'appointment', 'calendar', 'booking',
            'portfolio', 'investment', 'financial', 'banking'
        ]
        
        self.component_keywords = [
            'button', 'input', 'field', 'dropdown', 'select', 'checkbox',
            'radio', 'toggle', 'slider', 'card', 'modal', 'dialog',
            'header', 'footer', 'nav', 'menu', 'tab', 'sidebar',
            'toolbar', 'breadcrumb', 'pagination', 'table', 'chart',
            'graph', 'avatar', 'badge', 'chip', 'tag', 'icon'
        ]
        
        self.wireframe_indicators = [
            'wireframe', 'mockup', 'prototype', 'sketch', 'draft',
            'layout', 'structure', 'framework', 'placeholder'
        ]
        
        print("📄 PDF Design Analyzer initialized")
    
    def analyze_pdf_design(self, pdf_path: str) -> Optional[PDFDesignAnalysis]:
        """Analyze a PDF design file."""
        if not PDF_AVAILABLE:
            print("❌ PDF processing libraries not available")
            return None
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return None
        
        try:
            print(f"📥 Analyzing PDF design: {os.path.basename(pdf_path)}")
            
            # Open PDF with PyMuPDF for better processing
            doc = fitz.open(pdf_path)
            pages = []
            all_text = ""
            
            for page_num in range(doc.page_count):
                try:
                    page = doc[page_num]
                    page_analysis = self._analyze_pdf_page(page, page_num + 1)
                    pages.append(page_analysis)
                    all_text += page_analysis.extracted_text + "\n"
                except Exception as page_error:
                    print(f"   ⚠️ Error processing page {page_num + 1}: {page_error}")
                    # Continue with other pages
                    continue
            
            if not pages:
                print(f"   ❌ No pages could be processed from PDF")
                doc.close()
                return None
            
            # Extract design insights
            screens = self._extract_screens(pages, all_text)
            ui_components = self._extract_ui_components(pages, all_text)
            user_flows = self._extract_user_flows(pages, all_text)
            wireframes = self._extract_wireframes(pages, all_text)
            mockups = self._extract_mockups(pages, all_text)
            
            # Extract text insights
            design_notes = self._extract_design_notes(all_text)
            requirements = self._extract_requirements(all_text)
            
            # Calculate analysis results
            complexity_score = self._calculate_complexity_score(pages, screens, ui_components)
            design_type = self._determine_design_type(pages, wireframes, mockups)
            implementation_notes = self._generate_implementation_notes(screens, ui_components, design_type)
            accessibility_considerations = self._analyze_accessibility(pages, all_text)
            
            # Close document after all processing is complete
            doc.close()
            
            analysis = PDFDesignAnalysis(
                file_name=os.path.basename(pdf_path),
                file_path=pdf_path,
                total_pages=doc.page_count,
                pages=pages,
                
                screens=screens,
                ui_components=ui_components,
                user_flows=user_flows,
                wireframes=wireframes,
                mockups=mockups,
                
                extracted_text=all_text,
                design_notes=design_notes,
                requirements=requirements,
                
                complexity_score=complexity_score,
                design_type=design_type,
                implementation_notes=implementation_notes,
                accessibility_considerations=accessibility_considerations,
                
                processing_date=datetime.now().isoformat()
            )
            
            print(f"✅ PDF design analyzed: {analysis.file_name}")
            print(f"   📄 Pages: {analysis.total_pages}")
            print(f"   📱 Screens: {len(screens)}")
            print(f"   🧩 UI Components: {len(ui_components)}")
            print(f"   🎨 Design Type: {design_type}")
            print(f"   ⚡ Complexity Score: {complexity_score:.1f}/10")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing PDF design: {e}")
            return None
    
    def _analyze_pdf_page(self, page, page_number: int) -> PDFDesignPage:
        """Analyze a single PDF page."""
        # Extract text
        text = page.get_text()
        
        # Get page dimensions
        rect = page.rect
        page_size = {
            'width': rect.width,
            'height': rect.height
        }
        
        # Extract elements (text blocks, images, etc.)
        elements = []
        
        # Get text blocks with positions
        text_blocks = page.get_text("dict")
        for block in text_blocks.get("blocks", []):
            if "lines" in block:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        element = PDFDesignElement(
                            element_type="text",
                            name=span["text"].strip(),
                            page_number=page_number,
                            position={
                                'x': span["bbox"][0],
                                'y': span["bbox"][1],
                                'width': span["bbox"][2] - span["bbox"][0],
                                'height': span["bbox"][3] - span["bbox"][1]
                            },
                            properties={
                                'font': span.get("font", ""),
                                'size': span.get("size", 0),
                                'flags': span.get("flags", 0)
                            },
                            text_content=span["text"].strip(),
                            confidence=1.0
                        )
                        if element.text_content:
                            elements.append(element)
        
        # Get images
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            try:
                img_rect = page.get_image_bbox(img[7])  # Get image bbox
                element = PDFDesignElement(
                    element_type="image",
                    name=f"Image_{img_index + 1}_Page_{page_number}",  # Make names unique
                    page_number=page_number,
                    position={
                        'x': img_rect.x0,
                        'y': img_rect.y0,
                        'width': img_rect.width,
                        'height': img_rect.height
                    },
                    properties={
                        'xref': img[0],
                        'smask': img[1],
                        'width': img[2],
                        'height': img[3]
                    },
                    text_content="",
                    confidence=0.8
                )
                elements.append(element)
            except Exception as e:
                # Skip problematic images but continue processing
                print(f"   ⚠️ Skipping image {img_index + 1} on page {page_number}: {e}")
                continue
        
        # Analyze page content
        text_lower = text.lower()
        has_wireframes = any(keyword in text_lower for keyword in self.wireframe_indicators)
        has_mockups = not has_wireframes and len(image_list) > 0  # Images likely indicate mockups
        
        # Count potential screens
        screen_count = sum(1 for keyword in self.screen_keywords if keyword in text_lower)
        
        return PDFDesignPage(
            page_number=page_number,
            page_size=page_size,
            elements=elements,
            extracted_text=text,
            has_wireframes=has_wireframes,
            has_mockups=has_mockups,
            screen_count=screen_count
        )
    
    def _extract_screens(self, pages: List[PDFDesignPage], all_text: str) -> List[str]:
        """Extract screen names from PDF content."""
        screens = set()
        
        # Look for screen keywords in text
        text_lower = all_text.lower()
        for keyword in self.screen_keywords:
            if keyword in text_lower:
                screens.add(keyword.title() + " Screen")
        
        # Look for screen patterns in text elements
        for page in pages:
            for element in page.elements:
                if element.element_type == "text" and element.text_content:
                    text = element.text_content.lower()
                    
                    # Look for "X Screen" or "X Page" patterns
                    screen_patterns = [
                        r'(\w+)\s+screen',
                        r'(\w+)\s+page',
                        r'(\w+)\s+view',
                        r'(\w+)\s+dashboard'
                    ]
                    
                    for pattern in screen_patterns:
                        matches = re.findall(pattern, text)
                        for match in matches:
                            if len(match) > 2:  # Avoid single letters
                                screens.add(match.title() + " Screen")
        
        return sorted(list(screens))
    
    def _extract_ui_components(self, pages: List[PDFDesignPage], all_text: str) -> List[str]:
        """Extract UI component names from PDF content."""
        components = set()
        
        # Look for component keywords
        text_lower = all_text.lower()
        for keyword in self.component_keywords:
            if keyword in text_lower:
                components.add(keyword.title())
        
        # Look for component patterns in text
        component_patterns = [
            r'(\w+)\s+button',
            r'(\w+)\s+field',
            r'(\w+)\s+input',
            r'(\w+)\s+dropdown',
            r'(\w+)\s+menu'
        ]
        
        for pattern in component_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match) > 2:
                    components.add(match.title() + "Component")
        
        return sorted(list(components))
    
    def _extract_user_flows(self, pages: List[PDFDesignPage], all_text: str) -> List[str]:
        """Extract user flow information from PDF content."""
        flows = []
        
        # Look for flow indicators
        flow_patterns = [
            r'user flow:?\s*([^\n]+)',
            r'flow:?\s*([^\n]+)',
            r'journey:?\s*([^\n]+)',
            r'process:?\s*([^\n]+)',
            r'workflow:?\s*([^\n]+)'
        ]
        
        text_lower = all_text.lower()
        for pattern in flow_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 5:
                    flows.append(f"Flow: {match.strip().title()}")
        
        # Look for sequential indicators
        if any(word in text_lower for word in ['step 1', 'step 2', 'first', 'next', 'then', 'finally']):
            flows.append("Sequential User Flow identified")
        
        return flows
    
    def _extract_wireframes(self, pages: List[PDFDesignPage], all_text: str) -> List[str]:
        """Extract wireframe information."""
        wireframes = []
        
        for page in pages:
            if page.has_wireframes:
                wireframes.append(f"Page {page.page_number}: Wireframe Content")
        
        # Look for wireframe mentions in text
        wireframe_mentions = re.findall(r'wireframe[^.\n]*', all_text.lower())
        for mention in wireframe_mentions:
            if len(mention.strip()) > 10:
                wireframes.append(f"Wireframe: {mention.strip().title()}")
        
        return wireframes
    
    def _extract_mockups(self, pages: List[PDFDesignPage], all_text: str) -> List[str]:
        """Extract mockup information."""
        mockups = []
        
        for page in pages:
            if page.has_mockups:
                mockups.append(f"Page {page.page_number}: High-Fidelity Mockup")
        
        # Look for mockup mentions in text
        mockup_mentions = re.findall(r'mockup[^.\n]*', all_text.lower())
        for mention in mockup_mentions:
            if len(mention.strip()) > 10:
                mockups.append(f"Mockup: {mention.strip().title()}")
        
        return mockups
    
    def _extract_design_notes(self, text: str) -> List[str]:
        """Extract design notes and annotations."""
        notes = []
        
        # Look for note patterns
        note_patterns = [
            r'note:?\s*([^\n]+)',
            r'annotation:?\s*([^\n]+)',
            r'comment:?\s*([^\n]+)',
            r'requirement:?\s*([^\n]+)',
            r'todo:?\s*([^\n]+)'
        ]
        
        text_lower = text.lower()
        for pattern in note_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 5:
                    notes.append(match.strip().capitalize())
        
        return notes[:10]  # Limit to top 10 notes
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract functional requirements from design."""
        requirements = []
        
        # Look for requirement patterns
        req_patterns = [
            r'must\s+([^.\n]+)',
            r'should\s+([^.\n]+)',
            r'needs? to\s+([^.\n]+)',
            r'required:?\s*([^\n]+)',
            r'functional:?\s*([^\n]+)'
        ]
        
        text_lower = text.lower()
        for pattern in req_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 10:
                    requirements.append(f"Must {match.strip()}")
        
        return requirements[:8]  # Limit to top 8 requirements
    
    def _calculate_complexity_score(self, pages: List[PDFDesignPage], screens: List[str], components: List[str]) -> float:
        """Calculate design complexity score (0-10)."""
        score = 0.0
        
        # Base score from pages
        score += min(len(pages) * 1.0, 2.0)
        
        # Score from screens
        score += min(len(screens) * 0.8, 3.0)
        
        # Score from components
        score += min(len(components) * 0.3, 3.0)
        
        # Score from page complexity
        total_elements = sum(len(page.elements) for page in pages)
        score += min(total_elements * 0.01, 2.0)
        
        return min(score, 10.0)
    
    def _determine_design_type(self, pages: List[PDFDesignPage], wireframes: List[str], mockups: List[str]) -> str:
        """Determine the type of design document."""
        has_wireframes = len(wireframes) > 0
        has_mockups = len(mockups) > 0
        
        if has_wireframes and has_mockups:
            return "mixed"
        elif has_wireframes:
            return "wireframes"
        elif has_mockups:
            return "mockups"
        else:
            return "documentation"
    
    def _generate_implementation_notes(self, screens: List[str], components: List[str], design_type: str) -> List[str]:
        """Generate implementation notes based on PDF analysis."""
        notes = []
        
        if len(screens) > 5:
            notes.append("Multiple screens detected - plan navigation architecture")
        
        if design_type == "wireframes":
            notes.append("Wireframe designs - need visual design phase before implementation")
        elif design_type == "mockups":
            notes.append("High-fidelity designs - ready for direct implementation")
        
        if any("form" in comp.lower() for comp in components):
            notes.append("Form components detected - implement validation logic")
        
        if any("list" in comp.lower() for comp in components):
            notes.append("List components detected - consider data pagination")
        
        notes.append("PDF analysis complete - verify design details with stakeholders")
        
        return notes
    
    def _analyze_accessibility(self, pages: List[PDFDesignPage], text: str) -> List[str]:
        """Analyze accessibility considerations from PDF design."""
        considerations = []
        
        # Check for accessibility mentions
        if any(word in text.lower() for word in ['accessibility', 'a11y', 'wcag', 'aria']):
            considerations.append("Accessibility requirements mentioned in design")
        
        # Standard accessibility considerations
        considerations.extend([
            "Ensure color contrast meets WCAG 2.1 AA standards",
            "Implement keyboard navigation for all interactive elements",
            "Add appropriate ARIA labels for screen readers",
            "Verify touch targets are minimum 44px for mobile",
            "Test with assistive technologies"
        ])
        
        return considerations
    
    def get_design_context_for_analysis(self, pdf_analysis: PDFDesignAnalysis) -> Dict[str, Any]:
        """Get PDF design context formatted for analysis integration."""
        return {
            'design_name': pdf_analysis.file_name,
            'design_type': pdf_analysis.design_type,
            'design_complexity': pdf_analysis.complexity_score,
            'pages_count': pdf_analysis.total_pages,
            'screens': pdf_analysis.screens,
            'ui_components': pdf_analysis.ui_components,
            'user_flows': pdf_analysis.user_flows,
            'wireframes': pdf_analysis.wireframes,
            'mockups': pdf_analysis.mockups,
            'design_notes': pdf_analysis.design_notes,
            'requirements': pdf_analysis.requirements,
            'implementation_notes': pdf_analysis.implementation_notes,
            'accessibility_considerations': pdf_analysis.accessibility_considerations,
            'extracted_text_length': len(pdf_analysis.extracted_text)
        }

# Example usage
if __name__ == "__main__":
    analyzer = PDFDesignAnalyzer()
    
    # Test with example PDF
    test_pdf = "/path/to/design.pdf"
    if os.path.exists(test_pdf):
        analysis = analyzer.analyze_pdf_design(test_pdf)
        if analysis:
            context = analyzer.get_design_context_for_analysis(analysis)
            print(json.dumps(context, indent=2))
    
    print("📄 PDF Design Analyzer Ready")
    print("Drop PDF design files for analysis!") 