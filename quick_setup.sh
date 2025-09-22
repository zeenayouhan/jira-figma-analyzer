#!/bin/bash
echo "🔧 Quick Webhook Configuration Setup"
echo "====================================="

# Generate webhook secret
WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "Generated webhook secret: $WEBHOOK_SECRET"

# Get local IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "Your local IP: $LOCAL_IP"

# Create .env file
cat > .env << EOL
# Bitbucket API Configuration
BITBUCKET_USERNAME=your_bitbucket_username
BITBUCKET_APP_PASSWORD=your_bitbucket_app_password

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key

# Webhook Server Configuration
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
WEBHOOK_SECRET=$WEBHOOK_SECRET

# Repository Configuration
BITBUCKET_WORKSPACE=sj-ml
BITBUCKET_REPOSITORY=habitto

# Analysis Configuration
AUTO_ANALYSIS_ENABLED=true
SAVE_REPOSITORY_CONTEXT=true
ANALYSIS_OUTPUT_DIR=analysis_outputs
EOL

echo ""
echo "✅ .env file created with generated secret"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your Bitbucket credentials"
echo "2. Start webhook server: python webhook_server.py"
echo "3. Configure Bitbucket webhook: http://$LOCAL_IP:5000/webhook/bitbucket"
echo ""
echo "🔐 Your webhook secret: $WEBHOOK_SECRET"
echo "🌐 Your webhook URL: http://$LOCAL_IP:5000/webhook/bitbucket"
