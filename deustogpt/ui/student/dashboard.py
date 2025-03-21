"""
Student dashboard module - displays available agents and manages agent selection.
"""

import os
import streamlit as st
import random
from typing import List, Dict, Any, Optional

from deustogpt.models.agent import Agent
from deustogpt.models.user import User
from deustogpt.auth.google_auth import get_user_id
from deustogpt.ui.student.agent_card import display_agent_card
from deustogpt.auth.session import get_backend_user, get_current_user_name

def show_student_dashboard():
    """Display the main dashboard for students with available AI agents."""
    user_email = st.session_state.user_email
    user_id = st.session_state.backend_user_id or get_user_id()
    user_name = get_current_user_name()
    
    st.header(f"Panel del Estudiante: {user_name}")
    
    # Check if user is currently in a chat
    if st.session_state.current_agent_id:
        from deustogpt.ui.student.chat import show_chat_interface
        show_chat_interface(st.session_state.current_agent_id)
    else:
        display_available_agents(user_email)
        display_recent_activity(user_id)


def display_available_agents(user_email: str):
    """
    Display agents the student has access to.
    
    Args:
        user_email: Email of the current student
    """
    # Get agents student has access to
    student_agents = get_student_agents(user_email)
    
    if not student_agents:
        show_no_agents_message()
        return
    
    st.subheader("Mis Asistentes Virtuales")
    
    # Create grid of agent cards
    cols = st.columns(2)
    for i, agent in enumerate(student_agents):
        with cols[i % 2]:
            display_agent_card(agent, on_chat_clicked)
            st.write("")  # Add spacing between cards


def get_student_agents(user_email):
    """
    Get agents available to a student.
    """
    available_agents = []
    
    # Get agents the student is subscribed to via API
    agents = Agent.get_by_student(user_email)
    
    for agent in agents:
        # Format agent data for display
        available_agents.append({
            "id": agent.id,
            "name": agent.name,
            "description": agent.personality[:100] + "..." if agent.personality and len(agent.personality) > 100 else agent.personality,
            "teacher": get_teacher_name(agent.created_by),
            "icon": generate_agent_icon(agent.id)
        })
    
    return available_agents

def render_student_dashboard():
    """
    Render the student dashboard.
    """
    # Get current user email
    user_email = st.session_state.get("user_email", "")
    
    # Get agents available to the student
    agents = get_student_agents(user_email)
    
    if not agents:
        st.info("You don't have any agents available. Please contact your teacher.")
        return
    
    # Display the agents in a grid
    col1, col2 = st.columns(2)
    
    for i, agent in enumerate(agents):
        with col1 if i % 2 == 0 else col2:
            with st.container():
                st.markdown(f"### {agent['name']}")
                st.markdown(f"**By:** {agent['teacher']}")
                st.markdown(agent['description'] or "No description")
                if st.button("Chat", key=f"chat_btn_{agent['id']}"):
                    st.session_state.selected_agent = agent['id']
                    st.experimental_rerun()

def get_teacher_name(teacher_id: str) -> str:
    """
    Get teacher's name from their ID.
    
    Args:
        teacher_id: ID of the teacher
    
    Returns:
        Teacher's name or formatted email
    """
    if '@' in teacher_id:
        name = teacher_id.split('@')[0]
        # Capitalize and format name
        name_parts = name.split('.')
        formatted_name = ' '.join([part.capitalize() for part in name_parts])
        return f"Prof. {formatted_name}"
    return f"Prof. {teacher_id}"


def get_last_used(agent_id: str) -> str:
    """
    Get when the agent was last used by the student.
    
    Args:
        agent_id: ID of the agent
    
    Returns:
        String describing when the agent was last used
    """
    # In a real app, this would come from actual usage data
    options = ["Hoy", "Ayer", "Hace 2 días", "La semana pasada", "Hace 2 semanas", "Nuevo"]
    return random.choice(options)


def generate_agent_icon(agent_id: str) -> str:
    """
    Generate a consistent icon for an agent based on its ID.
    
    Args:
        agent_id: ID of the agent
    
    Returns:
        Emoji icon for the agent
    """
    # Create a deterministic icon based on agent ID
    icons = ["🤖", "🧠", "📚", "💡", "🔍", "📊", "🧮", "⚙️", "💻", "🧪"]
    hash_value = sum(ord(c) for c in str(agent_id))
    return icons[hash_value % len(icons)]


def on_chat_clicked(agent_id: str):
    """
    Handle click on chat button.
    
    Args:
        agent_id: ID of the selected agent
    """
    st.session_state.current_agent_id = agent_id
    
    # Initialize message history with welcome message
    agent = Agent.get_by_id(agent_id)
    agent_name = agent.name if agent else f"Agente #{agent_id}"
    
    st.session_state.messages = [{
        "role": "assistant", 
        "content": f"¡Hola! Soy el asistente de {agent_name}. ¿En qué puedo ayudarte hoy?"
    }]
    
    st.rerun()


def show_no_agents_message():
    """Display a message when the student has no agents."""
    st.info("""
        Aún no tienes ningún asistente virtual asignado. 
        
        Tu profesor necesita añadirte a un asistente virtual para que puedas usarlo.
    """)
    
    with st.expander("¿Cómo funciona?"):
        st.write("""
            1. Los profesores crean asistentes virtuales para sus asignaturas
            2. Te añaden como estudiante usando tu correo electrónico
            3. Los asistentes aparecerán automáticamente en tu panel
            4. Podrás chatear con ellos para resolver tus dudas
        """)


def display_recent_activity(user_id: str):
    """
    Display recent activity for the student.
    
    Args:
        user_id: ID of the current student
    """
    # In a real app, this would show actual recent interactions
    if "chat_logs" in st.session_state and st.session_state.chat_logs:
        st.subheader("Actividad Reciente")
        
        # Show only this user's logs
        user_logs = [log for log in st.session_state.chat_logs 
                     if log.get("user_id") == user_id]
                     
        if user_logs:
            for log in user_logs[-5:]:  # Show last 5 interactions
                agent_id = log.get("agent_id")
                agent = Agent.get_by_id(agent_id) if agent_id else None
                agent_name = agent.name if agent else "Asistente desconocido"
                
                with st.container():
                    st.caption(f"Con {agent_name}")
                    if log.get("role") == "user":
                        st.write(f"📤 Tú: {log.get('content')[:50]}...")
                    else:
                        st.write(f"📥 Asistente: {log.get('content')[:50]}...")


def get_sample_agents() -> List[Dict[str, Any]]:
    """
    Get sample agent data for demonstration purposes.
    
    Returns:
        List of sample agent data
    """
    return [
        {
            "id": 1, 
            "name": "Introducción a los Computadores", 
            "teacher": "Prof. Aritz Bilbao", 
            "description": "Asistente para consultas sobre fundamentos de arquitectura de computadores y sistemas operativos.",
            "last_used": "Ayer",
            "icon": "💻"
        },
        {
            "id": 2, 
            "name": "Programación de Aplicaciones", 
            "teacher": "Prof. Andoni Eguíluz", 
            "description": "Resuelve dudas sobre desarrollo de aplicaciones, patrones de diseño y arquitectura software.",
            "last_used": "Hace 3 días",
            "icon": "🧮"
        },
        {
            "id": 3, 
            "name": "Programación Técnica y Científica", 
            "teacher": "Prof. Carlos Quesada", 
            "description": "Ayuda con algoritmos matemáticos, análisis de datos y visualización científica.",
            "last_used": "La semana pasada",
            "icon": "📊"
        }
    ]