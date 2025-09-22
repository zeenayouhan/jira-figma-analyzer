# 🎨 Figma Integration Setup Guide

## 🎯 **Overview**

Your Jira-Figma Analyzer now includes **full Figma design reading capabilities**! When you add Figma links to tickets, the tool will:

- 📥 **Fetch actual design files** from Figma API
- 🧩 **Extract UI components** and screen names
- 📱 **Analyze screen flows** and user journeys
- ⚡ **Calculate design complexity** scores
- 🎯 **Generate design-specific questions** based on actual content
- ♿ **Identify accessibility considerations** from the design

## 🔑 **Setup Instructions**

### **1. Get a Figma Access Token**

1. **Go to Figma Account Settings**: https://www.figma.com/settings
2. **Scroll to "Personal access tokens"**
3. **Click "Create new token"**
4. **Name it**: "Jira Figma Analyzer"
5. **Copy the token** (starts with `figd_...`)

### **2. Add Token to Environment**

Add your Figma token to the `.env` file:

```bash
# Add this line to your .env file
FIGMA_ACCESS_TOKEN=figd_your_token_here

# Your existing OpenAI key
OPENAI_API_KEY=sk-proj-your_openai_key_here
```

### **3. Restart the Application**

```bash
# Kill the current app
pkill -f streamlit

# Restart with Figma integration
source venv/bin/activate && streamlit run enhanced_streamlit_app.py --server.port 8502
```

## 🎨 **How It Works**

### **Before (Link Detection Only)**

```
Ticket: "Create login screen - see Figma: https://figma.com/file/abc123"
↓
Analysis: "This ticket has 1 Figma link"
↓
Questions: Generic UI/design questions
```

### **After (Full Design Analysis)**

```
Ticket: "Create login screen - see Figma: https://figma.com/file/abc123"
↓
Figma API: Fetches actual design file
↓
Analysis:
  - Design Name: "Mobile Login Flow"
  - Screens: ["Login", "Forgot Password", "2FA"]
  - Components: ["LoginButton", "EmailInput", "PasswordField"]
  - Complexity: 7.2/10
  - Accessibility: ["Form labels needed", "Touch targets 44px"]
↓
Questions: Specific design implementation questions
```

## 📊 **What Gets Analyzed**

### **Design Structure**

- **Pages**: All design pages and artboards
- **Components**: UI elements like buttons, forms, cards
- **Screens**: Login, dashboard, profile pages, etc.
- **User Flows**: Sequential screens and navigation

### **Implementation Insights**

- **Complexity Score**: 0-10 based on design complexity
- **Component Count**: Number of unique UI elements
- **Screen Count**: Total screens to implement
- **Nesting Depth**: How complex the component hierarchy is

### **Accessibility Analysis**

- **Form Requirements**: Label and validation needs
- **Button Guidelines**: Accessibility labels and keyboard navigation
- **Image Requirements**: Alt text and screen reader support
- **Touch Targets**: Mobile-friendly sizing requirements

### **Implementation Notes**

- **Navigation Architecture**: For multi-screen apps
- **Form Handling**: Validation and error management
- **Performance Considerations**: For lists and complex UIs
- **Focus Management**: For modals and dialogs

## 🎯 **Enhanced Question Examples**

### **Without Figma Reading**

```
- What are the UI requirements for this feature?
- How should the user interface look?
- What design considerations are important?
```

### **With Figma Reading**

```
- How should the "LoginButton" component integrate with our existing React Native button library?
- The design shows 3 screens (Login → 2FA → Dashboard) - what's the navigation flow between them?
- The Figma design has a complexity score of 7.2/10 - do we need additional development time for the nested components?
- The accessibility analysis indicates form labels are needed - how should we implement WCAG-compliant labels for the "EmailInput" and "PasswordField" components?
- The design includes modal dialogs - how should we handle focus management and keyboard navigation?
```

## ✅ **Testing the Integration**

### **1. Verify Setup**

```bash
# Test Figma token
cd /your/project/directory
python3 -c "
from figma_integration import FigmaIntegration
figma = FigmaIntegration()
test_url = 'https://www.figma.com/file/abc123/test'
print('File key extracted:', figma.extract_figma_file_key(test_url))
print('Token available:', bool(figma.figma_token))
"
```

### **2. Test with Real Figma URL**

1. **Go to** `http://localhost:8502`
2. **Navigate to** "🎯 Analyze Tickets"
3. **Create a ticket** with a real Figma URL
4. **Check the logs** for Figma analysis output
5. **Review questions** for design-specific content

### **3. Expected Console Output**

```
🎨 Figma Integration initialized
📥 Fetching Figma design: abc123def456
✅ Figma design analyzed: Mobile Login Flow
   📄 Pages: 3
   🧩 UI Components: 12
   📱 Screens: 3
   🔄 User Flows: 2
   ⚡ Complexity Score: 7.2/10
```

## 🔒 **Security & Permissions**

### **Token Permissions**

- **Read-only access** to your Figma files
- **No editing capabilities** - analysis only
- **Team files**: Requires team access to read shared designs

### **Privacy**

- **No data storage**: Designs analyzed in real-time
- **API calls only**: No Figma content cached locally
- **Secure transmission**: HTTPS API calls only

## 🚨 **Troubleshooting**

### **Common Issues**

**❌ "Figma access token not provided"**

```bash
# Add token to .env file
echo 'FIGMA_ACCESS_TOKEN=figd_your_token_here' >> .env
```

**❌ "Figma API access denied"**

- Check token is valid and not expired
- Ensure you have access to the Figma file
- Verify file URL is correct and public/accessible

**❌ "Figma file not found"**

- Check the Figma URL is correct
- Ensure file is not private (if using personal token)
- Verify file key extraction from URL

**❌ "Could not extract file key from URL"**

- Supported URL formats:
  - `https://www.figma.com/file/FILE_KEY/Title`
  - `https://www.figma.com/design/FILE_KEY/Title`
  - `https://figma.com/file/FILE_KEY/Title`

### **Debug Mode**

```bash
# Enable debug logging
export FIGMA_DEBUG=true

# Run with verbose output
python3 -c "
from figma_integration import FigmaIntegration
figma = FigmaIntegration()
result = figma.analyze_figma_design('YOUR_FIGMA_URL')
print('Analysis result:', result)
"
```

## 🎉 **Ready to Use!**

Your Jira-Figma Analyzer now provides **context-aware analysis** that considers:

✅ **Actual Figma designs** - Real component names, screens, and flows
✅ **Design complexity** - Implementation effort estimation  
✅ **Accessibility requirements** - WCAG compliance considerations
✅ **Implementation notes** - Technical guidance based on design patterns
✅ **Business context** - Financial advisory workflow integration
✅ **Knowledge base** - Your Confluence documentation context

**Test it now**: Add a real Figma URL to a ticket and see the enhanced analysis! 🚀
