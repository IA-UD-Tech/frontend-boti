"""
Session state management for Streamlit application.
"""

import streamlit as st
from typing import Optional, Dict, Any
from deustogpt.api.user_api import get_user


def initialize_session_state():
    """Initialize all required session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "embedded_documents" not in st.session_state:
        st.session_state.embedded_documents = {}
    if "google_token" not in st.session_state:
        st.session_state.google_token = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "current_agent_id" not in st.session_state:
        st.session_state.current_agent_id = None
    if "showing_create_form" not in st.session_state:
        st.session_state.showing_create_form = False
    if "created_agents" not in st.session_state:
        st.session_state.created_agents = []
    # Backend user data
    if "backend_user_id" not in st.session_state:
        st.session_state.backend_user_id = None
    if "backend_user" not in st.session_state:
        st.session_state.backend_user = None


def is_authenticated():
    """Check if the user is currently authenticated."""
    return st.session_state.google_token and st.session_state.user_role


def get_backend_user() -> Optional[Dict[str, Any]]:
    """
    Get the current user's data from the backend.
    
    Returns:
        User data from backend or None if not available
    """
    if not st.session_state.backend_user and st.session_state.backend_user_id:
        # If we have an ID but no user data, try to fetch it
        st.session_state.backend_user = get_user(st.session_state.backend_user_id)
    
    return st.session_state.backend_user


def get_current_user_role() -> str:
    """
    Get the current user role.
    
    Returns:
        User role (teacher/student)
    """
    return st.session_state.user_role


def get_current_user_name() -> str:
    """
    Get the current user's name.
    
    Returns:
        User name from backend or formatted email if not available
    """
    user = get_backend_user()
    if user and user.get("name"):
        return user.get("name")
    
    # Fallback to email-based name
    email = st.session_state.user_email
    if email:
        name = email.split('@')[0]
        # Format name
        name_parts = name.split('.')
        return ' '.join([part.capitalize() for part in name_parts])
    
    return "Usuario"