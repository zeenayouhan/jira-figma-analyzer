#!/usr/bin/env python3
"""
Webhook Server for Jira-Figma Analyzer

This server listens for webhooks from Bitbucket and automatically
triggers analysis for new pull requests, issues, and commits.
"""

import os
import json
import signal
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from bitbucket_integration import BitbucketIntegration
from jira_figma_analyzer import JiraFigmaAnalyzer
import threading
import queue

class WebhookServer:
    """Main webhook server class."""
    
    def __init__(self, port=5000, host='0.0.0.0'):
        self.app = Flask(__name__)
        self.port = port
        self.host = host
        self.analyzer = JiraFigmaAnalyzer()
        self.bitbucket = BitbucketIntegration()
        self.analysis_queue = queue.Queue()
        
        # Setup routes
        self.setup_routes()
        
        # Start background worker
        self.worker_thread = threading.Thread(target=self.background_worker, daemon=True)
        self.worker_thread.start()
        
        print(f"🚀 Webhook server initialized on {host}:{port}")
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "service": "Jira-Figma Analyzer Webhook Server",
                "timestamp": datetime.now().isoformat(),
                "bitbucket_authenticated": self.bitbucket.authenticated
            }), 200
        
        @self.app.route('/webhook/bitbucket', methods=['POST'])
        def bitbucket_webhook():
            """Handle Bitbucket webhooks."""
            try:
                payload = request.get_json()
                event_type = request.headers.get('X-Event-Key', '')
                
                print(f"📥 Received webhook: {event_type}")
                
                # Queue the analysis for background processing
                self.analysis_queue.put({
                    'event_type': event_type,
                    'payload': payload,
                    'timestamp': datetime.now().isoformat()
                })
                
                return jsonify({
                    "status": "received",
                    "event_type": event_type,
                    "queued_for_analysis": True
                }), 200
                
            except Exception as e:
                print(f"❌ Webhook error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/webhook/jira', methods=['POST'])
        def jira_webhook():
            """Handle Jira webhooks (future enhancement)."""
            try:
                payload = request.get_json()
                event_type = request.headers.get('X-Atlassian-Webhook-Identifier', '')
                
                print(f"📥 Received Jira webhook: {event_type}")
                
                # Queue for analysis
                self.analysis_queue.put({
                    'event_type': f'jira:{event_type}',
                    'payload': payload,
                    'timestamp': datetime.now().isoformat()
                })
                
                return jsonify({
                    "status": "received",
                    "event_type": event_type,
                    "queued_for_analysis": True
                }), 200
                
            except Exception as e:
                print(f"❌ Jira webhook error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/manual-analysis', methods=['POST'])
        def manual_analysis():
            """Manually trigger analysis."""
            try:
                data = request.get_json()
                
                # Queue manual analysis
                self.analysis_queue.put({
                    'event_type': 'manual',
                    'payload': data,
                    'timestamp': datetime.now().isoformat()
                })
                
                return jsonify({
                    "status": "queued",
                    "message": "Analysis queued for manual trigger"
                }), 200
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Get server status and queue information."""
            return jsonify({
                "server_status": "running",
                "queue_size": self.analysis_queue.qsize(),
                "bitbucket_connected": self.bitbucket.authenticated,
                "analyzer_ready": True,
                "timestamp": datetime.now().isoformat()
            }), 200
    
    def background_worker(self):
        """Background worker to process analysis queue."""
        print("🔄 Background worker started")
        
        while True:
            try:
                # Get item from queue (blocks until available)
                item = self.analysis_queue.get(timeout=10)
                
                print(f"🔍 Processing: {item['event_type']}")
                
                # Process based on event type
                if item['event_type'] == 'pullrequest:created':
                    self.handle_pr_created(item['payload'])
                elif item['event_type'] == 'pullrequest:updated':
                    self.handle_pr_updated(item['payload'])
                elif item['event_type'] == 'repo:push':
                    self.handle_push_event(item['payload'])
                elif item['event_type'].startswith('jira:'):
                    self.handle_jira_event(item['payload'])
                elif item['event_type'] == 'manual':
                    self.handle_manual_analysis(item['payload'])
                
                # Mark task as done
                self.analysis_queue.task_done()
                
            except queue.Empty:
                # No items in queue, continue
                continue
            except Exception as e:
                print(f"❌ Background worker error: {e}")
                continue
    
    def handle_pr_created(self, payload):
        """Handle pull request creation."""
        try:
            pr = payload.get('pullrequest', {})
            repository = payload.get('repository', {})
            
            print(f"📝 Analyzing PR #{pr.get('id')}: {pr.get('title')}")
            
            # Create synthetic ticket data from PR
            ticket_data = {
                'key': f"PR-{pr.get('id', 'UNKNOWN')}",
                'summary': pr.get('title', 'Pull Request'),
                'description': f"{pr.get('description', '')}\n\nRepository: {repository.get('full_name', '')}\nSource Branch: {pr.get('source', {}).get('branch', {}).get('name', '')}\nDestination Branch: {pr.get('destination', {}).get('branch', {}).get('name', '')}",
                'priority': {'name': 'Medium'},
                'assignee': {'displayName': pr.get('author', {}).get('display_name', 'Unknown')},
                'reporter': {'displayName': pr.get('author', {}).get('display_name', 'Unknown')},
                'labels': ['pull-request', 'code-review'],
                'components': [{'name': 'Development'}],
                'comments': []
            }
            
            # Add repository context
            repo_context = self.bitbucket.analyze_repository_context()
            if repo_context and 'error' not in repo_context:
                ticket_data['description'] += f"\n\nRepository Context:\n- Primary Language: {repo_context.get('repository', {}).get('primary_language', 'Unknown')}\n- Recent Activity: {repo_context.get('recent_activity', {}).get('commits_count', 0)} commits\n- Active Features: {', '.join(repo_context.get('recent_activity', {}).get('active_features', [])[:3])}"
            
            # Analyze the PR
            ticket = self.analyzer.parse_jira_ticket(ticket_data)
            result = self.analyzer.analyze_ticket_content(ticket)
            
            # Generate report
            report = self.analyzer.generate_report(result)
            
            # Save analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_outputs/AUTO_PR_analysis_{pr.get('id', 'unknown')}_{timestamp}.md"
            
            os.makedirs("analysis_outputs", exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✅ Generated analysis for PR #{pr.get('id')}: {filename}")
            
        except Exception as e:
            print(f"❌ Error analyzing PR: {e}")
    
    def handle_pr_updated(self, payload):
        """Handle pull request updates."""
        print(f"🔄 PR updated: {payload.get('pullrequest', {}).get('id', 'unknown')}")
        # For now, treat updates like creation
        self.handle_pr_created(payload)
    
    def handle_push_event(self, payload):
        """Handle push events."""
        try:
            repository = payload.get('repository', {})
            changes = payload.get('push', {}).get('changes', [])
            
            print(f"📤 Push to {repository.get('name', 'unknown')}")
            
            # Update repository context
            context = self.bitbucket.analyze_repository_context()
            
            if context and 'error' not in context:
                # Save updated context
                with open('repository_context.json', 'w') as f:
                    json.dump(context, f, indent=2)
                
                print("✅ Updated repository context from push event")
            
        except Exception as e:
            print(f"❌ Error handling push event: {e}")
    
    def handle_jira_event(self, payload):
        """Handle Jira webhook events."""
        try:
            issue = payload.get('issue', {})
            
            if issue:
                print(f"🎫 Jira issue event: {issue.get('key', 'unknown')}")
                
                # Convert Jira webhook payload to our format
                ticket_data = {
                    'key': issue.get('key', ''),
                    'summary': issue.get('fields', {}).get('summary', ''),
                    'description': issue.get('fields', {}).get('description', ''),
                    'priority': issue.get('fields', {}).get('priority', {}),
                    'assignee': issue.get('fields', {}).get('assignee', {}),
                    'reporter': issue.get('fields', {}).get('reporter', {}),
                    'labels': issue.get('fields', {}).get('labels', []),
                    'components': issue.get('fields', {}).get('components', []),
                    'comments': []
                }
                
                # Analyze the Jira issue
                ticket = self.analyzer.parse_jira_ticket(ticket_data)
                result = self.analyzer.analyze_ticket_content(ticket)
                
                # Generate report
                report = self.analyzer.generate_report(result)
                
                # Save analysis
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis_outputs/AUTO_JIRA_analysis_{issue.get('key', 'unknown')}_{timestamp}.md"
                
                os.makedirs("analysis_outputs", exist_ok=True)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                print(f"✅ Generated analysis for Jira issue {issue.get('key')}: {filename}")
            
        except Exception as e:
            print(f"❌ Error handling Jira event: {e}")
    
    def handle_manual_analysis(self, payload):
        """Handle manual analysis requests."""
        try:
            print("🔧 Processing manual analysis request")
            
            # Analyze based on provided data
            ticket = self.analyzer.parse_jira_ticket(payload)
            result = self.analyzer.analyze_ticket_content(ticket)
            
            # Generate report
            report = self.analyzer.generate_report(result)
            
            # Save analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_outputs/MANUAL_analysis_{timestamp}.md"
            
            os.makedirs("analysis_outputs", exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✅ Generated manual analysis: {filename}")
            
        except Exception as e:
            print(f"❌ Error in manual analysis: {e}")
    
    def run(self, debug=False):
        """Start the webhook server."""
        print(f"🌐 Starting webhook server on {self.host}:{self.port}")
        print(f"📡 Webhook URL: http://{self.host}:{self.port}/webhook/bitbucket")
        print(f"🏥 Health check: http://{self.host}:{self.port}/")
        print(f"📊 Status: http://{self.host}:{self.port}/status")
        
        self.app.run(host=self.host, port=self.port, debug=debug)

def setup_webhook_url():
    """Print instructions for setting up webhook in Bitbucket."""
    print("\n🔧 WEBHOOK SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to your Bitbucket repository settings")
    print("2. Navigate to 'Webhooks' section")
    print("3. Click 'Add webhook'")
    print("4. Configure:")
    print("   - Title: Jira-Figma Analyzer")
    print("   - URL: http://your-server:5000/webhook/bitbucket")
    print("   - Triggers: Pull request (created, updated), Repository (push)")
    print("5. Save the webhook")
    print("\n📝 For Jira integration:")
    print("   - URL: http://your-server:5000/webhook/jira")
    print("   - Triggers: Issue (created, updated)")
    print("=" * 50)

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print("\n🛑 Shutting down webhook server...")
    sys.exit(0)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Jira-Figma Analyzer Webhook Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to run on (default: 5000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--setup-info", action="store_true", help="Show webhook setup instructions")
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if args.setup_info:
        setup_webhook_url()
        sys.exit(0)
    
    # Create and run server
    server = WebhookServer(port=args.port, host=args.host)
    
    try:
        server.run(debug=args.debug)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
