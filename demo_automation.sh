#!/bin/bash

echo "🎯 Habitto Jira Figma Analyzer - Automation Demo"
echo "================================================"
echo ""

echo "🚀 Step 1: Setting up automation..."
chmod +x setup_automation.sh
./setup_automation.sh
echo ""

echo "🔍 Step 2: Analyzing single ticket..."
python3 automate_analysis.py --mode single --input examples/mobile_number_update.json
echo ""

echo "📁 Step 3: Batch analysis of all tickets..."
python3 automate_analysis.py --mode batch
echo ""

echo "📊 Step 4: Showing generated reports..."
echo "Generated reports:"
ls -la analysis_outputs/
echo ""

echo "📋 Step 5: Sample report preview..."
echo "First 20 lines of mobile number update analysis:"
head -20 analysis_outputs/mobile_number_update_analysis.md
echo ""

echo "�� Demo completed! Automation is working perfectly!"
echo ""
echo "📁 Your reports are saved in: analysis_outputs/"
echo "📖 Complete instructions: COMPLETE_INSTRUCTIONS.md"
echo "🎯 Ready for contest submission!"
