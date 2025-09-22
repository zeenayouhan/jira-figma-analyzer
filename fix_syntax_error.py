#!/usr/bin/env python3
"""
Fix the syntax error in jira_figma_analyzer.py around line 170
"""

import re

def fix_syntax_error():
    file_path = 'jira_figma_analyzer.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the malformed try-except blocks around feedback system initialization
    # The current code has nested try blocks and missing except blocks
    
    # Find the problematic section and replace it
    pattern = r'''        # Initialize feedback system
        try:
            from feedback_system import FeedbackSystem
            self\.feedback_system = FeedbackSystem\(\)\n            print\("📝 Feedback system initialized"\)\n            FEEDBACK_AVAILABLE = True\n            \n            # Initialize feedback learning system\n            if FEEDBACK_LEARNING_AVAILABLE:\n                try:\n                    self\.feedback_learning = FeedbackLearningSystem\(self\.feedback_system\)\n                    print\("🧠 Feedback Learning System initialized"\)\n        except Exception as e:\n                    print\(f"⚠️ Feedback learning system initialization failed: \{e\}"\)\n                    self\.feedback_learning = None\n            else:\n                self\.feedback_learning = None\n                \n        except ImportError as e:\n            print\(f"⚠️ Feedback system not available: \{e\}"\)\n            self\.feedback_system = None\n            self\.feedback_learning = None\n            FEEDBACK_AVAILABLE = False'''
    
    replacement = '''        # Initialize feedback system
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
            FEEDBACK_AVAILABLE = False'''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed syntax error in jira_figma_analyzer.py")

if __name__ == "__main__":
    fix_syntax_error()
