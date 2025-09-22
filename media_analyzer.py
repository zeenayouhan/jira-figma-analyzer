#!/usr/bin/env python3
"""
Media Analyzer for Jira-Figma Analyzer

This module handles analysis of images and videos attached to tickets,
extracting relevant information to enhance ticket analysis context.
"""

import os
import base64
import json
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import hashlib
from datetime import datetime

# Image processing
try:
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    import numpy as np
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

# Optional OCR
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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

@dataclass
class MediaAnalysis:
    """Results from media analysis."""
    media_id: str
    filename: str
    media_type: str  # 'image' or 'video'
    file_size: int
    dimensions: Tuple[int, int]
    
    # Extracted content
    extracted_text: str
    detected_objects: List[str]
    ui_elements: List[str]
    color_palette: List[str]
    
    # Analysis insights
    content_type: str  # 'mockup', 'wireframe', 'screenshot', 'workflow', 'other'
    complexity_score: float
    design_elements: List[str]
    user_actions: List[str]
    
    # Video-specific (if applicable)
    duration: Optional[float]
    frame_count: Optional[int]
    key_frames: Optional[List[str]]
    
    # Metadata
    analysis_date: str
    confidence_score: float
    
    # Japanese text analysis
    has_japanese_text: bool = False
    japanese_text_ratio: float = 0.0
    japanese_characters: List[str] = None

