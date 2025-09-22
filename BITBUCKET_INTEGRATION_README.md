# 🔗 Bitbucket Integration for Jira-Figma Analyzer

## 🆕 New Features Added

### 1. **Bitbucket API Integration** (`bitbucket_integration.py`)
- ✅ Fetch repository information and metadata
- ✅ Retrieve recent commits and pull requests
- ✅ Analyze codebase structure and technology stack
- ✅ Generate repository context for enhanced question generation

### 2. **Webhook Server** (`webhook_server.py`)
- ✅ Automatic analysis triggered by Bitbucket events
- ✅ Support for pull request creation/updates
- ✅ Repository push event handling
- ✅ Background processing queue
- ✅ Health check and status endpoints

### 3. **Enhanced Analyzer** (`enhanced_jira_figma_analyzer.py`)
- ✅ Repository context-aware question generation
- ✅ React Native specific questions and considerations
- ✅ Technology stack-aware analysis
- ✅ Enhanced test case generation based on codebase

### 4. **Easy Setup** (`setup_integration.py`)
- ✅ Interactive configuration wizard
- ✅ Connection testing and validation
- ✅ Automatic environment setup

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Setup Wizard
```bash
python setup_integration.py
```

### 3. Start Webhook Server
```bash
./start_server.sh
# or manually:
python webhook_server.py --port 5000
```

### 4. Configure Bitbucket Webhook
- Go to your repository settings in Bitbucket
- Add webhook: `http://your-server:5000/webhook/bitbucket`
- Enable triggers: Pull request events, Repository push

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Bitbucket API (Required)
BITBUCKET_USERNAME=your_username
BITBUCKET_APP_PASSWORD=your_app_password

# Repository (Required)
BITBUCKET_WORKSPACE=sj-ml
BITBUCKET_REPOSITORY=habitto

# OpenAI (Optional - for enhanced questions)
OPENAI_API_KEY=your_openai_key

# Webhook Server
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
```

### Bitbucket App Password Setup
1. Go to: https://bitbucket.org/account/settings/app-passwords/
2. Create new app password with permissions:
   - **Repositories**: Read
   - **Pull requests**: Read
   - **Issues**: Read (optional)

## 🎯 How It Works

### Automatic Analysis Flow
```
Bitbucket Event → Webhook → Queue → Enhanced Analysis → Report
```

1. **Event Trigger**: Pull request created/updated in Bitbucket
2. **Webhook Reception**: Server receives webhook payload
3. **Background Processing**: Event queued for analysis
4. **Enhanced Analysis**: Repository context + ticket analysis
5. **Report Generation**: Comprehensive markdown report saved

### Repository Context Integration
- **Codebase Analysis**: File structure, technology stack, recent changes
- **Development Patterns**: Commit frequency, file types, feature areas
- **Smart Questions**: Context-aware questions based on actual codebase
- **React Native Focus**: Mobile-specific considerations and test cases

## 📊 Enhanced Analysis Features

### Context-Aware Questions
- Repository-specific integration questions
- Technology stack compatibility questions
- Recent development activity considerations
- Platform-specific (iOS/Android) questions

### Enhanced Test Cases
- React Native simulator testing
- Platform-specific test scenarios
- Performance testing on mobile devices
- Accessibility testing requirements

### Risk Assessment
- Platform compatibility risks
- Integration conflict assessment
- Performance impact evaluation
- Development activity-based risks

## 🌐 API Endpoints

### Webhook Endpoints
- `POST /webhook/bitbucket` - Bitbucket events
- `POST /webhook/jira` - Jira events (future)
- `POST /manual-analysis` - Manual trigger

### Status Endpoints
- `GET /` - Health check
- `GET /status` - Queue and connection status

## 📁 File Structure

```
jira-figma-analyzer/
├── bitbucket_integration.py      # Bitbucket API client
├── webhook_server.py             # Webhook server
├── enhanced_jira_figma_analyzer.py # Enhanced analyzer
├── setup_integration.py          # Setup wizard
├── start_server.sh              # Startup script
├── .env.example                 # Environment template
├── repository_context.json      # Cached repository data
└── analysis_outputs/            # Auto-generated reports
    ├── AUTO_PR_analysis_*.md
    ├── ENHANCED_analysis_*.md
    └── repository_context.json
