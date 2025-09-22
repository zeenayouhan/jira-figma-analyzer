#!/usr/bin/env python3
"""
Setup script for Bitbucket integration

This script helps set up the Bitbucket integration by:
1. Creating necessary configuration files
2. Testing API connections
3. Setting up webhook endpoints
4. Validating the integration
"""

import os
import getpass
import json
from bitbucket_integration import BitbucketIntegration
from enhanced_jira_figma_analyzer import EnhancedJiraFigmaAnalyzer

def setup_environment():
    """Set up environment variables and configuration."""
    print("🔧 Setting up Bitbucket Integration...")
    print("=" * 50)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        overwrite = input("Do you want to update the configuration? (y/N): ").lower()
        if overwrite != 'y':
            return
    
    print("\n📝 Please provide Bitbucket credentials:")
    print("   (You can create app passwords at: https://bitbucket.org/account/settings/app-passwords/)")
    
    username = input("Bitbucket username: ").strip()
    app_password = getpass.getpass("Bitbucket app password: ").strip()
    
    print("\n🤖 OpenAI configuration (optional for enhanced question generation):")
    openai_key = getpass.getpass("OpenAI API key (press Enter to skip): ").strip()
    
    print("\n🏗️ Repository configuration:")
    workspace = input("Bitbucket workspace (default: sj-ml): ").strip() or "sj-ml"
    repository = input("Repository name (default: habitto): ").strip() or "habitto"
    
    print("\n🌐 Webhook configuration:")
    webhook_host = input("Webhook host (default: 0.0.0.0): ").strip() or "0.0.0.0"
    webhook_port = input("Webhook port (default: 5000): ").strip() or "5000"
    
    # Create .env file
    env_content = f"""# Bitbucket API Configuration
BITBUCKET_USERNAME={username}
BITBUCKET_APP_PASSWORD={app_password}

# OpenAI Configuration (optional)
OPENAI_API_KEY={openai_key}

# Webhook Server Configuration
WEBHOOK_HOST={webhook_host}
WEBHOOK_PORT={webhook_port}

# Repository Configuration
BITBUCKET_WORKSPACE={workspace}
BITBUCKET_REPOSITORY={repository}

# Analysis Configuration
AUTO_ANALYSIS_ENABLED=true
SAVE_REPOSITORY_CONTEXT=true
ANALYSIS_OUTPUT_DIR=analysis_outputs
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Configuration saved to .env file")

def test_bitbucket_connection():
    """Test Bitbucket API connection."""
    print("\n🔍 Testing Bitbucket connection...")
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        bitbucket = BitbucketIntegration()
        
        if not bitbucket.authenticated:
            print("❌ Bitbucket authentication failed")
            print("   Please check your credentials in the .env file")
            return False
        
        # Test repository access
        repo_info = bitbucket.get_repository_info()
        
        if repo_info:
            print(f"✅ Successfully connected to repository: {repo_info.name}")
            print(f"   Description: {repo_info.description}")
            print(f"   Language: {repo_info.language}")
            print(f"   Size: {repo_info.size:,} bytes")
            return True
        else:
            print("❌ Could not access repository")
            print("   Please check repository name and permissions")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_enhanced_analyzer():
    """Test the enhanced analyzer."""
    print("\n🧪 Testing enhanced analyzer...")
    
    try:
        analyzer = EnhancedJiraFigmaAnalyzer()
        
        # Test sample ticket
        sample_ticket = {
            'key': 'TEST-001',
            'summary': 'Test integration functionality',
            'description': 'Testing the enhanced analyzer with repository context integration.',
            'priority': {'name': 'Medium'},
            'assignee': {'displayName': 'Test User'},
            'reporter': {'displayName': 'Setup Script'},
            'labels': ['test', 'integration'],
            'components': [{'name': 'Testing'}],
            'comments': []
        }
        
        ticket = analyzer.parse_jira_ticket(sample_ticket)
        result = analyzer.analyze_ticket_content(ticket)
        
        print(f"✅ Enhanced analyzer working:")
        print(f"   Generated {len(result.suggested_questions)} questions")
        print(f"   Generated {len(result.test_cases)} test cases")
        print(f"   Identified {len(result.risk_areas)} risk areas")
        
        if analyzer.repository_context:
            print("✅ Repository context loaded successfully")
        else:
            print("⚠️  Repository context not available (check credentials)")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced analyzer test failed: {e}")
        return False

def setup_webhook_instructions():
    """Provide webhook setup instructions."""
    print("\n🔗 Webhook Setup Instructions:")
    print("=" * 40)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    host = os.getenv('WEBHOOK_HOST', 'localhost')
    port = os.getenv('WEBHOOK_PORT', '5000')
    
    if host == '0.0.0.0':
        host = 'your-server-ip'
    
    print(f"""
1. Start the webhook server:
   python webhook_server.py --port {port}

2. Configure Bitbucket webhook:
   - Go to your repository settings
   - Navigate to 'Webhooks'
   - Add new webhook with:
     * Title: Jira-Figma Analyzer
     * URL: http://{host}:{port}/webhook/bitbucket
     * Triggers: Pull request (created, updated), Repository (push)

3. Test the webhook:
   - Create a test pull request
   - Check analysis_outputs/ for auto-generated reports

4. For Jira integration (optional):
   - URL: http://{host}:{port}/webhook/jira
   - Triggers: Issue (created, updated)
""")

def create_startup_script():
    """Create a startup script for easy server launch."""
    script_content = '''#!/bin/bash
# Startup script for Jira-Figma Analyzer with Bitbucket integration

echo "🚀 Starting Jira-Figma Analyzer with Bitbucket Integration..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check configuration
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Running setup..."
    python setup_integration.py
fi

# Start webhook server
echo "🌐 Starting webhook server..."
python webhook_server.py --port ${WEBHOOK_PORT:-5000}
'''
    
    with open('start_server.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('start_server.sh', 0o755)
    print("✅ Created start_server.sh script")

def main():
    """Main setup function."""
    print("🎯 Jira-Figma Analyzer - Bitbucket Integration Setup")
    print("=" * 60)
    
    # Step 1: Environment setup
    setup_environment()
    
    # Step 2: Test connections
    bitbucket_ok = test_bitbucket_connection()
    analyzer_ok = test_enhanced_analyzer()
    
    # Step 3: Create startup script
    create_startup_script()
    
    # Step 4: Provide instructions
    setup_webhook_instructions()
    
    # Summary
    print("\n📊 Setup Summary:")
    print("=" * 20)
    print(f"✅ Environment configured: True")
    print(f"✅ Bitbucket connection: {bitbucket_ok}")
    print(f"✅ Enhanced analyzer: {analyzer_ok}")
    print(f"✅ Startup script created: True")
    
    if bitbucket_ok and analyzer_ok:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: ./start_server.sh")
        print("2. Configure webhooks in Bitbucket")
        print("3. Test with a sample pull request")
    else:
        print("\n⚠️  Setup completed with issues. Please check the error messages above.")

if __name__ == "__main__":
    main()
