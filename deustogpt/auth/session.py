"""
Session state management for Streamlit application.
"""

import streamlit as st


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


def is_authenticated():
    """Check if the user is currently authenticated."""
    return st.session_state.google_token and st.session_state.user_role


def get_current_user_role():
    """Get the current user's role."""
    return st.session_state.user_role


def get_current_user_email():
    """Get the current user's email address."""
    return st.session_state.user_email