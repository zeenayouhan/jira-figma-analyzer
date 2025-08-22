#!/bin/bash

# Habitto Jira Figma Analyzer - Automated Setup Script
# This script sets up the complete automation environment

echo "🚀 Setting up Habitto Jira Figma Analyzer - Automated Analysis Tool"
echo "=================================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x automate_analysis.py
chmod +x setup_automation.sh

# Create output directory
echo "📁 Creating output directories..."
mkdir -p analysis_outputs
mkdir -p examples

# Create a sample configuration file
echo "⚙️ Creating sample configuration..."
cat > config.json << 'CONFIG_EOF'
{
  "default_output_dir": "analysis_outputs",
  "default_input_dir": "examples",
  "report_template": "comprehensive",
  "include_figma_analysis": true,
  "include_test_cases": true,
  "include_questions": true,
  "max_questions_per_category": 15,
  "max_test_cases_per_category": 20
}
CONFIG_EOF

echo "✅ Setup completed successfully!"
echo ""
echo "🎯 USAGE INSTRUCTIONS:"
echo "======================"
echo ""
echo "1. 📋 SINGLE TICKET ANALYSIS:"
echo "   python3 automate_analysis.py --mode single --input examples/your_ticket.json"
echo ""
echo "2. 📁 BATCH ANALYSIS (all JSON files in examples folder):"
echo "   python3 automate_analysis.py --mode batch"
echo ""
echo "3. 🎯 INTERACTIVE MODE:"
echo "   python3 automate_analysis.py --mode interactive"
echo ""
echo "4. 🎯 QUICK ANALYSIS WITH TITLE/DESCRIPTION:"
echo "   python3 automate_analysis.py --mode interactive --title 'Your Ticket Title' --description 'Your ticket description'"
echo ""
echo "📊 OUTPUT:"
echo "   - Individual analysis reports saved to 'analysis_outputs/' folder"
echo "   - Batch summary reports for multiple tickets"
echo "   - Comprehensive markdown reports with all questions and test cases"
echo ""
echo "🔧 ADVANCED USAGE:"
echo "   python3 automate_analysis.py --help"
echo ""
echo "🎉 Ready to analyze Habitto tickets automatically!"
