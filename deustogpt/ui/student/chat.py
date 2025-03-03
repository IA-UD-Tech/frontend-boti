"""
Chat interface module for student-agent interactions.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import time

from deustogpt.models.agent import Agent
from deustogpt.models.message import Message
from deustogpt.services.llm_service import LLMService
from deustogpt.services.document_service import DocumentService
from deustogpt.auth.google_auth import get_user_id


def show_chat_interface(agent_id: str):
    """
    Display the chat interface for interacting with an AI agent.
    
    Args:
        agent_id: ID of the agent to chat with
    """
    # Get agent information
    agent = Agent.get_by_id(agent_id)
    
    if not agent:
        st.error(f"No se encontró el agente con ID {agent_id}")
        if st.button("← Volver al panel"):
            st.session_state.current_agent_id = None
            st.session_state.messages = []
            st.rerun()
        return
    
    # Setup header with back button
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("←", help="Volver al panel"):
            st.session_state.current_agent_id = None
            st.session_state.messages = []
            st.rerun()
    with col2:
        st.header(f"Chat con {agent.name}")
    
    # Initialize message history if needed
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add a welcome message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"¡Hola! Soy el asistente de {agent.name}. ¿En qué puedo ayudarte hoy?"
        })
    
    # Initialize LLM service if needed
    if "llm_service" not in st.session_state:
        st.session_state.llm_service = LLMService(personality=agent.personality)
    
    # Initialize document service
    doc_service = DocumentService()
    
    # Display chat messages
    display_chat_messages()
    
    # Get and process user input
    process_user_input(agent, st.session_state.llm_service, doc_service)


def display_chat_messages():
    """Display all messages in the chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show document references if present
            if "references" in message and message["references"]:
                with st.expander("Referencias"):
                    for i, ref in enumerate(message["references"]):
                        st.markdown(f"**Fuente {i+1}:**")
                        st.write(ref["content"][:200] + "..." if len(ref["content"]) > 200 else ref["content"])
                        if "metadata" in ref and ref["metadata"]:
                            source = ref["metadata"].get("source", "Documento")
                            st.caption(f"De: {source}")


def process_user_input(agent: Agent, llm_service: LLMService, doc_service: DocumentService):
    """
    Process user input and generate AI responses.
    
    Args:
        agent: The agent to interact with
        llm_service: Service for generating AI responses
        doc_service: Service for document retrieval
    """
    # Get user ID
    user_id = get_user_id()
    
    # Chat input
    user_input = st.chat_input("Escribe tu mensaje aquí...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display the message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate AI response
        with st.chat_message("assistant"):
            # Show typing indicator
            message_placeholder = st.empty()
            message_placeholder.markdown("⏳ Pensando...")
            
            # Retrieve relevant documents if available
            references = []
            try:
                results = doc_service.similarity_search(agent.id, user_input)
                if results:
                    references = results
            except Exception as e:
                st.session_state.debug = f"Error retrieving documents: {str(e)}"
            
            # Generate response
            if references:
                # Add context from documents to improve response
                context = "\n\n".join([f"Información relevante: {ref['content']}" for ref in references[:2]])
                enhanced_prompt = f"{context}\n\nPregunta del usuario: {user_input}\n\nResponde utilizando la información provista si es relevante."
                response = llm_service.generate_response(enhanced_prompt)
            else:
                # Standard response without document context
                response = llm_service.generate_response(user_input)
            
            # Simulate typing effect
            full_response = response
            for i in range(min(len(full_response) // 3, 3)):
                chunk = full_response[:len(full_response) * (i+1) // 3]
                message_placeholder.markdown(chunk + "▌")
                time.sleep(0.05)
            
            # Display final response
            message_placeholder.markdown(full_response)
            
            # Show references if available
            if references:
                with st.expander("Fuentes de información"):
                    for i, ref in enumerate(references):
                        st.markdown(f"**Fuente {i+1}:**")
                        st.write(ref["content"][:200] + "..." if len(ref["content"]) > 200 else ref["content"])
                        if "metadata" in ref:
                            source = ref["metadata"].get("source", "Documento")
                            st.caption(f"De: {source}")
        
        # Add AI response to chat history
        ai_message = {
            "role": "assistant",
            "content": response
        }
        
        # Include references if available
        if references:
            ai_message["references"] = references
            
        st.session_state.messages.append(ai_message)


def clear_chat_history():
    """Clear the chat history."""
    st.session_state.messages = []
    # Add a welcome message
    current_agent_id = st.session_state.current_agent_id
    agent = Agent.get_by_id(current_agent_id)
    if agent:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"¡Hola! Soy el asistente de {agent.name}. ¿En qué puedo ayudarte hoy?"
        })
    st.rerun()


def log_chat_message(agent_id: str, user_id: str, role: str, content: str):
    """
    Log a chat message to session state.
    
    Args:
        agent_id: ID of the agent
        user_id: ID of the user
        role: Message role ('user' or 'assistant')
        content: Message content
    """
    if "chat_logs" not in st.session_state:
        st.session_state.chat_logs = []
        
    # Create message object
    message = Message(
        content=content,
        role=role,
        agent_id=agent_id,
        user_id=user_id
    )
    
    # Add to logs
    st.session_state.chat_logs.append(message.to_dict())