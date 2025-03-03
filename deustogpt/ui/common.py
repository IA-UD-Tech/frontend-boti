"""
Common UI components shared across the application.
"""

import streamlit as st

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

def show_header(user_email):
    """Show the application header with user information."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("DeustoGPT")
    with col2:
        st.text(f"Usuario: {user_email}")
        if st.button("Cerrar sesión", key="logout"):
            from deustogpt.auth.google_auth import logout
            logout()