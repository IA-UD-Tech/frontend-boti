"""
Main entry point for the DeustoGPT application.
"""

import streamlit as st
from deustogpt.config import ensure_upload_dir
from deustogpt.ui.common import setup_page, apply_custom_css, show_login_screen, show_header
from deustogpt.auth.session import initialize_session_state, is_authenticated, get_current_user_role
from deustogpt.auth.google_auth import handle_oauth_callback, get_user_id

def main():
    # Setup the page and apply custom styling
    setup_page()
    apply_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Ensure upload directory exists
    ensure_upload_dir()
    
    # Check for OAuth callback
    if not is_authenticated() and "code" in st.query_params:
        handle_oauth_callback(st.query_params)

    # If not authenticated, show login screen
    if not is_authenticated():
        show_login_screen()
        return

    # Show header with user info
    show_header(st.session_state.user_email)
    
    # Route to the appropriate view based on user role
    user_role = get_current_user_role()
    if user_role == "teacher":
        from deustogpt.ui.teacher.dashboard import show_teacher_dashboard
        show_teacher_dashboard()
    elif user_role == "student":
        from deustogpt.ui.student.dashboard import show_student_dashboard
        show_student_dashboard()
    else:
        st.error(f"Rol desconocido: {user_role}")

if __name__ == "__main__":
    main()