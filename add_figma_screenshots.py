#!/usr/bin/env python3
"""
Add screenshot capture functionality to Figma integration for GPT-4 Vision analysis
"""

def add_figma_screenshots():
    # Read the current file
    with open('figma_integration.py', 'r') as f:
        content = f.read()
    
    # Add screenshot functionality to the FigmaDesign dataclass
    old_design_class = '''@dataclass
class FigmaDesign:
    """Represents a Figma design with all its components and analysis."""
    file_id: str
    name: str
    pages: List[Dict[str, Any]]
    screens: List[Dict[str, Any]]
    ui_components: List[Dict[str, Any]]
    design_tokens: Dict[str, Any]
    complexity_score: float
    implementation_notes: List[str]
    accessibility_notes: List[str]
    screen_details: List[Dict[str, Any]]
    japanese_text_analysis: Optional[Dict[str, Any]] = None
    japanese_screens: Optional[List[str]] = None
    total_japanese_text_nodes: int = 0'''
    
    new_design_class = '''@dataclass
class FigmaDesign:
    """Represents a Figma design with all its components and analysis."""
    file_id: str
    name: str
    pages: List[Dict[str, Any]]
    screens: List[Dict[str, Any]]
    ui_components: List[Dict[str, Any]]
    design_tokens: Dict[str, Any]
    complexity_score: float
    implementation_notes: List[str]
    accessibility_notes: List[str]
    screen_details: List[Dict[str, Any]]
    japanese_text_analysis: Optional[Dict[str, Any]] = None
    japanese_screens: Optional[List[str]] = None
    total_japanese_text_nodes: int = 0
    screenshots: Optional[Dict[str, str]] = None  # screen_name -> screenshot_path'''
    
    content = content.replace(old_design_class, new_design_class)
    
    # Add screenshot capture method
    screenshot_method = '''
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
        
        return screenshots'''
    
    # Find the analyze_figma_design method and add screenshot capture
    old_analyze_method = '''        # Store Japanese analysis results
        design.japanese_text_analysis = japanese_analysis
        design.japanese_screens = japanese_screens
        design.total_japanese_text_nodes = total_japanese_text_nodes
        
        print(f"✅ Japanese text analysis completed: {total_japanese_text_nodes} Japanese text nodes found")
        
        return design'''
    
    new_analyze_method = '''        # Store Japanese analysis results
        design.japanese_text_analysis = japanese_analysis
        design.japanese_screens = japanese_screens
        design.total_japanese_text_nodes = total_japanese_text_nodes
        
        print(f"✅ Japanese text analysis completed: {total_japanese_text_nodes} Japanese text nodes found")
        
        # Capture screenshots for GPT-4 Vision analysis
        print("📸 Capturing screenshots for GPT-4 Vision analysis...")
        screenshots = self._capture_screen_screenshots(file_id, design.screens)
        design.screenshots = screenshots
        
        return design'''
    
    content = content.replace(old_analyze_method, new_analyze_method)
    
    # Add the screenshot method to the class
    # Find the end of the class and add the method
    class_end_pattern = '    def get_design_context_for_analysis(self, design: FigmaDesign) -> str:'
    if class_end_pattern in content:
        content = content.replace(class_end_pattern, screenshot_method + '\n    def get_design_context_for_analysis(self, design: FigmaDesign) -> str:')
    else:
        # Add at the end of the class
        content = content.rstrip() + screenshot_method + '\n'
    
    # Write the updated content
    with open('figma_integration.py', 'w') as f:
        f.write(content)
    
    print("✅ Added screenshot capture functionality to Figma integration")

if __name__ == "__main__":
    add_figma_screenshots()
