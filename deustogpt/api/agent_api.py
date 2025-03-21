import requests
import os
import json
from typing import Dict, List, Any, Optional, Union
from uuid import UUID

# Use environment variable for API URL with a default value
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

class AgentAPIException(Exception):
    """Exception raised for agent API errors."""
    pass

def _handle_response(response):
    """Handle API response, return data or raise exception."""
    try:
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        else:
            error_msg = f"Agent API Error: {response.status_code} - {response.text}"
            raise AgentAPIException(error_msg)
    except json.JSONDecodeError:
        if response.status_code >= 200 and response.status_code < 300:
            return {"message": "Success"}
        else:
            raise AgentAPIException(f"Invalid JSON response: {response.text}")

def create_agent(name: str, description: str, created_by: str, 
                 students: List[str] = None, agent_type: str = "custom") -> Dict:
    """Create a new agent via the API."""
    url = f"{API_BASE_URL}/agents/"
    
    payload = {
        "name": name,
        "description": description,
        "created_by": created_by,
        "students": students or [],
        "agent_type": agent_type
    }
    
    response = requests.post(url, json=payload)
    return _handle_response(response)

def get_agents(created_by: Optional[str] = None, 
               skip: int = 0, limit: int = 100) -> List[Dict]:
    """Get all agents, optionally filtered by creator."""
    url = f"{API_BASE_URL}/agents/"
    params = {"skip": skip, "limit": limit}
    if created_by:
        params["created_by"] = created_by
        
    response = requests.get(url, params=params)
    return _handle_response(response)

def get_agent_by_id(agent_id: Union[str, UUID]) -> Dict:
    """Get an agent by ID."""
    url = f"{API_BASE_URL}/agents/{agent_id}"
    response = requests.get(url)
    return _handle_response(response)

def update_agent(agent_id: Union[str, UUID], update_data: Dict) -> Dict:
    """Update an agent."""
    url = f"{API_BASE_URL}/agents/{agent_id}"
    response = requests.put(url, json=update_data)
    return _handle_response(response)

def delete_agent(agent_id: Union[str, UUID]) -> Dict:
    """Delete an agent."""
    url = f"{API_BASE_URL}/agents/{agent_id}"
    response = requests.delete(url)
    return _handle_response(response)

def subscribe_student(agent_id: Union[str, UUID], student_email: str) -> Dict:
    """Subscribe a student to an agent."""
    url = f"{API_BASE_URL}/agents/{agent_id}/subscribe"
    payload = {"student_email": student_email}
    response = requests.post(url, json=payload)
    return _handle_response(response)

def unsubscribe_student(agent_id: Union[str, UUID], student_email: str) -> Dict:
    """Unsubscribe a student from an agent."""
    url = f"{API_BASE_URL}/agents/{agent_id}/unsubscribe"
    payload = {"student_email": student_email}
    response = requests.delete(url, json=payload)
    return _handle_response(response)

def get_agents_by_student(student_email: str, 
                          skip: int = 0, limit: int = 100) -> List[Dict]:
    """Get all agents a student is subscribed to."""
    url = f"{API_BASE_URL}/agents/by-student/{student_email}"
    params = {"skip": skip, "limit": limit}
    response = requests.get(url, params=params)
    return _handle_response(response)

def get_agent_config(agent_id: Union[str, UUID]) -> Dict[str, str]:
    """Get agent configuration as a dictionary."""
    url = f"{API_BASE_URL}/agents/{agent_id}/config/dict"
    response = requests.get(url)
    return _handle_response(response)

def set_agent_config(agent_id: Union[str, UUID], parameter: str, value: str) -> Dict:
    """Create or update agent configuration parameter."""
    url = f"{API_BASE_URL}/agents/{agent_id}/config/{parameter}"
    params = {"value": value}
    response = requests.patch(url, params=params)
    return _handle_response(response)