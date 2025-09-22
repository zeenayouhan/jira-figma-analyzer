#!/usr/bin/env python3
"""
Add delete buttons to the stored tickets section
"""

def add_delete_buttons():
    # Read the current file
    with open('complete_streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Find the section where tickets are displayed and add delete buttons
    old_ticket_display = '''                st.markdown(f"**Created:** {ticket.get('created_at', 'Unknown')}")
                st.markdown(f"**Questions:** {ticket.get('question_count', 0)}")
                st.markdown(f"**Test Cases:** {ticket.get('test_case_count', 0)}")
                st.markdown(f"**Risks:** {ticket.get('risk_count', 0)}")
                
                # Unique key for view button
                ticket_unique_id = ticket.get('ticket_id') or ticket.get('id') or f"ticket_{idx}"
                if st.button(f"🔍 View Full Analysis", key=f"view_full_{ticket_unique_id}"):
                    # Load and display full analysis
                    ticket_id = ticket.get('ticket_id') or ticket.get('id')
                    if ticket_id:
                        full_ticket = storage.get_ticket(ticket_id)
                        if full_ticket:
                            display_full_analysis_modal(full_ticket)
                        else:
                            st.error("Could not load ticket details")
                    else:
                        st.error("Invalid ticket ID")'''
    
    new_ticket_display = '''                st.markdown(f"**Created:** {ticket.get('created_at', 'Unknown')}")
                st.markdown(f"**Questions:** {ticket.get('question_count', 0)}")
                st.markdown(f"**Test Cases:** {ticket.get('test_case_count', 0)}")
                st.markdown(f"**Risks:** {ticket.get('risk_count', 0)}")
                
                # Action buttons
                col1, col2 = st.columns([1, 1])
                ticket_unique_id = ticket.get('ticket_id') or ticket.get('id') or f"ticket_{idx}"
                
                with col1:
                    if st.button(f"🔍 View Full Analysis", key=f"view_full_{ticket_unique_id}"):
                        # Load and display full analysis
                        ticket_id = ticket.get('ticket_id') or ticket.get('id')
                        if ticket_id:
                            full_ticket = storage.get_ticket(ticket_id)
                            if full_ticket:
                                display_full_analysis_modal(full_ticket)
                            else:
                                st.error("Could not load ticket details")
                        else:
                            st.error("Invalid ticket ID")
                
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{ticket_unique_id}", type="secondary"):
                        # Delete the ticket
                        ticket_id = ticket.get('ticket_id') or ticket.get('id')
                        if ticket_id:
                            if storage.delete_ticket(ticket_id):
                                st.success(f"✅ Ticket {ticket_id} deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete ticket")
                        else:
                            st.error("Invalid ticket ID")'''
    
    content = content.replace(old_ticket_display, new_ticket_display)
    
    # Also add delete buttons to search results
    old_search_display = '''                    st.markdown(f"**Description:** {result.get('description', 'No description')[:200]}...")
                    st.markdown(f"**Stored:** {result.get('created_at', 'Unknown date')}")
                    # Use ticket_id or index to ensure unique keys
                    unique_key = result.get('ticket_id') or result.get('id') or f"search_{idx}"
                    if st.button(f"🔍 View Full Analysis", key=f"view_search_{unique_key}"):
                        # Load and display full analysis
                        ticket_id = result.get('ticket_id') or result.get('id')
                        if ticket_id:
                            full_ticket = storage.get_ticket(ticket_id)
                            if full_ticket:
                                display_full_analysis_modal(full_ticket)
                            else:
                                st.error("Could not load ticket details")
                        else:
                            st.error("Invalid ticket ID")'''
    
    new_search_display = '''                    st.markdown(f"**Description:** {result.get('description', 'No description')[:200]}...")
                    st.markdown(f"**Stored:** {result.get('created_at', 'Unknown date')}")
                    
                    # Action buttons for search results
                    col1, col2 = st.columns([1, 1])
                    unique_key = result.get('ticket_id') or result.get('id') or f"search_{idx}"
                    
                    with col1:
                        if st.button(f"🔍 View Full Analysis", key=f"view_search_{unique_key}"):
                            # Load and display full analysis
                            ticket_id = result.get('ticket_id') or result.get('id')
                            if ticket_id:
                                full_ticket = storage.get_ticket(ticket_id)
                                if full_ticket:
                                    display_full_analysis_modal(full_ticket)
                                else:
                                    st.error("Could not load ticket details")
                            else:
                                st.error("Invalid ticket ID")
                    
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_search_{unique_key}", type="secondary"):
                            # Delete the ticket
                            ticket_id = result.get('ticket_id') or result.get('id')
                            if ticket_id:
                                if storage.delete_ticket(ticket_id):
                                    st.success(f"✅ Ticket {ticket_id} deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete ticket")
                            else:
                                st.error("Invalid ticket ID")'''
    
    content = content.replace(old_search_display, new_search_display)
    
    # Add a "Delete All" button at the top of the stored tickets section
    old_stored_tickets_header = '''    # Recent tickets
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📅 Stored Tickets")
    with col2:
        show_all = st.checkbox("Show All Tickets", value=False)'''
    
    new_stored_tickets_header = '''    # Recent tickets
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("📅 Stored Tickets")
    with col2:
        show_all = st.checkbox("Show All Tickets", value=False)
    with col3:
        if st.button("🗑️ Delete All", type="secondary", help="Delete all stored tickets"):
            if st.session_state.get('confirm_delete_all', False):
                if storage.delete_all_tickets():
                    st.success("✅ All tickets deleted successfully!")
                    st.session_state['confirm_delete_all'] = False
                    st.rerun()
                else:
                    st.error("❌ Failed to delete all tickets")
            else:
                st.session_state['confirm_delete_all'] = True
                st.warning("⚠️ Click again to confirm deletion of ALL tickets")'''
    
    content = content.replace(old_stored_tickets_header, new_stored_tickets_header)
    
    # Write the updated content
    with open('complete_streamlit_app.py', 'w') as f:
        f.write(content)
    
    print("✅ Added delete buttons to stored tickets section")

if __name__ == "__main__":
    add_delete_buttons()
