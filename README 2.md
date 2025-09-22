# 🎯 Jira Figma Analyzer

A smart tool that analyzes Jira tickets containing Figma links and suggests questions and clarifications to ask from clients. This tool helps development teams gather better requirements and reduce back-and-forth communication.

## ✨ Features

- **Figma Link Detection**: Automatically extracts Figma links from Jira tickets
- **Smart Question Generation**: Suggests relevant questions based on ticket content
- **Multiple Input Methods**: Support for manual entry, JSON import, and interactive CLI
- **Comprehensive Analysis**: Covers design, technical, and business aspects
- **Risk Assessment**: Identifies potential issues and areas needing clarification
- **Multiple Output Formats**: Markdown, JSON, and plain text reports
- **Web Interface**: Beautiful Streamlit-based UI for easy interaction

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd jira-figma-analyzer
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### Web Interface (Recommended)

Launch the Streamlit web interface:

```bash
streamlit run streamlit_app.py
```

This will open a web browser with an intuitive interface where you can:
- Enter ticket data manually
- Import JSON data
- Use predefined templates
- View analysis results in organized tabs

#### Command Line Interface

##### Interactive Mode
```bash
python cli.py --interactive
```

##### Analyze from JSON File
```bash
python cli.py --file ticket.json
```

##### Analyze with Inline JSON
```bash
python cli.py --json '{"key": "PROJ-123", "summary": "Dashboard", "description": "..."}'
```

##### Save Report to File
```bash
python cli.py --file ticket.json --output report.md
```

#### Python Library

```python
from jira_figma_analyzer import JiraFigmaAnalyzer

analyzer = JiraFigmaAnalyzer()

# Your ticket data
ticket_data = {
    'key': 'PROJ-123',
    'summary': 'Implement new dashboard',
    'description': 'Create dashboard with charts. Figma: https://figma.com/file/abc123',
    'priority': {'name': 'High'},
    # ... other fields
}

# Analyze
ticket = analyzer.parse_jira_ticket(ticket_data)
result = analyzer.analyze_ticket_content(ticket)

# Generate report
report = analyzer.generate_report(result)
print(report)
```

## 📋 Input Format

The tool accepts Jira ticket data in JSON format with the following structure:

```json
{
  "key": "PROJ-123",
  "summary": "Ticket title",
  "description": "Detailed description with Figma links",
  "priority": {"name": "High"},
  "assignee": {"displayName": "John Doe"},
  "reporter": {"displayName": "Jane Smith"},
  "labels": ["frontend", "dashboard"],
  "components": [{"name": "User Interface"}],
  "comments": []
}
```

## 🎨 Supported Figma Link Formats

The tool automatically detects Figma links in these formats:
- `https://www.figma.com/file/[ID]`
- `https://figma.com/file/[ID]`
- `https://www.figma.com/proto/[ID]`
- `https://figma.com/proto/[ID]`

## 📊 Analysis Output

The tool provides comprehensive analysis including:

### Questions Generated
- **Design Questions**: UI/UX related questions
- **Business Questions**: Stakeholder and value-related questions
- **General Questions**: Overall project questions

### Areas Needing Clarification
- Missing technical requirements
- Vague descriptions
- Unclear business context

### Technical Considerations
- Mobile responsiveness
- API integrations
- Security requirements
- Performance considerations

### Risk Areas
- Missing design references
- Scope creep indicators
- High-priority items without requirements

## 🔧 Configuration

### Environment Variables

Create a `.env` file for any API keys or configuration:

```env
# Optional: OpenAI API key for enhanced analysis
OPENAI_API_KEY=your_openai_api_key_here
```

### Customizing Question Templates

You can modify the question templates in `jira_figma_analyzer.py`:

```python
self.question_templates = {
    'design': [
        "Your custom design question here",
        # ... more questions
    ],
    'technical': [
        "Your custom technical question here",
        # ... more questions
    ],
    'business': [
        "Your custom business question here",
        # ... more questions
    ]
}
```

## 📁 Project Structure

```
jira-figma-analyzer/
├── jira_figma_analyzer.py    # Main analyzer library
├── streamlit_app.py          # Web interface
├── cli.py                    # Command line interface
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── examples/                 # Example files
    ├── sample_ticket.json    # Sample ticket data
    └── sample_report.md      # Sample analysis report
```

## 🧪 Examples

### Example 1: Dashboard Implementation

**Input:**
```json
{
  "key": "DASH-001",
  "summary": "Implement new user dashboard with responsive design",
  "description": "Create a new dashboard for users to view their data, charts, and analytics. Should be mobile-friendly and include real-time updates. Figma link: https://www.figma.com/file/abc123/dashboard-design",
  "priority": {"name": "High"},
  "labels": ["frontend", "dashboard", "responsive"]
}
```

**Output Questions:**
- Are all the Figma designs final and approved?
- What is the target screen size/resolution for this design?
- What is the expected user flow for this feature?
- What should happen in error states or edge cases?
- What is the business value/ROI expected from this feature?

### Example 2: Mobile App Feature

**Input:**
```json
{
  "key": "MOBILE-001",
  "summary": "Add push notification feature to mobile app",
  "description": "Implement push notifications for user engagement. Should work on both iOS and Android. Include settings for users to manage notification preferences. Figma link: https://www.figma.com/file/def456/notification-ui",
  "priority": {"name": "Medium"},
  "labels": ["mobile", "notifications", "ios", "android"]
}
```

**Output Questions:**
- Are there any specific animations or transitions required?
- What is the mobile/tablet experience requirements?
- Are there any third-party integrations required?
- What is the expected user load/scale requirements?
- Who are the primary users of this feature?

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page for existing problems
2. Create a new issue with detailed information
3. Include sample data and error messages when possible

## 🔮 Future Enhancements

- [ ] Integration with Jira API for direct ticket fetching
- [ ] Figma API integration for design analysis
- [ ] Machine learning for better question suggestions
- [ ] Team collaboration features
- [ ] Export to various project management tools
- [ ] Custom question templates per organization
- [ ] Analytics dashboard for question effectiveness

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Inspired by the need for better client communication in software development
- Thanks to all contributors and users who provide feedback
