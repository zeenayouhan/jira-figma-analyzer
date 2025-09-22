#!/bin/bash

# Jira Figma Analyzer Setup Script

echo "🎯 Setting up Jira Figma Analyzer..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make scripts executable
chmod +x jira_figma_analyzer.py
chmod +x cli.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Usage options:"
echo "1. Web Interface (Recommended):"
echo "   streamlit run streamlit_app.py"
echo ""
echo "2. Command Line Interface:"
echo "   python3 cli.py --interactive"
echo "   python3 cli.py --file examples/sample_ticket.json"
echo ""
echo "3. Direct Python usage:"
echo "   python3 jira_figma_analyzer.py"
echo ""
echo "For more information, see README.md"
