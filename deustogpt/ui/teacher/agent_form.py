"""
Agent form module - form for creating and editing agents.
"""

import streamlit as st
import os
from typing import List, Optional

from deustogpt.models.agent import Agent
from deustogpt.auth.google_auth import get_user_id
from deustogpt.services.document_service import DocumentService
from deustogpt.config import UPLOAD_DIR


def show_create_agent_form():
    """Display form for creating a new agent."""
    st.subheader("Crear Nuevo Agente de Chat")
    
    doc_service = DocumentService()
    
    with st.form("create_agent_form"):
        # Basic information
        agent_name = st.text_input("Nombre del Agente", 
                                 placeholder="Ej: Asistente de Programación Python")
        
        # Personality/prompt with examples
        st.markdown("### Personalidad / Prompt del Agente")
        st.caption("""
            Define cómo se comportará el asistente. Sé específico sobre su personalidad, 
            tono, nivel académico, y tipo de respuestas que debe dar.
        """)
        
        with st.expander("Ver ejemplos de prompts"):
            st.code("""
            Eres un asistente especializado en Programación Python para estudiantes universitarios.
            Debes explicar los conceptos de forma clara y concisa, utilizando ejemplos prácticos.
            Cuando te pidan código, proporciona explicaciones línea por línea.
            Si no conoces la respuesta, indica honestamente que no lo sabes, pero sugiere dónde 
            pueden buscar más información.
            """)
            
            st.code("""
            Eres un tutor de Arquitectura de Computadores. Explica los conceptos de manera
            accesible pero precisa. Utiliza analogías para facilitar la comprensión de temas complejos.
            Evita jerga innecesaria, pero utiliza la terminología técnica correcta cuando sea apropiado.
            Cuando un estudiante tenga dificultades, guíalo con preguntas para que llegue a la respuesta.
            """)
            
        personality = st.text_area("Personalidad / Prompt", 
                                 height=150,
                                 placeholder="Define cómo se comportará el agente...")
        
        # File upload
        st.markdown("### Conocimiento Base (Opcional)")
        st.caption("""
            Sube archivos para proporcionar conocimiento especializado al agente.
            Formatos soportados: PDF, TXT, DOCX, CSV, MD
        """)
        
        uploaded_files = st.file_uploader(
            "Subir archivos para el conocimiento base", 
            accept_multiple_files=True,
            type=["pdf", "txt", "docx", "csv", "md"]
        )
        
        # Student subscription
        st.markdown("### Estudiantes")
        st.caption("""
            Añade estudiantes que tendrán acceso a este agente.
            Ingresa un correo electrónico por línea.
        """)
        
        student_emails = st.text_area(
            "Correos electrónicos de estudiantes", 
            height=100,
            placeholder="estudiante1@opendeusto.es\nestudiante2@opendeusto.es"
        )
        
        # Advanced settings toggle
        show_advanced = st.checkbox("Mostrar configuración avanzada")
        
        if show_advanced:
            st.markdown("### Configuración Avanzada")
            
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider(
                    "Temperatura", 
                    min_value=0.0, 
                    max_value=1.0, 
                    value=0.7, 
                    step=0.1,
                    help="Mayor valor = más creatividad, menor valor = más consistencia"
                )
            with col2:
                max_tokens = st.slider(
                    "Longitud máxima de respuesta", 
                    min_value=100, 
                    max_value=4000, 
                    value=1000, 
                    step=100,
                    help="Número máximo de tokens en cada respuesta"
                )
                
            include_search = st.checkbox(
                "Buscar en la web cuando no conozca la respuesta", 
                value=False,
                help="Permite al agente buscar información actualizada en internet"
            )
        else:
            # Default values
            temperature = 0.7
            max_tokens = 1000
            include_search = False
        
        # Submit button
        submitted = st.form_submit_button("Crear Agente", use_container_width=True)
        
        if submitted:
            # Validate form
            validation_error = validate_form(agent_name, personality)
            
            if validation_error:
                st.error(validation_error)
            else:
                # Process agent creation
                create_agent_result = create_new_agent(
                    name=agent_name,
                    personality=personality,
                    uploaded_files=uploaded_files,
                    student_emails=student_emails,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    include_search=include_search,
                    doc_service=doc_service
                )
                
                if create_agent_result["success"]:
                    agent_id = create_agent_result["agent_id"]
                    st.success(f"¡Agente '{agent_name}' creado exitosamente!")
                    
                    # Reset form state
                    st.session_state.showing_create_form = False
                    st.rerun()
                else:
                    st.error(f"Error al crear el agente: {create_agent_result['error']}")
    
    # Cancel button outside the form
    if st.button("Cancelar", key="cancel_create_form"):
        st.session_state.showing_create_form = False
        st.rerun()