```

## 🔍 Testing the Integration

### 1. Test Repository Connection
```bash
python bitbucket_integration.py
```

### 2. Test Enhanced Analysis
```bash
python enhanced_jira_figma_analyzer.py
```

### 3. Test Webhook Server
```bash
# Start server
python webhook_server.py

# Test endpoint
curl -X GET http://localhost:5000/
curl -X GET http://localhost:5000/status
```

### 4. Simulate Webhook
```bash
curl -X POST http://localhost:5000/manual-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "key": "TEST-123",
    "summary": "Test webhook integration",
    "description": "Testing the webhook integration functionality"
  }'
```

## 🛠️ Advanced Configuration

### Custom Repository Analysis
```python
from bitbucket_integration import BitbucketIntegration

# Custom workspace/repository
bitbucket = BitbucketIntegration("your-workspace", "your-repo")
context = bitbucket.analyze_repository_context()
```

### Enhanced Analyzer Usage
```python
from enhanced_jira_figma_analyzer import EnhancedJiraFigmaAnalyzer

analyzer = EnhancedJiraFigmaAnalyzer("workspace", "repo")
analyzer.refresh_repository_context()  # Force refresh

# Analyze with context
result = analyzer.analyze_ticket_content(ticket)
report = analyzer.generate_enhanced_report(result)
```

### Webhook Server Customization
```python
from webhook_server import WebhookServer

# Custom configuration
server = WebhookServer(port=8080, host='127.0.0.1')
server.run(debug=True)
```

## 🔒 Security Considerations

- **App Passwords**: Use Bitbucket app passwords, not account passwords
- **Environment Variables**: Keep credentials in .env file (not committed)
- **Webhook Security**: Consider adding webhook secrets for production
- **Network Access**: Restrict webhook server access as needed

## 🐛 Troubleshooting

### Common Issues

#### "Authentication failed"
- Check BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD
- Verify app password permissions
- Test with: `python bitbucket_integration.py`

#### "Repository not found"
- Verify BITBUCKET_WORKSPACE and BITBUCKET_REPOSITORY values
- Check repository access permissions
- Ensure repository is not private without access

#### "Webhook not receiving events"
- Check webhook URL configuration in Bitbucket
- Verify server is accessible from internet
- Check webhook event triggers are enabled

#### "Analysis not generating"
- Check analysis_outputs/ directory permissions
- Verify OpenAI API key (if using enhanced questions)
- Check server logs for error messages

### Debug Mode
```bash
# Run webhook server in debug mode
python webhook_server.py --debug

# Check repository context
cat repository_context.json

# View recent analysis
ls -la analysis_outputs/
```

## 🚀 Production Deployment

### Using Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "webhook_server.py", "--host", "0.0.0.0"]
```

### Using systemd (Linux)
```ini
[Unit]
Description=Jira-Figma Analyzer Webhook Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/jira-figma-analyzer
ExecStart=/path/to/python webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📈 Monitoring and Logging

### Server Logs
- Webhook events are logged to console
- Analysis results logged with timestamps
- Error handling with detailed error messages

### Metrics
- Queue size monitoring via `/status` endpoint
- Analysis completion tracking
- Repository context refresh frequency

---

## 🎉 Benefits of Bitbucket Integration

1. **🤖 Automated Analysis**: No manual ticket analysis needed
2. **🎯 Context-Aware**: Questions based on actual codebase
3. **⚡ Real-time**: Immediate analysis on pull request creation
4. **📊 Enhanced Insights**: Repository activity and patterns included
5. **🔄 Always Current**: Repository context stays up-to-date
6. **🚀 Scalable**: Background processing handles multiple events

The integration transforms the Jira-Figma Analyzer from a manual tool into an intelligent, automated system that provides context-aware analysis based on your actual React Native codebase! 🎯

