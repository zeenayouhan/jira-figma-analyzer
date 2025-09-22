#!/bin/bash

# Simple deployment script for Jira-Figma Analyzer
# Works without Docker - for direct server deployment

echo "🚀 Jira-Figma Analyzer - Simple Deployment"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "🐍 Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p analysis_outputs logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x *.py
chmod 644 *.json *.md

# Check environment file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your actual API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - FIGMA_ACCESS_TOKEN"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Load environment variables
echo "🔧 Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Test the application
echo "�� Testing application..."
python3 -c "
import sys
sys.path.append('.')
try:
    from jira_figma_analyzer import JiraFigmaAnalyzer
    analyzer = JiraFigmaAnalyzer()
    print('✅ Application test passed!')
except Exception as e:
    print(f'❌ Application test failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "🚀 To start the application:"
    echo "   source venv/bin/activate"
    echo "   streamlit run complete_streamlit_app.py --server.port 8501 --server.address 0.0.0.0"
    echo ""
    echo "🌐 Access at: http://localhost:8501"
    echo ""
    echo "📊 For production with nginx:"
    echo "   1. Install nginx"
    echo "   2. Copy nginx.conf to /etc/nginx/sites-available/"
    echo "   3. Enable site: sudo ln -s /etc/nginx/sites-available/jira-analyzer /etc/nginx/sites-enabled/"
    echo "   4. Restart nginx: sudo systemctl restart nginx"
    echo ""
    echo "🔧 For systemd service:"
    echo "   sudo cp jira-analyzer.service /etc/systemd/system/"
    echo "   sudo systemctl enable jira-analyzer"
    echo "   sudo systemctl start jira-analyzer"
else
    echo "❌ Deployment failed. Please check the errors above."
    exit 1
fi
