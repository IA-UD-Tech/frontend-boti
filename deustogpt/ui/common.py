"""
Common UI components shared across the application.
"""

import streamlit as st
from deustogpt.auth.session import get_backend_user

def setup_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="DeustoGPT",
        page_icon="🤖",
        layout="wide"
    )

def apply_custom_css():
    """Apply custom CSS styling to the application."""
    try:
        with open("deustogpt/static/css/chat_theme.html") as f:
            custom_css = f.read()
        st.markdown(custom_css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found.")

def show_login_screen():
    """Display the initial login screen with options for teachers and students."""
    st.header("Bienvenido a DeustoGPT")
    st.write("Selecciona tu tipo de usuario para continuar:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👨‍🏫 Para Profesores (@deusto.es)")
        if st.button("Acceso para profesores", key="teacher_login"):
            from deustogpt.auth.google_auth import login_with_google
            login_with_google("teacher")
            
    with col2:
        st.subheader("🧑‍🎓 Para Estudiantes (@opendeusto.es)")
        if st.button("Acceso para estudiantes", key="student_login"):
            from deustogpt.auth.google_auth import login_with_google
            login_with_google("student")

def show_header(user_email: str):
    """
    Display the application header with user information.
    
    Args:
        user_email: Email of the current user
    """
    backend_user = get_backend_user()
    
    with st.container():
        cols = st.columns([0.7, 0.3])
        
        with cols[0]:
            st.markdown("## 🤖 DeustoGPT")
        
        with cols[1]:
            # Show user info with avatar if available
            user_container = st.container()
            with user_container:
                if backend_user and backend_user.get("avatar_url"):
                    avatar_url = backend_user.get("avatar_url")
                    name = backend_user.get("name", user_email.split('@')[0])
                    
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; justify-content:flex-end;">
                        <span style="margin-right:10px;">{name}</span>
                        <img src="{avatar_url}" width="40" height="40" 
                             style="border-radius:50%;" alt="User Avatar">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Fallback to just email
                    st.write(f"👤 {user_email}")
                    
            if st.button("Cerrar sesión", key="logout"):
                # Clear session state and reload
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
                
    st.markdown("---")