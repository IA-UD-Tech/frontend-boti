"""
Model representing a chat agent in the system.
"""

import json
from datetime import datetime
import random
import streamlit as st

class Agent:
    def __init__(self, id=None, name=None, personality=None, created_by=None, 
                 students=None, files=None, created_at=None):
        self.id = id or str(random.randint(1000, 9999))
        self.name = name
        self.personality = personality
        self.created_by = created_by
        self.created_at = created_at or datetime.now().isoformat()
        self.students = students or []
        self.files = files or []

    @classmethod
    def create(cls, name, personality, created_by, students=None, files=None):
        """Create a new agent and save it to session state."""
        agent = cls(
            name=name,
            personality=personality,
            created_by=created_by,
            students=students or [],
            files=files or [],
            created_at=datetime.now().isoformat()
        )
        
        # Save to session state
        if "created_agents" not in st.session_state:
            st.session_state.created_agents = []
        
        st.session_state.created_agents.append(agent.__dict__)
        return agent

    @classmethod
    def get_by_id(cls, agent_id):
        """Get an agent by its ID from session state."""
        if "created_agents" not in st.session_state:
            return None
            
        for agent_data in st.session_state.created_agents:
            if str(agent_data["id"]) == str(agent_id):
                return cls(**agent_data)
        return None

    @classmethod
    def get_by_teacher(cls, teacher_id):
        """Get all agents created by a specific teacher."""
        if "created_agents" not in st.session_state:
            return []
            
        return [cls(**agent_data) for agent_data in st.session_state.created_agents 
                if agent_data["created_by"] == teacher_id]

    @classmethod
    def get_by_student(cls, student_email):
        """Get all agents a student has access to."""
        if "created_agents" not in st.session_state:
            return []
            
        return [cls(**agent_data) for agent_data in st.session_state.created_agents 
                if student_email in agent_data["students"]]