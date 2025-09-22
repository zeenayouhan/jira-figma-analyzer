#!/usr/bin/env python3

# Read the current file
with open('jira_figma_analyzer.py', 'r') as f:
    content = f.read()

# Find and replace the AI prompt section for design questions
old_prompt_section = '''                        messages=[
                            {
                                "role": "system",
                                "content": """You are a senior UX/UI designer and React Native developer. Generate specific, actionable design questions based on the ticket requirements and relevant Figma design content.

IMPORTANT: Focus ONLY on design elements that are directly related to the ticket requirements. If the ticket is about a specific feature (like rating prompt, login, payment), ask questions ONLY about those specific components and flows.

Focus on:
- Specific screens and components mentioned in the design that relate to the ticket
- User flows and interactions relevant to the ticket feature
- Implementation details for the actual UI elements needed for this ticket
- Design system consistency questions for the specific feature
- Accessibility and responsive design for the specific components being built

Generate 5-8 highly specific questions that reference ONLY the design elements directly related to this ticket's requirements. 

IMPORTANT RULES:
1. ONLY ask about screens/components that are directly related to the ticket (e.g., profile editing, user settings, form fields)
2. DO NOT ask about unrelated screens like registration, onboarding, chat, or other features
3. Focus on the specific functionality mentioned in the ticket
4. If no relevant screens are found, ask generic implementation questions about the feature"""
                            },
                            {
                                "role": "user",
                                "content": f"""
                                Ticket: {ticket.title}
                                Description: {ticket.description}
                                
                                Key Requirements: {', '.join(ticket_keywords)}
                                
                                Relevant Figma Design Analysis:
                                {design_context}
                                
                                Generate specific design questions that focus ONLY on the design elements needed for this ticket's requirements. Do not ask about unrelated screens or components from the larger Figma file.
                                """
                            }
                        ],'''

new_prompt_section = '''                        messages=[
                            {
                                "role": "system",
                                "content": """You are a senior UX/UI designer and React Native developer. Generate highly specific design questions based ONLY on the exact ticket requirements provided.

CRITICAL REQUIREMENTS:
1. Read the ticket title and description carefully
2. Generate questions ONLY about the specific feature mentioned in the ticket
3. DO NOT ask about random screens or components from the Figma file
4. Focus on the exact UI elements needed for this specific feature
5. If it's about profile editing, ask ONLY about profile editing screens/forms
6. If it's about dropdowns, ask about dropdown design patterns
7. If no relevant screens are found in Figma, generate implementation questions for the specific feature

Generate 6-8 targeted questions about implementing THIS SPECIFIC FEATURE."""
                            },
                            {
                                "role": "user", 
                                "content": f"""
TICKET TO ANALYZE:
Title: {ticket.title}
Description: {ticket.description}

SPECIFIC FEATURE TO FOCUS ON: 
{ticket.title}

REQUIREMENTS FROM DESCRIPTION:
{ticket.description}

Generate design questions that are DIRECTLY related to implementing this specific feature: "{ticket.title}"

Focus on:
- UI components needed for this exact feature
- User interaction patterns for this specific functionality  
- Design system considerations for this feature
- Implementation details for this exact requirement
- Accessibility for this specific feature

DO NOT ask about:
- Random screens from the Figma file
- Unrelated features or components
- General app design questions

Example good questions for "Enable Editing of Occupation, Country of Residence":
- How should the occupation dropdown be designed and positioned in the profile form?
- What validation states should be shown for country selection?
- How should the save/update flow work for these specific fields?

Generate similar targeted questions for: {ticket.title}
                                """
                            }
                        ],'''

# Replace the prompt section
content = content.replace(old_prompt_section, new_prompt_section)

# Write back to file
with open('jira_figma_analyzer.py', 'w') as f:
    f.write(content)

print("✅ Created contextual design question generation focused on ticket content!")
