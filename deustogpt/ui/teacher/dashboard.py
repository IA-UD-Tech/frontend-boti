"""
Teacher dashboard UI components.
"""

import streamlit as st
from deustogpt.utils.visualization import generate_sample_usage_data, create_usage_chart
from deustogpt.models.agent import Agent
from deustogpt.auth.google_auth import get_user_id

def show_teacher_dashboard():
    """Display the teacher dashboard."""
    st.header(f"Panel del Profesor: {st.session_state.user_email}")
    
    # Button for creating new agents
    if st.button("➕ Crear Nuevo Agente", use_container_width=True):
        st.session_state.showing_create_form = True
        st.rerun()
    
    if st.session_state.showing_create_form:
        from deustogpt.ui.teacher.agent_form import show_create_agent_form
        show_create_agent_form()
    else:
        display_teacher_agents()

def display_teacher_agents():
    """Display a grid of agents created by the teacher."""
    teacher_id = get_user_id()
    
    # Get agents from model or use sample data if none exist
    teacher_agents = Agent.get_by_teacher(teacher_id)
    
    if teacher_agents:
        agents = [{
            "id": agent.id,
            "name": agent.name,
            "students": len(agent.students),
            "usage": generate_sample_usage_data()
        } for agent in teacher_agents]
    else:
        # Sample data for demonstration
        agents = [
            {"id": 1, "name": "Introducción a los Computadores", "students": 15, "usage": generate_sample_usage_data()},
            {"id": 2, "name": "Programación de Aplicaciones", "students": 8, "usage": generate_sample_usage_data()},
            {"id": 3, "name": "Programación Técnica y Científica", "students": 12, "usage": generate_sample_usage_data()},
            {"id": 4, "name": "Calculabilidad y Complejidad", "students": 5, "usage": generate_sample_usage_data()}
        ]

    st.subheader("Mis Chatbots")

    # Use a 2-column layout for better spacing
    cols = st.columns(2)
    for i, agent in enumerate(agents):
        with cols[i % 2]:
            display_agent_card(agent)
            st.write("---")

def display_agent_card(agent):
    """Display a card for a single agent with interactive Plotly charts."""
    with st.container():
        # Agent name with emoji
        st.markdown(f"### 🤖 {agent['name']}")

        # Create metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            total_interactions = sum(agent["usage"]["counts"])
            st.metric("Total Interacciones", f"{total_interactions:,}")
        with col2:
            st.metric("Estudiantes", f"{agent['students']}")
        with col3:
            avg = total_interactions / len(agent["usage"]["counts"])
            st.metric("Media Diaria", f"{avg:.1f}")

        # Create interactive usage chart
        fig = create_usage_chart(agent["usage"])
        st.plotly_chart(fig, use_container_width=True)

        # Action buttons
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.button("✏️ Editar", key=f"edit_{agent['id']}")
        with col2:
            st.button("👥 Estudiantes", key=f"students_{agent['id']}")
        with col3:
            st.button("📊 Análisis", key=f"analytics_{agent['id']}")