#!/usr/bin/env python3
"""
Bitbucket API Integration for Jira-Figma Analyzer

This module provides integration with Bitbucket API to:
1. Fetch repository information and context
2. Retrieve commit history and pull requests
3. Analyze code structure for better question generation
4. Set up webhooks for automatic analysis
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import base64
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
import asyncio

# Load environment variables
load_dotenv()

@dataclass
class BitbucketRepository:
    """Represents a Bitbucket repository."""
    name: str
    full_name: str
    description: str
    language: str
    size: int
    default_branch: str
    created_on: str
    updated_on: str
    links: Dict[str, Any]
    
@dataclass
class CommitInfo:
    """Represents a commit in the repository."""
    hash: str
    message: str
    author: str
    date: str
    files_changed: List[str]

@dataclass
class PullRequestInfo:
    """Represents a pull request."""
    id: int
    title: str
    description: str
    state: str
    author: str
    created_on: str
    updated_on: str
    source_branch: str
    destination_branch: str

class BitbucketIntegration:
    """Main class for Bitbucket API integration."""
    
    def __init__(self, workspace: str = "sj-ml", repository: str = "habitto"):
        self.workspace = workspace
        self.repository = repository
        self.base_url = "https://api.bitbucket.org/2.0"
        self.username = os.getenv("BITBUCKET_USERNAME")
        self.app_password = os.getenv("BITBUCKET_APP_PASSWORD")
        
        if not self.username or not self.app_password:
            print("⚠️  Bitbucket credentials not found. Set BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables.")
            self.authenticated = False
        else:
            self.authenticated = True
            
        # Create session for requests
        self.session = requests.Session()
        if self.authenticated:
            self.session.auth = (self.username, self.app_password)
    
    def get_repository_info(self) -> Optional[BitbucketRepository]:
        """Fetch repository information."""
        if not self.authenticated:
            return None
            
        try:
            url = f"{self.base_url}/repositories/{self.workspace}/{self.repository}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return BitbucketRepository(
                name=data.get("name", ""),
                full_name=data.get("full_name", ""),
                description=data.get("description", ""),
                language=data.get("language", ""),
                size=data.get("size", 0),
                default_branch=data.get("mainbranch", {}).get("name", "main"),
                created_on=data.get("created_on", ""),
                updated_on=data.get("updated_on", ""),
                links=data.get("links", {})
            )
        except Exception as e:
            print(f"❌ Error fetching repository info: {e}")
            return None
    
    def get_recent_commits(self, limit: int = 10) -> List[CommitInfo]:
        """Fetch recent commits from the repository."""
        if not self.authenticated:
            return []
            
        try:
            url = f"{self.base_url}/repositories/{self.workspace}/{self.repository}/commits"
            params = {"pagelen": limit}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            commits = []
            data = response.json()
            
            for commit_data in data.get("values", []):
                # Get files changed in this commit
                files_changed = self._get_commit_files(commit_data.get("hash", ""))
                
                commit = CommitInfo(
                    hash=commit_data.get("hash", ""),
                    message=commit_data.get("message", ""),
                    author=commit_data.get("author", {}).get("raw", ""),
                    date=commit_data.get("date", ""),
                    files_changed=files_changed
                )
                commits.append(commit)
            
            return commits
        except Exception as e:
            print(f"❌ Error fetching commits: {e}")
            return []
    
    def _get_commit_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in a specific commit."""
        if not self.authenticated or not commit_hash:
            return []
            
        try:
            url = f"{self.base_url}/repositories/{self.workspace}/{self.repository}/diffstat/{commit_hash}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            files = []
            
            for file_data in data.get("values", []):
                files.append(file_data.get("new", {}).get("path", ""))
            
            return files
        except Exception:
            return []
    
    def get_pull_requests(self, state: str = "OPEN", limit: int = 10) -> List[PullRequestInfo]:
        """Fetch pull requests from the repository."""
        if not self.authenticated:
            return []
            
        try:
            url = f"{self.base_url}/repositories/{self.workspace}/{self.repository}/pullrequests"
            params = {"state": state, "pagelen": limit}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            pull_requests = []
            data = response.json()
            
            for pr_data in data.get("values", []):
                pr = PullRequestInfo(
                    id=pr_data.get("id", 0),
                    title=pr_data.get("title", ""),
                    description=pr_data.get("description", ""),
                    state=pr_data.get("state", ""),
                    author=pr_data.get("author", {}).get("display_name", ""),
                    created_on=pr_data.get("created_on", ""),
                    updated_on=pr_data.get("updated_on", ""),
                    source_branch=pr_data.get("source", {}).get("branch", {}).get("name", ""),
                    destination_branch=pr_data.get("destination", {}).get("branch", {}).get("name", "")
                )
                pull_requests.append(pr)
            
            return pull_requests
        except Exception as e:
            print(f"❌ Error fetching pull requests: {e}")
            return []
    
    def get_repository_structure(self, path: str = "", limit: int = 100) -> Dict[str, Any]:
        """Get repository file structure."""
        if not self.authenticated:
            return {}
            
        try:
            url = f"{self.base_url}/repositories/{self.workspace}/{self.repository}/src/HEAD/{path}"
            params = {"pagelen": limit}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            structure = {
                "directories": [],
                "files": [],
                "total_size": 0
            }
            
            for item in data.get("values", []):
                item_info = {
                    "name": item.get("path", ""),
                    "type": item.get("type", ""),
                    "size": item.get("size", 0)
                }
                
                if item.get("type") == "commit_directory":
                    structure["directories"].append(item_info)
                else:
                    structure["files"].append(item_info)
                    structure["total_size"] += item.get("size", 0)
            
            return structure
        except Exception as e:
            print(f"❌ Error fetching repository structure: {e}")
            return {}
    
    def analyze_repository_context(self) -> Dict[str, Any]:
        """Analyze repository to provide context for question generation."""
        if not self.authenticated:
            return {"error": "Not authenticated with Bitbucket"}
        
        print("🔍 Analyzing Habitto repository context...")
        
        # Get repository info
        repo_info = self.get_repository_info()
        
        # Get recent commits
        recent_commits = self.get_recent_commits(limit=20)
        
        # Get open pull requests
        open_prs = self.get_pull_requests("OPEN", limit=10)
        
        # Get repository structure
        repo_structure = self.get_repository_structure()
        
        # Analyze patterns
        analysis = {
            "repository": {
                "name": repo_info.name if repo_info else "habitto",
                "description": repo_info.description if repo_info else "",
                "primary_language": repo_info.language if repo_info else "JavaScript",
                "size": repo_info.size if repo_info else 0,
                "last_updated": repo_info.updated_on if repo_info else ""
            },
            "recent_activity": {
                "commits_count": len(recent_commits),
                "open_prs_count": len(open_prs),
                "recent_files_changed": self._analyze_recent_changes(recent_commits),
                "active_features": self._extract_active_features(recent_commits, open_prs)
            },
            "codebase_structure": {
                "directories": len(repo_structure.get("directories", [])),
                "files": len(repo_structure.get("files", [])),
                "estimated_components": self._estimate_components(repo_structure),
                "technology_stack": self._identify_tech_stack(repo_structure)
            },
            "development_patterns": {
                "commit_frequency": self._analyze_commit_frequency(recent_commits),
                "common_file_types": self._analyze_file_types(recent_commits),
                "feature_areas": self._identify_feature_areas(recent_commits)
            }
        }
        
        return analysis
    
    def _analyze_recent_changes(self, commits: List[CommitInfo]) -> List[str]:
        """Analyze recently changed files."""
        changed_files = set()
        for commit in commits:
            changed_files.update(commit.files_changed)
        return list(changed_files)[:20]  # Top 20 most recently changed files
    
    def _extract_active_features(self, commits: List[CommitInfo], prs: List[PullRequestInfo]) -> List[str]:
        """Extract active features from commits and PRs."""
        features = set()
        
        # Extract from commit messages
        for commit in commits:
            message = commit.message.lower()
            if "feat:" in message or "feature:" in message:
                features.add(commit.message.split(":")[1].strip()[:50])
        
        # Extract from PR titles
        for pr in prs:
            if any(keyword in pr.title.lower() for keyword in ["feat", "feature", "add", "implement"]):
                features.add(pr.title[:50])
        
        return list(features)[:10]
    
    def _estimate_components(self, structure: Dict[str, Any]) -> int:
        """Estimate number of React Native components."""
        files = structure.get("files", [])
        component_files = [f for f in files if f.get("name", "").endswith((".jsx", ".tsx", ".js", ".ts"))]
        return len(component_files)
    
    def _identify_tech_stack(self, structure: Dict[str, Any]) -> List[str]:
        """Identify technology stack from file structure."""
        files = structure.get("files", [])
        tech_indicators = {
            "package.json": "Node.js/npm",
            "yarn.lock": "Yarn",
            "Podfile": "iOS/CocoaPods",
            "android/": "Android",
            "ios/": "iOS",
            ".tsx": "TypeScript React",
            ".jsx": "React",
            "metro.config.js": "React Native Metro",
            "__tests__/": "Jest Testing"
        }
        
        identified_tech = []
        for file in files:
            file_name = file.get("name", "")
            for indicator, tech in tech_indicators.items():
                if indicator in file_name and tech not in identified_tech:
                    identified_tech.append(tech)
        
        return identified_tech
    
    def _analyze_commit_frequency(self, commits: List[CommitInfo]) -> str:
        """Analyze commit frequency pattern."""
        if len(commits) == 0:
            return "No recent activity"
        elif len(commits) >= 15:
            return "High activity"
        elif len(commits) >= 5:
            return "Moderate activity"
        else:
            return "Low activity"
    
    def _analyze_file_types(self, commits: List[CommitInfo]) -> Dict[str, int]:
        """Analyze common file types in recent changes."""
        file_types = {}
        for commit in commits:
            for file_path in commit.files_changed:
                if "." in file_path:
                    ext = file_path.split(".")[-1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
        
        return dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _identify_feature_areas(self, commits: List[CommitInfo]) -> List[str]:
        """Identify feature areas from commit file paths."""
        areas = set()
        for commit in commits:
            for file_path in commit.files_changed:
                # Extract feature area from path structure
                path_parts = file_path.split("/")
                if len(path_parts) > 2:
                    # Look for common React Native patterns
                    if "src" in path_parts:
                        src_index = path_parts.index("src")
                        if src_index + 1 < len(path_parts):
                            areas.add(path_parts[src_index + 1])
                    elif "components" in path_parts:
                        comp_index = path_parts.index("components")
                        if comp_index + 1 < len(path_parts):
                            areas.add(f"components/{path_parts[comp_index + 1]}")
                    elif "screens" in path_parts:
                        screen_index = path_parts.index("screens")
                        if screen_index + 1 < len(path_parts):
                            areas.add(f"screens/{path_parts[screen_index + 1]}")
        
        return list(areas)[:15]

def create_webhook_handler():
    """Create a Flask webhook handler for automatic analysis."""
    from flask import Flask, request, jsonify
    from jira_figma_analyzer import JiraFigmaAnalyzer
    
    app = Flask(__name__)
    analyzer = JiraFigmaAnalyzer()
    bitbucket = BitbucketIntegration()
    
    @app.route('/webhook/bitbucket', methods=['POST'])
    def handle_bitbucket_webhook():
        """Handle incoming Bitbucket webhooks."""
        try:
            payload = request.get_json()
            
            # Check if this is a relevant event
            event_type = request.headers.get('X-Event-Key', '')
            
            if event_type == 'pullrequest:created':
                return handle_pr_created(payload)
            elif event_type == 'issue:created':
                return handle_issue_created(payload)
            elif event_type == 'repo:push':
                return handle_push_event(payload)
            
            return jsonify({"status": "ignored", "event": event_type}), 200
            
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return jsonify({"error": str(e)}), 500
    
    def handle_pr_created(payload):
        """Handle pull request creation."""
        pr = payload.get('pullrequest', {})
        
        # Create synthetic ticket data from PR
        ticket_data = {
            'key': f"PR-{pr.get('id', 'UNKNOWN')}",
            'summary': pr.get('title', 'Pull Request'),
            'description': pr.get('description', ''),
            'priority': {'name': 'Medium'},
            'assignee': {'displayName': pr.get('author', {}).get('display_name', 'Unknown')},
            'reporter': {'displayName': pr.get('author', {}).get('display_name', 'Unknown')},
            'labels': ['pull-request', 'code-review'],
            'components': [],
            'comments': []
        }
        
        # Analyze the PR as if it were a ticket
        ticket = analyzer.parse_jira_ticket(ticket_data)
        result = analyzer.analyze_ticket_content(ticket)
        
        # Generate analysis report
        report = analyzer.generate_report(result)
        
        # Save to analysis outputs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_outputs/PR_analysis_{pr.get('id', 'unknown')}_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"✅ Generated analysis for PR #{pr.get('id')}: {filename}")
        
        return jsonify({"status": "analyzed", "report_file": filename}), 200
    
    def handle_issue_created(payload):
        """Handle issue creation (if using Bitbucket issues)."""
        # Similar to PR handling but for issues
        return jsonify({"status": "issue_handled"}), 200
    
    def handle_push_event(payload):
        """Handle push events to update repository context."""
        # Update repository analysis on push
        context = bitbucket.analyze_repository_context()
        
        # Save updated context
        with open('repository_context.json', 'w') as f:
            json.dump(context, f, indent=2)
        
        print("✅ Updated repository context from push event")
        
        return jsonify({"status": "context_updated"}), 200
    
    return app

if __name__ == "__main__":
    # Test the integration
    bitbucket = BitbucketIntegration()
    
    print("🚀 Testing Bitbucket Integration...")
    
    # Test repository info
    repo_info = bitbucket.get_repository_info()
    if repo_info:
        print(f"✅ Repository: {repo_info.name}")
        print(f"   Description: {repo_info.description}")
        print(f"   Language: {repo_info.language}")
        print(f"   Size: {repo_info.size} bytes")
    
    # Test repository analysis
    context = bitbucket.analyze_repository_context()
    print(f"📊 Repository Analysis:")
    print(f"   Recent commits: {context.get('recent_activity', {}).get('commits_count', 0)}")
    print(f"   Open PRs: {context.get('recent_activity', {}).get('open_prs_count', 0)}")
    print(f"   Tech stack: {context.get('codebase_structure', {}).get('technology_stack', [])}")
