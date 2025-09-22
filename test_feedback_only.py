#!/usr/bin/env python3
"""Minimal test app for feedback system only"""

import streamlit as st
from dataclasses import dataclass

@dataclass
class TestTicket:
    ticket_id: str = "TEST-123"
    title: str = "Test Ticket"

def test_feedback_section():
    """Test the feedback section in isolation"""
    st.header("🧪 Feedback System Test")
    
    # Create a mock result
    result = TestTicket()
    
    st.subheader("📝 Feedback")
    st.markdown("Help us improve by rating the quality of the generated analysis!")
    
    try:
        # Initialize session state for ratings to prevent disappearing
        feedback_key = f"feedback_{result.ticket_id}"
        if f"{feedback_key}_submitted" not in st.session_state:
            st.session_state[f"{feedback_key}_submitted"] = False
        
        # Initialize rating session states
        if f"overall_{result.ticket_id}" not in st.session_state:
            st.session_state[f"overall_{result.ticket_id}"] = 3
        if f"questions_{result.ticket_id}" not in st.session_state:
            st.session_state[f"questions_{result.ticket_id}"] = 3
        if f"testcases_{result.ticket_id}" not in st.session_state:
            st.session_state[f"testcases_{result.ticket_id}"] = 3
        if f"risks_{result.ticket_id}" not in st.session_state:
            st.session_state[f"risks_{result.ticket_id}"] = 3
        
        # Only show feedback form if not already submitted
        if not st.session_state[f"{feedback_key}_submitted"]:
            # Feedback form
            feedback_col1, feedback_col2 = st.columns(2)
            
            with feedback_col1:
                st.markdown("**Rate the overall analysis quality:**")
                overall_rating = st.radio(
                    "Overall Rating",
                    [1, 2, 3, 4, 5],
                    format_func=lambda x: f"{x} {'⭐' * x}",
                    horizontal=True,
                    key=f"overall_{result.ticket_id}",
                    index=[1, 2, 3, 4, 5].index(st.session_state[f"overall_{result.ticket_id}"])
                )
                
                feedback_comment = st.text_area(
                    "Additional comments (optional)",
                    placeholder="What was good? What could be improved?",
                    key=f"comment_{result.ticket_id}"
                )
            
            with feedback_col2:
                st.markdown("**Rate specific aspects:**")
                
                questions_rating = st.selectbox(
                    "Questions Quality",
                    [1, 2, 3, 4, 5],
                    format_func=lambda x: f"{x} ⭐",
                    key=f"questions_{result.ticket_id}",
                    index=[1, 2, 3, 4, 5].index(st.session_state[f"questions_{result.ticket_id}"])
                )
                
                test_cases_rating = st.selectbox(
                    "Test Cases Quality", 
                    [1, 2, 3, 4, 5],
                    format_func=lambda x: f"{x} ⭐",
                    key=f"testcases_{result.ticket_id}",
                    index=[1, 2, 3, 4, 5].index(st.session_state[f"testcases_{result.ticket_id}"])
                )
                
                risks_rating = st.selectbox(
                    "Risk Analysis Quality",
                    [1, 2, 3, 4, 5], 
                    format_func=lambda x: f"{x} ⭐",
                    key=f"risks_{result.ticket_id}",
                    index=[1, 2, 3, 4, 5].index(st.session_state[f"risks_{result.ticket_id}"])
                )
            
            # Update session state with current values - REMOVED BECAUSE IT CAUSES ERROR
            # st.session_state[f"overall_{result.ticket_id}"] = overall_rating
            # st.session_state[f"questions_{result.ticket_id}"] = questions_rating
            # st.session_state[f"testcases_{result.ticket_id}"] = test_cases_rating
            # st.session_state[f"risks_{result.ticket_id}"] = risks_rating
            
            # Show current ratings summary
            st.markdown("---")
            st.markdown("**📊 Current Ratings:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall", f"{overall_rating}⭐")
            with col2:
                st.metric("Questions", f"{questions_rating}⭐")
            with col3:
                st.metric("Test Cases", f"{test_cases_rating}⭐")
            with col4:
                st.metric("Risks", f"{risks_rating}⭐")
            
            if st.button("📤 Submit Feedback", key=f"submit_feedback_{result.ticket_id}"):
                try:
                    # Mark as submitted to prevent re-submission
                    st.session_state[f"{feedback_key}_submitted"] = True
                    st.success("🎉 Thank you for your feedback! This helps us improve the analysis quality.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error submitting feedback: {e}")
        else:
            st.info("✅ Thank you! Your feedback has been submitted for this ticket.")
            if st.button("📝 Submit New Feedback", key=f"reset_feedback_{result.ticket_id}"):
                st.session_state[f"{feedback_key}_submitted"] = False
                st.rerun()
    
    except Exception as e:
        st.error(f"⚠️ Feedback system error: {e}")
        import traceback
        st.error(traceback.format_exc())

def main():
    st.set_page_config(page_title="Feedback Test", page_icon="🧪")
    
    st.title("🧪 Feedback System Test")
    st.markdown("This is a test to verify the feedback system works correctly.")
    
    test_feedback_section()
    
    st.markdown("---")
    st.markdown("**🎯 Test Instructions:**")
    st.markdown("1. Click on any rating (radio buttons or selectboxes)")
    st.markdown("2. Verify that the rating **stays selected** (doesn't disappear)")
    st.markdown("3. Check that the **Current Ratings** section shows your selections")
    st.markdown("4. Try submitting feedback to test the complete flow")

if __name__ == "__main__":
    main() 