def validate_form(agent_name: str, personality: str) -> Optional[str]:
    """
    Validate form inputs.
    
    Args:
        agent_name: Name of the agent
        personality: Personality/prompt for the agent
        
    Returns:
        Error message if validation fails, None if validation succeeds
    """
    if not agent_name:
        return "El nombre del agente es obligatorio"
        
    if not personality:
        return "La personalidad/prompt del agente es obligatoria"
        
    if len(agent_name) < 3:
        return "El nombre del agente debe tener al menos 3 caracteres"
        
    if len(personality) < 20:
        return "El prompt debe ser más descriptivo (mínimo 20 caracteres)"
        
    return None


def create_new_agent(name, personality, uploaded_files, student_emails, temperature, max_tokens, include_search, doc_service):
    """
    Create a new agent with the provided information.
    
    Args:
        name: Name of the agent
        personality: Personality/prompt for the agent
        uploaded_files: List of uploaded files
        student_emails: Student email addresses
        temperature: Temperature parameter for response generation
        max_tokens: Maximum tokens for response generation
        include_search: Whether to include web search capability
        doc_service: Document service for processing files
        
    Returns:
        Dict with success status, agent_id if successful, and error message if failed
    """
    try:
        # Get creator ID
        teacher_id = get_user_id()
        
        # Process student emails
        student_list = []
        if student_emails:
            student_list = [email.strip() for email in student_emails.split("\n") if email.strip()]
            
        # Process files
        file_paths = []
        if uploaded_files:
            for file in uploaded_files:
                file_path = doc_service.process_uploaded_file(file)
                file_paths.append(file_path)
        
        # Create advanced settings
        advanced_settings = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "include_search": include_search
        }
        
        # Create the agent
        agent = Agent.create(
            name=name,
            personality=personality,
            created_by=teacher_id,
            students=student_list,
            files=file_paths
        )
        
        # Store advanced settings
        if "agent_settings" not in st.session_state:
            st.session_state.agent_settings = {}
            
        st.session_state.agent_settings[agent.id] = advanced_settings
        
        # Process knowledge base if files were uploaded
        if file_paths:
            doc_service.create_knowledge_base_for_agent(agent.id, file_paths)
        
        return {
            "success": True,
            "agent_id": agent.id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def show_edit_agent_form(agent_id: str):
    """
    Display form for editing an existing agent.
    
    Args:
        agent_id: ID of the agent to edit
    """
    agent = Agent.get_by_id(agent_id)
    
    if not agent:
        st.error(f"No se encontró el agente con ID {agent_id}")
        return
    
    st.subheader(f"Editar Agente: {agent.name}")
    
    with st.form("edit_agent_form"):
        # Campos que realmente existen en el agente
        agent_name = st.text_input("Nombre del Agente", value=agent.name)
        personality = st.text_area("Personalidad / Prompt", value=agent.personality, height=150)
        
        student_emails = "\n".join(agent.students) if agent.students else ""
        student_emails = st.text_area("Correos electrónicos de estudiantes", value=student_emails, height=100)

        submitted = st.form_submit_button("Guardar Cambios")

        if submitted:
            # Actualizamos los atributos existentes
            agent.name = agent_name
            agent.personality = personality
            agent.students = [email.strip() for email in student_emails.split("\n") if email.strip()]
            
            # Actualizamos el agente en session_state; usamos get_by_teacher para actualizar la lista completa
            updated_agents = []
            for a in Agent.get_by_teacher(agent.created_by):
                if a.id == agent.id:
                    updated_agents.append(agent.__dict__)
                else:
                    updated_agents.append(a.__dict__)
            st.session_state.created_agents = updated_agents
            
            st.success(f"¡Agente '{agent.name}' actualizado!")
            st.session_state.editing_agent_id = None
            st.rerun()

    if st.button("Cancelar"):
        st.session_state.editing_agent_id = None
        st.rerun()
