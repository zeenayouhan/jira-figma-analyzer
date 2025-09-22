#!/usr/bin/env python3

# Create a bulletproof version of the Streamlit app
import re

# Read the current file
with open('enhanced_streamlit_app.py', 'r') as f:
    content = f.read()

# Add comprehensive error handling and data type checking
bulletproof_fixes = [
    # Fix all .get() calls to be bulletproof
    (r'(\w+)\.get\(', r'safe_get(\1, '),
    (r'analysis_ctx\.get\(', r'safe_get(analysis_ctx, '),
    (r'result\.get\(', r'safe_get(result, '),
    (r'ticket\.get\(', r'safe_get(ticket, '),
    (r'doc\.get\(', r'safe_get(doc, '),
    (r'screen\.get\(', r'safe_get(screen, '),
    (r'design\.get\(', r'safe_get(design, '),
    (r'stored_ticket\.get\(', r'safe_get(stored_ticket, '),
    (r'stored_ticket\[\'(\w+)\'\]', r'safe_get(stored_ticket, "\1")'),
    (r'result\[\'(\w+)\'\]', r'safe_get(result, "\1")'),
    (r'analysis_ctx\[\'(\w+)\'\]', r'safe_get(analysis_ctx, "\1")'),
]

# Apply fixes
for pattern, replacement in bulletproof_fixes:
    content = re.sub(pattern, replacement, content)

# Add the safe_get function at the top
safe_get_function = '''
def safe_get(obj, key, default=None):
    """Safely get a value from an object, handling all data types."""
    if obj is None:
        return default
    if isinstance(obj, str):
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    if hasattr(obj, 'get'):
        return obj.get(key, default)
    if hasattr(obj, key):
        return getattr(obj, key, default)
    return default

'''

# Insert the safe_get function after imports
import_end = content.find('import pandas as pd')
if import_end != -1:
    content = content[:import_end] + safe_get_function + content[import_end:]
else:
    content = safe_get_function + content

# Write the bulletproof version
with open('enhanced_streamlit_app.py', 'w') as f:
    f.write(content)

print("Created bulletproof version of enhanced_streamlit_app.py")
