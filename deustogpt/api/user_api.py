"""
User API client for interacting with backend user endpoints.
"""
import os
import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

# Get backend URL from environment or use default
BACKEND_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000")

def get_api_url(endpoint: str) -> str:
    """Construct full API URL from endpoint path."""
    return urljoin(BACKEND_URL, f"/api/v1{endpoint}")

def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Find a user by email.
    
    Args:
        email: User's email address
        
    Returns:
        User data if found, None otherwise
    """
    try:
        response = requests.get(get_api_url("/users/"))
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user.get("email") == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error finding user: {str(e)}")
        return None

def create_user(email: str, name: str, avatar_url: str = None, status: bool = True) -> Optional[Dict[str, Any]]:
    """
    Create a new user.
    
    Args:
        email: User's email address
        name: User's name
        avatar_url: URL to user's avatar/profile picture
        status: User status (active/inactive)
        
    Returns:
        Created user data if successful, None otherwise
    """
    try:
        user_data = {
            "email": email,
            "name": name,
            "status": status
        }
        if avatar_url:
            user_data["avatar_url"] = avatar_url
            
        response = requests.post(
            get_api_url("/users/"),
            json=user_data
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error creating user: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return None

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID.
    
    Args:
        user_id: User's unique ID
        
    Returns:
        User data if found, None otherwise
    """
    try:
        response = requests.get(get_api_url(f"/users/{user_id}"))
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error getting user: {str(e)}")
        return None

def get_all_users() -> List[Dict[str, Any]]:
    """
    Get all users.
    
    Returns:
        List of all users
    """
    try:
        response = requests.get(get_api_url("/users/"))
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error getting users: {str(e)}")
        return []