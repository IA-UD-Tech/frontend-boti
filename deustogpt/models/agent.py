"""
Model representing a chat agent in the system.
"""

import json
from datetime import datetime
import uuid
import random
import os
import streamlit as st
from typing import Any, Dict, List, Optional

from deustogpt.api.agent_api import (
    create_agent as api_create_agent,
    get_agents as api_get_agents,
    get_agent_by_id as api_get_agent_by_id,
    update_agent as api_update_agent,
    delete_agent as api_delete_agent,
    subscribe_student as api_subscribe_student,
    unsubscribe_student as api_unsubscribe_student,
    get_agents_by_student as api_get_agents_by_student
)

class Agent:
    def __init__(self, id=None, name=None, description=None, personality=None, 
                 created_by=None, students=None, files=None, created_at=None, 
                 agent_type=None, **kwargs):
        # Handle mapping between backend and frontend field names
        self.id = id or str(uuid.uuid4())
        self.name = name
        # Handle difference between description in API and personality in frontend
        self.personality = personality or description
        self.description = description or personality
        self.created_by = created_by
        self.created_at = created_at or datetime.now().isoformat()
        self.students = students or []
        self.files = files or []
        self.agent_type = agent_type or "custom"

    @classmethod
    def create(cls, name, personality, created_by, students=None, files=None):
        """Create a new agent using the API."""
        try:
            agent_data = api_create_agent(
                name=name,
                description=personality,  # Map personality to description for API
                created_by=created_by,
                students=students or []
            )
            
            agent = cls(
                id=agent_data.get("id"),
                name=agent_data.get("name"),
                description=agent_data.get("description"),
                created_by=agent_data.get("created_by"),
                students=agent_data.get("students", []),
                files=files or [],
                created_at=agent_data.get("created_at"),
                agent_type=agent_data.get("agent_type")
            )
            
            # Store in session state as fallback
            if "created_agents" not in st.session_state:
                st.session_state.created_agents = []
            
            st.session_state.created_agents.append(agent.__dict__)
            return agent
            
        except Exception as e:
            st.error(f"Error creating agent via API: {str(e)}")
            # Fallback: Create locally if API fails
            agent = cls(
                name=name,
                personality=personality,
                created_by=created_by,
                students=students or [],
                files=files or []
            )
            
            if "created_agents" not in st.session_state:
                st.session_state.created_agents = []
            
            st.session_state.created_agents.append(agent.__dict__)
            return agent

    @classmethod
    def get_by_id(cls, agent_id):
        """Get an agent by ID using the API."""
        try:
            agent_data = api_get_agent_by_id(agent_id)
            return cls(
                id=agent_data.get("id"),
                name=agent_data.get("name"),
                description=agent_data.get("description"),
                created_by=agent_data.get("created_by"),
                students=agent_data.get("students", []),
                agent_type=agent_data.get("agent_type"),
                created_at=agent_data.get("created_at")
            )
        except Exception as e:
            st.warning(f"Failed to get agent from API: {str(e)}")
            # Fallback to session state
            if "created_agents" in st.session_state:
                for agent_data in st.session_state.created_agents:
                    if str(agent_data.get("id")) == str(agent_id):
                        return cls(**agent_data)
            return None

    @classmethod
    def get_by_teacher(cls, teacher_id):
        """Get all agents created by a teacher using the API."""
        try:
            agents_data = api_get_agents(created_by=teacher_id)
            return [cls(
                id=agent_data.get("id"),
                name=agent_data.get("name"),
                description=agent_data.get("description"),
                created_by=agent_data.get("created_by"),
                students=agent_data.get("students", []),
                agent_type=agent_data.get("agent_type"),
                created_at=agent_data.get("created_at")
            ) for agent_data in agents_data]
        except Exception as e:
            st.warning(f"Failed to get teacher's agents from API: {str(e)}")
            # Fallback to session state
            if "created_agents" in st.session_state:
                return [cls(**agent_data) for agent_data in st.session_state.created_agents
                        if str(agent_data.get("created_by")) == str(teacher_id)]
            return []

    @classmethod
    def get_by_student(cls, student_email):
        """Get all agents a student is subscribed to using the API."""
        try:
            print(f"Fetching agents for student: {student_email}")
            agents_data = api_get_agents_by_student(student_email)

            # Create Agent objects from the API response
            agents = [cls(
                id=agent_data.get("id"),
                name=agent_data.get("name"),
                description=agent_data.get("description"),
                created_by=agent_data.get("created_by"),
                students=agent_data.get("students", []),
                agent_type=agent_data.get("agent_type"),
                created_at=agent_data.get("created_at")
            ) for agent_data in agents_data]

            print(f"Found {len(agents)} agents for student {student_email}")
            return agents

        except Exception as e:
            st.warning(f"Failed to get student's agents from API: {str(e)}")
            print(f"API error details: {type(e).__name__}: {str(e)}")

            # Fallback to session state
            if "created_agents" in st.session_state:
                fallback_agents = [cls(**agent_data) for agent_data in st.session_state.created_agents
                        if student_email in agent_data.get("students", [])]
                print(f"Using fallback: found {len(fallback_agents)} agents in session state")
                return fallback_agents

            # If all else fails, generate some sample data in development
            if os.getenv("ENVIRONMENT") == "development":
                from deustogpt.utils.data_generator import generate_sample_agents
                print("Generating sample agent data for development")
                sample_data = generate_sample_agents(3)
                sample_agents = [cls(**agent) for agent in sample_data]
                return sample_agents

            return []

    def update(self, **kwargs):
        """Update agent attributes using the API."""
        try:
            # Handle mapping between frontend and backend fields
            update_data = kwargs.copy()
            if "personality" in update_data and "description" not in update_data:
                update_data["description"] = update_data.pop("personality")
                
            updated_data = api_update_agent(self.id, update_data)
            
            # Update self with new data
            for key, value in updated_data.items():
                if key == "description":
                    self.personality = value
                setattr(self, key, value)
                
            # Update session state
            if "created_agents" in st.session_state:
                for i, agent_data in enumerate(st.session_state.created_agents):
                    if str(agent_data.get("id")) == str(self.id):
                        st.session_state.created_agents[i] = self.__dict__
                        break
                        
            return True
        except Exception as e:
            st.error(f"Failed to update agent via API: {str(e)}")
            return False

    def delete(self):
        """Delete the agent using the API."""
        try:
            api_delete_agent(self.id)
            
            # Remove from session state
            if "created_agents" in st.session_state:
                st.session_state.created_agents = [
                    agent for agent in st.session_state.created_agents 
                    if str(agent.get("id")) != str(self.id)
                ]
            return True
        except Exception as e:
            st.error(f"Failed to delete agent via API: {str(e)}")
            return False

    def subscribe_student(self, student_email):
        """Subscribe a student to this agent using the API."""
        try:
            updated_data = api_subscribe_student(self.id, student_email)
            
            # Update students list
            self.students = updated_data.get("students", [])
            
            # Update session state
            if "created_agents" in st.session_state:
                for i, agent_data in enumerate(st.session_state.created_agents):
                    if str(agent_data.get("id")) == str(self.id):
                        agent_data["students"] = self.students
                        break
                        
            return True
        except Exception as e:
            st.error(f"Failed to subscribe student via API: {str(e)}")
            return False

    def unsubscribe_student(self, student_email):
        """Unsubscribe a student from this agent using the API."""
        try:
            updated_data = api_unsubscribe_student(self.id, student_email)
            
            # Update students list
            self.students = updated_data.get("students", [])
            
            # Update session state
            if "created_agents" in st.session_state:
                for i, agent_data in enumerate(st.session_state.created_agents):
                    if str(agent_data.get("id")) == str(self.id):
                        agent_data["students"] = self.students
                        break
                        
            return True
        except Exception as e:
            st.error(f"Failed to unsubscribe student via API: {str(e)}")
            return False