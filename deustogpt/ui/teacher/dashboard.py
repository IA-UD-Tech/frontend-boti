"""
Teacher dashboard UI components.
"""

import streamlit as st
from deustogpt.utils.visualization import generate_sample_usage_data, create_usage_chart
from deustogpt.models.agent import Agent
from deustogpt.auth.google_auth import get_user_id

def show_teacher_dashboard():
    """Display the teacher dashboard."""

    # Asegurar que la lista de agentes existe
    if "created_agents" not in st.session_state:
        st.session_state.created_agents = []

    # Si no hay agentes, crear uno de prueba solo si no está en session_state
    if not st.session_state.get("created_agents", []):
        test_agent = Agent.create("Agente de prueba", "Soy un asistente de prueba", "test_teacher")
        st.session_state.created_agents.append(test_agent.__dict__)  # Asegurar que se guarda bien


    st.header(f"Panel del Profesor: {st.session_state.user_email}")

    # "Editar" button
    if "editing_agent_id" in st.session_state and st.session_state.editing_agent_id:
        from deustogpt.ui.teacher.agent_form import show_edit_agent_form
        show_edit_agent_form(st.session_state.editing_agent_id)
        return
    
    # Button for creating new agents
    if st.button("➕ Crear Nuevo Agente", use_container_width=True):
        st.session_state.showing_create_form = True
        st.rerun()
    
    if st.session_state.showing_create_form:
        from deustogpt.ui.teacher.agent_form import show_create_agent_form
        show_create_agent_form()
    else:
        display_teacher_agents()

def get_agent_attr(agent, attr):
    """Devuelve el atributo 'attr' de 'agent', ya sea como dict o como objeto."""
    if isinstance(agent, dict):
        return agent.get(attr)
    else:
        return getattr(agent, attr)

def display_teacher_agents():
    """Display a grid of agents created by the teacher."""
    teacher_id = get_user_id()
    
    # Aseguramos que 'created_agents' existe en session_state.
    if "created_agents" not in st.session_state:
        st.session_state.created_agents = []
    
    # Intentamos obtener agentes reales del profesor.
    teacher_agents = Agent.get_by_teacher(teacher_id)

    # Si no se encontraron agentes reales, cargamos agentes de prueba.
    if not teacher_agents:
        st.warning("No has creado ningún chatbot. Se mostrarán agentes de ejemplo para prueba.")
        fake_agents = [
            {"id": "1001", "name": "Introducción a los Computadores", 
             "personality": "Fake personality", "created_by": teacher_id, 
             "created_at": "2025-03-07T00:00:00", "students": [], "files": []},
            {"id": "1002", "name": "Programación de Aplicaciones", 
             "personality": "Fake personality", "created_by": teacher_id, 
             "created_at": "2025-03-07T00:00:00", "students": [], "files": []},
            {"id": "1003", "name": "Programación Técnica y Científica", 
             "personality": "Fake personality", "created_by": teacher_id, 
             "created_at": "2025-03-07T00:00:00", "students": [], "files": []},
            {"id": "1004", "name": "Calculabilidad y Complejidad", 
             "personality": "Fake personality", "created_by": teacher_id, 
             "created_at": "2025-03-07T00:00:00", "students": [], "files": []}
        ]
        st.session_state.created_agents = fake_agents  # Guardamos los fake agents en session_state.
        teacher_agents = fake_agents

    # Convertimos los agentes a un formato para mostrarlos.
    agents = [{
        "id": get_agent_attr(agent, "id"),
        "name": get_agent_attr(agent, "name"),
        "students": len(get_agent_attr(agent, "students")),
        "usage": generate_sample_usage_data()
    } for agent in teacher_agents]

    st.subheader("Mis Chatbots")
    cols = st.columns(2)
    for i, agent in enumerate(agents):
        with cols[i % 2]:
            display_agent_card(agent)
            st.write("---")

# Función para gestionar el clic en "Editar"
def on_edit_click(agent_id):
    st.session_state.editing_agent_id = agent_id
    st.rerun()

def display_agent_card(agent):
    """Display a card for a single agent with interactive Plotly charts."""
    with st.container():
        st.markdown(f"### 🤖 {agent['name']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            total_interactions = sum(agent["usage"]["counts"])
            st.metric("Total Interacciones", f"{total_interactions:,}")
        with col2:
            st.metric("Estudiantes", f"{agent['students']}")
        with col3:
            avg = total_interactions / len(agent["usage"]["counts"])
            st.metric("Media Diaria", f"{avg:.1f}")

        fig = create_usage_chart(agent["usage"])
        st.plotly_chart(fig, use_container_width=True)

        def on_edit_click(agent_id):
            st.session_state.editing_agent_id = agent_id
            st.rerun()

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("✏️ Editar", key=f"edit_{agent['id']}"):
                on_edit_click(agent["id"])
        with col2:
            st.button("👥 Estudiantes", key=f"students_{agent['id']}")
        with col3:
            st.button("📊 Análisis", key=f"analytics_{agent['id']}")