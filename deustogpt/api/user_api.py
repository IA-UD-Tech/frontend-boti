import requests
import os
import json
from typing import Dict, List, Any, Optional, Union
from uuid import UUID

API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")
if not API_BASE_URL.endswith("/api/v1"):
    API_BASE_URL = API_BASE_URL.rstrip("/") + "/api/v1"

class UserAPIException(Exception):
    """Exception raised for user API errors."""
    pass

def _handle_response(response):
    """Handle API response, return data or raise exception."""
    try:
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        else:
            error_msg = f"User API Error: {response.status_code} - {response.text}"
            raise UserAPIException(error_msg)
    except json.JSONDecodeError:
        if response.status_code >= 200 and response.status_code < 300:
            return {"message": "Success"}
        else:
            raise UserAPIException(f"Invalid JSON response: {response.text}")

def login(email: str, password: str) -> Dict:
    """
    Authenticate a user and get access token.
    """
    url = f"{API_BASE_URL}/auth/login"
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(url, data=payload)
    return _handle_response(response)

def get_current_user(token: str) -> Dict:
    """
    Get currently logged-in user information.
    """
    url = f"{API_BASE_URL}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return _handle_response(response)

def create_user(email: str, password: str, full_name: str, role: str, avatar_url: Optional[str] = None) -> Dict:
    """
    Create a new user.
    """
    url = f"{API_BASE_URL}/users/"
    payload = {
        "email": email,
        "name": full_name,  # Changed from "full_name" to "name" to match backend schema
        "role": role
    }
    
    # Add avatar_url to payload if provided
    if avatar_url:
        payload["avatar_url"] = avatar_url
        
    # Add password if provided and not empty
    if password:
        payload["password"] = password
        
    response = requests.post(url, json=payload)
    return _handle_response(response)

def get_user(user_id: Union[str, UUID]) -> Dict:
    """
    Get a user by ID - alias for get_user_by_id for backward compatibility.
    
    Args:
        user_id: ID of the user to fetch
        
    Returns:
        User data or None if not found
    """
    # This is just an alias for get_user_by_id to maintain compatibility
    return get_user_by_id(user_id)

def find_user_by_email(email: str) -> Optional[Dict]:
    """
    Find a user by their email address.
    
    Args:
        email: Email address to search for
        
    Returns:
        User data dictionary or None if not found
    """
    # First, try the specific endpoint if available
    try:
        url = f"{API_BASE_URL}/users/by-email"
        params = {"email": email}
        response = requests.get(url, params=params)
        
        # If successful, return the user data
        if response.status_code == 200:
            return response.json()
            
        # If not found specifically (404), proceed with fallback
    except Exception as e:
        print(f"Error in direct user lookup: {str(e)}")
    
    # Fallback: Check if the user exists by calling users/ endpoint
    try:
        url = f"{API_BASE_URL}/users/"
        response = requests.get(url)
        
        if response.status_code == 200:
            users = response.json()
            # Find user with matching email
            for user in users:
                if user.get("email") == email:
                    return user
    except Exception as e:
        print(f"Error in fallback user lookup: {str(e)}")
    
    # If we get here, the user truly doesn't exist
    return None

def get_users(skip: int = 0, limit: int = 100) -> List[Dict]:
    """
    Get list of users.
    """
    url = f"{API_BASE_URL}/users/"
    params = {"skip": skip, "limit": limit}
    response = requests.get(url, params=params)
    return _handle_response(response)

def get_user_by_id(user_id: Union[str, UUID]) -> Dict:
    """
    Get a specific user by ID.
    """
    url = f"{API_BASE_URL}/users/{user_id}"
    response = requests.get(url)
    return _handle_response(response)

def update_user(user_id: Union[str, UUID], update_data: Dict) -> Dict:
    """
    Update user information.
    """
    url = f"{API_BASE_URL}/users/{user_id}"
    response = requests.put(url, json=update_data)
    return _handle_response(response)

def delete_user(user_id: Union[str, UUID]) -> Dict:
    """
    Delete a user.
    """
    url = f"{API_BASE_URL}/users/{user_id}"
    response = requests.delete(url)
    return _handle_response(response)

def get_students() -> List[Dict]:
    """
    Get all users with student role.
    """
    url = f"{API_BASE_URL}/users/students"
    response = requests.get(url)
    return _handle_response(response)

def get_teachers() -> List[Dict]:
    """
    Get all users with teacher role.
    """
    url = f"{API_BASE_URL}/users/teachers"
    response = requests.get(url)
    return _handle_response(response)

def reset_password(email: str) -> Dict:
    """
    Request password reset for a user.
    """
    url = f"{API_BASE_URL}/auth/password-reset"
    payload = {"email": email}
    response = requests.post(url, json=payload)
    return _handle_response(response)

def confirm_password_reset(token: str, new_password: str) -> Dict:
    """
    Confirm password reset with token.
    """
    url = f"{API_BASE_URL}/auth/reset-password"
    payload = {
        "token": token,
        "new_password": new_password
    }
    response = requests.post(url, json=payload)
    return _handle_response(response)