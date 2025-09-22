#!/usr/bin/env python3

# Read the current file
with open('jira_figma_analyzer.py', 'r') as f:
    content = f.read()

# Find and replace the fallback questions section
old_fallback = '''        # Ensure we always have some questions
        if not questions:
            questions = [
                "What are the specific UI components needed for this feature?",
                "How should the user interface be structured for this functionality?",
                "What are the design system requirements for this feature?",
                "How should the user flow be designed for this functionality?",
                "What responsive design considerations are needed?",
                "What accessibility features should be implemented?",
                "How should the visual hierarchy be established?",
                "What interaction patterns should be used?"
            ]'''

new_fallback = '''        # Ensure we always have some questions - make them specific to the ticket
        if not questions:
            # Generate contextual fallback questions based on ticket content
            ticket_context = f"{ticket.title} {ticket.description}".lower()
            
            # Specific question templates based on ticket type
            if any(term in ticket_context for term in ['edit', 'update', 'modify', 'change']):
                questions = [
                    f"How should the editing interface be designed for {ticket.title.lower()}?",
                    f"What validation states are needed for the {ticket.title.lower()} feature?",
                    f"How should the save/update flow work for {ticket.title.lower()}?",
                    f"What are the form field requirements for {ticket.title.lower()}?",
                    f"How should error handling be displayed for {ticket.title.lower()}?",
                    f"What accessibility considerations are needed for {ticket.title.lower()}?"
                ]
            elif any(term in ticket_context for term in ['dropdown', 'select', 'picker']):
                questions = [
                    f"How should the dropdown/picker be styled for {ticket.title.lower()}?",
                    f"What are the selection states and animations needed?",
                    f"How should the dropdown options be organized and displayed?",
                    f"What search/filter functionality is needed in the dropdown?",
                    f"How should the selected value be displayed?",
                    f"What accessibility features are needed for the dropdown?"
                ]
            elif any(term in ticket_context for term in ['profile', 'user', 'account']):
                questions = [
                    f"How should the profile section be organized for {ticket.title.lower()}?",
                    f"What form layout works best for profile editing?",
                    f"How should profile changes be saved and confirmed?",
                    f"What validation is needed for profile fields?",
                    f"How should the profile update success state be shown?",
                    f"What accessibility considerations are needed for profile editing?"
                ]
            else:
                # Generic but still contextual
                questions = [
                    f"What are the specific UI components needed for {ticket.title.lower()}?",
                    f"How should the user flow be designed for {ticket.title.lower()}?",
                    f"What validation and error states are needed for {ticket.title.lower()}?",
                    f"How should the success state be displayed for {ticket.title.lower()}?",
                    f"What responsive design considerations are needed for {ticket.title.lower()}?",
                    f"What accessibility features should be implemented for {ticket.title.lower()}?"
                ]'''

# Replace the fallback section
content = content.replace(old_fallback, new_fallback)

# Write back to file
with open('jira_figma_analyzer.py', 'w') as f:
    f.write(content)

print("✅ Improved fallback questions to be ticket-specific!")
