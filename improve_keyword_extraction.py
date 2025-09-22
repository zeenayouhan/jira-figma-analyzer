#!/usr/bin/env python3

# Read the current file
with open('jira_figma_analyzer.py', 'r') as f:
    content = f.read()

# Find and replace the _extract_relevant_keywords method
old_extract_method = '''    def _extract_relevant_keywords(self, ticket: JiraTicket) -> List[str]:
        """Extract relevant keywords from ticket to filter Figma content."""
        content = f"{ticket.title} {ticket.description}".lower()
        
        # Common UI/UX keywords
        keywords = []
        
        # Extract specific feature keywords
        feature_keywords = [
            'login', 'signup', 'register', 'auth', 'profile', 'settings', 'dashboard',
            'payment', 'checkout', 'cart', 'search', 'filter', 'form', 'input',
            'button', 'modal', 'popup', 'navigation', 'menu', 'tab', 'card',
            'list', 'grid', 'table', 'chart', 'graph'
        ]
        
        for keyword in feature_keywords:
            if keyword in content:
                keywords.append(keyword)
        
        # Extract words that might be screen or component names
        words = content.split()
        for word in words:
            if len(word) > 3 and word.isalpha():
                keywords.append(word)
        
        return list(set(keywords))[:10]'''

new_extract_method = '''    def _extract_relevant_keywords(self, ticket: JiraTicket) -> List[str]:
        """Extract relevant keywords from ticket to filter Figma content."""
        content = f"{ticket.title} {ticket.description}".lower()
        
        keywords = []
        
        # Extract specific feature keywords with priority
        high_priority_keywords = [
            'profile', 'user', 'account', 'personal', 'settings', 'edit', 'update',
            'occupation', 'country', 'residence', 'dropdown', 'select', 'picker',
            'form', 'field', 'input', 'save', 'submit'
        ]
        
        medium_priority_keywords = [
            'login', 'signup', 'register', 'auth', 'dashboard', 'payment', 'checkout',
            'search', 'filter', 'button', 'modal', 'navigation', 'menu', 'tab'
        ]
        
        # High priority keywords get added multiple times for emphasis
        for keyword in high_priority_keywords:
            if keyword in content:
                keywords.extend([keyword, keyword])  # Add twice for importance
        
        for keyword in medium_priority_keywords:
            if keyword in content:
                keywords.append(keyword)
        
        # Extract specific nouns from title and description
        import re
        # Look for capitalized words (likely to be feature names)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', f"{ticket.title} {ticket.description}")
        keywords.extend([word.lower() for word in capitalized_words])
        
        # Extract quoted words (often specific feature names)
        quoted_words = re.findall(r'"([^"]*)"', f"{ticket.title} {ticket.description}")
        keywords.extend([word.lower() for word in quoted_words])
        
        return list(set(keywords))[:15]'''

# Replace the method
content = content.replace(old_extract_method, new_extract_method)

# Write back to file
with open('jira_figma_analyzer.py', 'w') as f:
    f.write(content)

print("✅ Improved keyword extraction for better relevance!")
