import requests
import os
import json
from typing import Dict, List, Any, Optional, Union
from uuid import UUID

# Use environment variable for API URL with a default value
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

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

def create_user(email: str, password: str, full_name: str, role: str) -> Dict:
    """
    Create a new user.
    """
    url = f"{API_BASE_URL}/users/"
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role
    }
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
    url = f"{API_BASE_URL}/users/by-email/{email}"
    try:
        response = requests.get(url)
        if response.status_code == 404:
            # User not found
            return None
        return _handle_response(response)
    except UserAPIException:
        # Try alternative approach by getting all users and filtering
        # This is a fallback if the direct endpoint doesn't exist
        try:
            all_users = get_users(limit=1000)  # Assuming there aren't too many users
            for user in all_users:
                if user.get("email") == email:
                    return user
            return None
        except Exception:
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