class MediaAnalyzer:
    """Main class for analyzing images and videos in ticket context."""
    
    def __init__(self):
        """Initialize the media analyzer."""
        self.temp_dir = Path(tempfile.gettempdir()) / "jira_media_analysis"
        self.temp_dir.mkdir(exist_ok=True)
        
        if not VISION_AVAILABLE:
            print("⚠️ Image processing libraries not available. Install with: pip install pillow opencv-python")
        
        if not OCR_AVAILABLE:
            print("⚠️ OCR not available. Install with: pip install pytesseract")
        else:
            print("✅ Media Analyzer initialized with OCR support")
        
        print("📸 Media Analyzer initialized")
    
    def analyze_media_file(self, file_path: str) -> Optional[MediaAnalysis]:
        """Analyze a media file (image or video)."""
        if not os.path.exists(file_path):
            print(f"❌ Media file not found: {file_path}")
            return None
        
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        # Determine media type
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        
        if file_extension in image_extensions:
            return self._analyze_image(file_path)
        elif file_extension in video_extensions:
            return self._analyze_video(file_path)
        else:
            print(f"❌ Unsupported media format: {file_extension}")
            return None
    
    def _analyze_image(self, image_path: Path) -> Optional[MediaAnalysis]:
        """Analyze an image file."""
        if not VISION_AVAILABLE:
            print("❌ Vision processing not available")
            return None
        
        try:
            print(f"📸 Analyzing image: {image_path.name}")
            
            # Load image
            image = Image.open(image_path)
            width, height = image.size
            file_size = image_path.stat().st_size
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            extracted_text = self._extract_text_from_image(image)
            
            # Analyze Japanese text content
            has_japanese = detect_japanese_text(extracted_text) if extracted_text else False
            japanese_ratio = 0.0
            japanese_chars = []
            
            if has_japanese and extracted_text:
                # Calculate Japanese character ratio
                total_chars = len(extracted_text)
                japanese_char_count = 0
                
                for char in extracted_text:
                    if detect_japanese_text(char):
                        japanese_char_count += 1
                        if char not in japanese_chars:
                            japanese_chars.append(char)
                
                japanese_ratio = japanese_char_count / total_chars if total_chars > 0 else 0.0
                print(f"🇯🇵 Japanese text detected: {japanese_char_count}/{total_chars} characters ({japanese_ratio:.1%})")
            
            # Analyze UI elements
            ui_elements = self._detect_ui_elements(image)
            
            # Extract color palette
            color_palette = self._extract_color_palette(image)
            
            # Detect content type
            content_type = self._classify_image_content(image, extracted_text, ui_elements)
            
            # Calculate complexity
            complexity_score = self._calculate_image_complexity(image, ui_elements, extracted_text)
            
            # Detect design elements
            design_elements = self._detect_design_elements(image, ui_elements, extracted_text)
            
            # Identify user actions
            user_actions = self._identify_user_actions(extracted_text, ui_elements)
            
            # Generate media ID
            media_id = self._generate_media_id(image_path.name, extracted_text)
            
            return MediaAnalysis(
                media_id=media_id,
                filename=image_path.name,
                media_type='image',
                file_size=file_size,
                dimensions=(width, height),
                extracted_text=extracted_text,
                detected_objects=[],  # Could be enhanced with object detection
                ui_elements=ui_elements,
                color_palette=color_palette,
                content_type=content_type,
                complexity_score=complexity_score,
                design_elements=design_elements,
                user_actions=user_actions,
                duration=None,
                frame_count=None,
                key_frames=None,
                analysis_date=datetime.now().isoformat(),
                confidence_score=0.8,  # Base confidence
                
                # Japanese text analysis
                has_japanese_text=has_japanese,
                japanese_text_ratio=japanese_ratio,
                japanese_characters=japanese_chars
            )
            
        except Exception as e:
            print(f"❌ Error analyzing image {image_path.name}: {e}")
            return None
    
    def _analyze_video(self, video_path: Path) -> Optional[MediaAnalysis]:
        """Analyze a video file."""
        if not VISION_AVAILABLE:
            print("❌ Vision processing not available")
            return None
        
        try:
            print(f"🎥 Analyzing video: {video_path.name}")
            
            # Open video
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                print(f"❌ Could not open video: {video_path.name}")
                return None
            
            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            file_size = video_path.stat().st_size
            
            # Extract key frames for analysis
            key_frames = self._extract_key_frames(cap, frame_count)
            
            # Analyze key frames
            all_text = ""
            all_ui_elements = []
            all_design_elements = []
            all_user_actions = []
            
            for i, frame in enumerate(key_frames):
                # Convert frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Extract information from this frame
                frame_text = self._extract_text_from_image(pil_image)
                frame_ui = self._detect_ui_elements(pil_image)
                frame_design = self._detect_design_elements(pil_image, frame_ui, frame_text)
                frame_actions = self._identify_user_actions(frame_text, frame_ui)
                
                all_text += frame_text + " "
                all_ui_elements.extend(frame_ui)
                all_design_elements.extend(frame_design)
                all_user_actions.extend(frame_actions)
            
            # Clean up duplicates
            all_ui_elements = list(set(all_ui_elements))
            all_design_elements = list(set(all_design_elements))
            all_user_actions = list(set(all_user_actions))
            
            # Determine content type
            content_type = self._classify_video_content(all_text, all_ui_elements)
            
            # Calculate complexity
            complexity_score = self._calculate_video_complexity(key_frames, all_ui_elements, all_text)
            
            # Generate media ID
            media_id = self._generate_media_id(video_path.name, all_text)
            
            cap.release()
            
            return MediaAnalysis(
                media_id=media_id,
                filename=video_path.name,
                media_type='video',
                file_size=file_size,
                dimensions=(width, height),
                extracted_text=all_text.strip(),
                detected_objects=[],
                ui_elements=all_ui_elements,
                color_palette=[],  # Could extract from key frames
                content_type=content_type,
                complexity_score=complexity_score,
                design_elements=all_design_elements,
                user_actions=all_user_actions,
                duration=duration,
                frame_count=frame_count,
                key_frames=[f"frame_{i}" for i in range(len(key_frames))],
                analysis_date=datetime.now().isoformat(),
                confidence_score=0.7  # Lower confidence for video analysis
            )
            
        except Exception as e:
            print(f"❌ Error analyzing video {video_path.name}: {e}")
            return None
    
    def _extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using OCR with Japanese support."""
        if not OCR_AVAILABLE:
            return ""
        
        try:
            # First try Japanese + English OCR
            try:
                japanese_text = pytesseract.image_to_string(image, lang='jpn+eng')
                if japanese_text.strip():
                    cleaned_text = ' '.join(japanese_text.split())
                    print(f"📝 Japanese OCR extracted: {len(cleaned_text)} characters")
                    return cleaned_text
            except:
                print("ℹ️ Japanese OCR not available, falling back to English")
            
            # Fallback to English OCR
            text = pytesseract.image_to_string(image, lang='eng')
            cleaned_text = ' '.join(text.split())
            
            if cleaned_text.strip():
                print(f"📝 English OCR extracted: {len(cleaned_text)} characters")
            
            return cleaned_text
        except Exception as e:
            print(f"⚠️ OCR failed: {e}")
            return ""
    
    def _detect_ui_elements(self, image: Image.Image) -> List[str]:
        """Detect UI elements in the image using simple heuristics."""
        ui_elements = []
        
        # Convert to numpy array for analysis
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Detect rectangles (could be buttons, forms, etc.)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangular_shapes = 0
        for contour in contours:
            # Approximate contour
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # If it's roughly rectangular
            if len(approx) == 4:
                rectangular_shapes += 1
        
        # Infer UI elements based on shape analysis
        if rectangular_shapes > 10:
            ui_elements.extend(['buttons', 'form_fields', 'cards'])
        elif rectangular_shapes > 5:
            ui_elements.extend(['buttons', 'containers'])
        elif rectangular_shapes > 0:
            ui_elements.append('layout_elements')
        
        return ui_elements
    
    def _extract_color_palette(self, image: Image.Image) -> List[str]:
        """Extract dominant colors from the image."""
        try:
            # Resize image for faster processing
            small_image = image.resize((50, 50))
            colors = small_image.getcolors(maxcolors=256*256*256)
            
            if colors:
                # Sort by frequency and get top colors
                colors.sort(reverse=True)
                dominant_colors = []
                
                for count, color in colors[:5]:  # Top 5 colors
                    if isinstance(color, tuple) and len(color) >= 3:
                        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                        dominant_colors.append(hex_color)
                
                return dominant_colors
        except Exception as e:
            print(f"⚠️ Color extraction failed: {e}")
        
        return []
    
    def _classify_image_content(self, image: Image.Image, text: str, ui_elements: List[str]) -> str:
        """Classify the type of image content."""
        text_lower = text.lower()
        
        # Check for specific indicators
        if any(word in text_lower for word in ['wireframe', 'mockup', 'prototype']):
            return 'wireframe'
        elif any(word in text_lower for word in ['screenshot', 'screen', 'app']):
            return 'screenshot'
        elif len(ui_elements) > 3:
            return 'mockup'
        elif any(word in text_lower for word in ['flow', 'process', 'step']):
            return 'workflow'
        else:
            return 'other'
    
    def _classify_video_content(self, text: str, ui_elements: List[str]) -> str:
        """Classify the type of video content."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['demo', 'demonstration', 'tutorial']):
            return 'demo'
        elif any(word in text_lower for word in ['flow', 'process', 'workflow']):
            return 'workflow'
        elif len(ui_elements) > 5:
            return 'ui_walkthrough'
        else:
            return 'other'
    
    def _calculate_image_complexity(self, image: Image.Image, ui_elements: List[str], text: str) -> float:
        """Calculate complexity score for an image."""
        complexity = 0.0
        
        # Base complexity from image dimensions
        width, height = image.size
        pixel_complexity = (width * height) / (1920 * 1080)  # Normalize to 1080p
        complexity += min(pixel_complexity * 2, 2.0)
        
        # UI element complexity
        complexity += len(ui_elements) * 0.5
        
        # Text complexity
        word_count = len(text.split())
        complexity += min(word_count / 50, 2.0)
        
        return min(complexity, 10.0)
    
    def _calculate_video_complexity(self, frames: List, ui_elements: List[str], text: str) -> float:
        """Calculate complexity score for a video."""
        complexity = 0.0
        
        # Frame count complexity
        complexity += min(len(frames) / 10, 3.0)
        
        # UI element complexity
        complexity += len(ui_elements) * 0.3
        
        # Text complexity
        word_count = len(text.split())
        complexity += min(word_count / 100, 2.0)
        
        return min(complexity, 10.0)
    
    def _detect_design_elements(self, image: Image.Image, ui_elements: List[str], text: str) -> List[str]:
        """Detect design elements in the image."""
        elements = []
        text_lower = text.lower()
        
        # Text-based detection
        if any(word in text_lower for word in ['button', 'btn']):
            elements.append('buttons')
        if any(word in text_lower for word in ['input', 'field', 'form']):
            elements.append('input_fields')
        if any(word in text_lower for word in ['menu', 'navigation', 'nav']):
            elements.append('navigation')
        if any(word in text_lower for word in ['card', 'tile']):
            elements.append('cards')
        if any(word in text_lower for word in ['modal', 'popup', 'dialog']):
            elements.append('modals')
        
        # UI element based detection
        if 'buttons' in ui_elements:
            elements.append('interactive_elements')
        if 'form_fields' in ui_elements:
            elements.append('data_entry')
        
        return list(set(elements))
    
    def _identify_user_actions(self, text: str, ui_elements: List[str]) -> List[str]:
        """Identify possible user actions from the content."""
        actions = []
        text_lower = text.lower()
        
        # Text-based action detection
        action_words = {
            'click': ['click', 'tap', 'press', 'select'],
            'input': ['enter', 'type', 'input', 'fill'],
            'navigate': ['go to', 'navigate', 'open', 'view'],
            'submit': ['submit', 'send', 'save', 'confirm'],
            'search': ['search', 'find', 'filter', 'lookup']
        }
        
        for action_type, keywords in action_words.items():
            if any(keyword in text_lower for keyword in keywords):
                actions.append(action_type)
        
        # UI-based action detection
        if 'buttons' in ui_elements:
            actions.append('click')
        if 'form_fields' in ui_elements:
            actions.append('input')
        
        return list(set(actions))
    
    def _extract_key_frames(self, cap, frame_count: int, max_frames: int = 5) -> List:
        """Extract key frames from video for analysis."""
        key_frames = []
        
        if frame_count <= max_frames:
            # If video is short, take every frame
            frame_indices = range(frame_count)
        else:
            # Take evenly distributed frames
            frame_indices = [int(i * frame_count / max_frames) for i in range(max_frames)]
        
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                key_frames.append(frame)
        
        return key_frames
    
    def _generate_media_id(self, filename: str, content: str) -> str:
        """Generate unique ID for media analysis."""
        content_hash = hashlib.md5(f"{filename}{content}".encode()).hexdigest()
        return f"media_{content_hash[:12]}"
    
    def get_analysis_context(self, media_analysis: MediaAnalysis) -> Dict[str, Any]:
        """Get analysis context for integration with ticket analysis."""
        return {
            'media_type': media_analysis.media_type,
            'content_type': media_analysis.content_type,
            'extracted_text': media_analysis.extracted_text,
            'ui_elements': media_analysis.ui_elements,
            'design_elements': media_analysis.design_elements,
            'user_actions': media_analysis.user_actions,
            'complexity_score': media_analysis.complexity_score,
            'confidence_score': media_analysis.confidence_score,
            'dimensions': media_analysis.dimensions,
            'file_size': media_analysis.file_size
        } 