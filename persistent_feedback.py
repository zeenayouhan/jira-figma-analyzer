import streamlit as st
import uuid

class PersistentFeedbackForm:
    """A feedback form that persists across Streamlit reruns during analysis"""
    
    def __init__(self, ticket_id, feedback_system):
        self.ticket_id = ticket_id
        self.feedback_system = feedback_system
        self.base_key = f"persistent_feedback_{ticket_id}"
        
    def render(self):
        """Render a persistent feedback form"""
        
        # Create a unique form key that includes a UUID for this session
        if f"{self.base_key}_form_id" not in st.session_state:
            st.session_state[f"{self.base_key}_form_id"] = str(uuid.uuid4())[:8]
        
        form_id = st.session_state[f"{self.base_key}_form_id"]
        
        # Initialize persistent rating states
        overall_key = f"{self.base_key}_overall_{form_id}"
        questions_key = f"{self.base_key}_questions_{form_id}"
        testcases_key = f"{self.base_key}_testcases_{form_id}"
        risks_key = f"{self.base_key}_risks_{form_id}"
        comment_key = f"{self.base_key}_comment_{form_id}"
        submitted_key = f"{self.base_key}_submitted_{form_id}"
        
        # Initialize session state if not exists
        if overall_key not in st.session_state:
            st.session_state[overall_key] = 3
        if questions_key not in st.session_state:
            st.session_state[questions_key] = 3
        if testcases_key not in st.session_state:
            st.session_state[testcases_key] = 3
        if risks_key not in st.session_state:
            st.session_state[risks_key] = 3
        if comment_key not in st.session_state:
            st.session_state[comment_key] = ""
        if submitted_key not in st.session_state:
            st.session_state[submitted_key] = False
        
        # Show submitted message if already submitted
        if st.session_state[submitted_key]:
            st.success("✅ Thank you for your feedback! Your ratings help improve the system.")
            
            # Show current ratings
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall", f"{st.session_state[overall_key]}⭐")
            with col2:
                st.metric("Questions", f"{st.session_state[questions_key]}⭐")
            with col3:
                st.metric("Test Cases", f"{st.session_state[testcases_key]}⭐")
            with col4:
                st.metric("Risks", f"{st.session_state[risks_key]}⭐")
            
            if st.button("📝 Submit New Feedback", key=f"new_feedback_{form_id}"):
                # Reset form for new feedback
                st.session_state[submitted_key] = False
                st.session_state[f"{self.base_key}_form_id"] = str(uuid.uuid4())[:8]
                st.rerun()
            
            return
        
        # Create the persistent form
        st.markdown("### 📝 Feedback - Help Improve The System")
        st.markdown("*Your ratings persist during analysis and help train our AI to generate better questions!*")
        
        with st.form(key=f"feedback_form_{form_id}"):
            feedback_col1, feedback_col2 = st.columns(2)
            
            with feedback_col1:
                st.markdown("**Rate the overall analysis quality:**")
                overall_rating = st.radio(
                    "Overall Rating",
                    [1, 2, 3, 4, 5],
                    format_func=lambda x: f"{x} {'⭐' * x}",
                    horizontal=True,
                    index=st.session_state[overall_key] - 1,
                    key=f"form_overall_{form_id}"
                )
                
                st.markdown("**Rate the business questions:**")
                questions_rating = st.selectbox(
                    "Questions Quality",
                    [1, 2, 3, 4, 5],
                    format_func=lambda x: f"{x} {'⭐' * x}",
                    index=st.session_state[questions_key] - 1,
                    key=f"form_questions_{form_id}"
                )
            
            with feedback_col2:
                st.markdown("**Rate the test cases:**")
                test_cases_rating = st.selectbox(
                    "Test Cases Quality",
                    [1, 2, 3, 4, 5],
                    format_func=lambda x: f"{x} {'⭐' * x}",
                    index=st.session_state[testcases_key] - 1,
                    key=f"form_testcases_{form_id}"
                )
                
                st.markdown("**Rate the risk analysis:**")
                risks_rating = st.selectbox(
                    "Risks Quality",
                    [1, 2, 3, 4, 5],
                    format_func=lambda x: f"{x} {'⭐' * x}",
                    index=st.session_state[risks_key] - 1,
                    key=f"form_risks_{form_id}"
                )
            
            feedback_comment = st.text_area(
                "Additional comments (optional)",
                value=st.session_state[comment_key],
                key=f"form_comment_{form_id}",
                placeholder="What could be improved? Were the questions relevant to your ticket?"
            )
            
            submitted = st.form_submit_button("🚀 Submit Feedback", use_container_width=True)
            
            if submitted:
                try:
                    # Store feedback
                    self.feedback_system.store_feedback(
                        ticket_id=self.ticket_id,
                        overall_rating=overall_rating,
                        questions_rating=questions_rating,
                        test_cases_rating=test_cases_rating,
                        risks_rating=risks_rating,
                        comment=feedback_comment
                    )
                    
                    # Update session state
                    st.session_state[overall_key] = overall_rating
                    st.session_state[questions_key] = questions_rating
                    st.session_state[testcases_key] = test_cases_rating
                    st.session_state[risks_key] = risks_rating
                    st.session_state[comment_key] = feedback_comment
                    st.session_state[submitted_key] = True
                    
                    st.success("✅ Feedback submitted successfully! Thank you for helping improve the system.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error submitting feedback: {str(e)}")
        
        # Show current selections outside the form (for persistence)
        if not st.session_state[submitted_key]:
            st.markdown("---")
            st.markdown("**📊 Current Selections:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall", f"{st.session_state[overall_key]}⭐")
            with col2:
                st.metric("Questions", f"{st.session_state[questions_key]}⭐")
            with col3:
                st.metric("Test Cases", f"{st.session_state[testcases_key]}⭐")
            with col4:
                st.metric("Risks", f"{st.session_state[risks_key]}⭐") 