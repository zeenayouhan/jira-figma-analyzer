#!/usr/bin/env python3
"""
Force Railway redeploy by updating configuration
"""

import json
import os
from datetime import datetime

# Update railway.json with timestamp to force new deployment
railway_config = {
    "build": {
        "buildCommand": "pip install -r requirements.txt"
    },
    "deploy": {
        "startCommand": "python start.py",
        "restartPolicyType": "ON_FAILURE",
        "restartPolicyMaxRetries": 3
    },
    "environment": {
        "PYTHONPATH": "/app",
        "STREAMLIT_SERVER_HEADLESS": "true",
        "STREAMLIT_SERVER_ENABLE_CORS": "true"
    },
    "_lastUpdated": datetime.now().isoformat()
}

with open('railway.json', 'w') as f:
    json.dump(railway_config, f, indent=2)

print("✅ Updated railway.json to force redeploy")

# Also update start.py with a comment to ensure it's rebuilt
with open('start.py', 'r') as f:
    content = f.read()

# Add a comment with timestamp
timestamp_comment = f"# Force rebuild: {datetime.now().isoformat()}\n"

if "# Force rebuild:" not in content:
    content = timestamp_comment + content
else:
    # Replace existing timestamp
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("# Force rebuild:"):
            lines[i] = timestamp_comment.strip()
            break
    content = '\n'.join(lines)

with open('start.py', 'w') as f:
    f.write(content)

print("✅ Updated start.py to force rebuild")
