"""
Main entry point for the DeustoGPT application.
"""

import streamlit as st
import requests
from deustogpt.config import ensure_upload_dir
from deustogpt.ui.common import setup_page, apply_custom_css, show_login_screen, show_header
from deustogpt.auth.session import initialize_session_state, is_authenticated, get_current_user_role
from deustogpt.auth.google_auth import handle_oauth_callback, get_user_id
import os

API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

def check_api_health():
    """Check if the backend API is reachable and operational."""
    try:
        response = requests.get(f"{API_BASE_URL}/healthcheck")
        if response.status_code == 200:
            return True
        return False
    except Exception:
        return False

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

    if not check_api_health():
        st.error("Could not connect to the backend API. Using offline mode.")

if __name__ == "__main__":
    main()