"""
User model representing teachers and students in the DeustoGPT system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List, ClassVar


class UserRole(Enum):
    """Enumeration of possible user roles."""
    TEACHER = "teacher"
    STUDENT = "student"


@dataclass
class User:
    """
    Represents a user of the DeustoGPT system.
    
    Attributes:
        id: Unique identifier for the user
        email: User's email address
        role: Role of the user (teacher or student)
        name: User's full name
        profile_picture: URL to user's profile picture
        metadata: Additional data associated with the user
    """
    id: str
    email: str
    role: UserRole
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_google_info(cls, user_info: Dict[str, Any]) -> 'User':
        """
        Create a User instance from Google OAuth user information.
        
        Args:
            user_info: User information obtained from Google OAuth
            
        Returns:
            A new User instance
            
        Raises:
            ValueError: If the email domain is not authorized
        """
        email = user_info.get("email")
        if not email:
            raise ValueError("Email is required")
            
        # Determine role based on email domain
        if email.endswith("@deusto.es"):
            role = UserRole.TEACHER
        elif email.endswith("@opendeusto.es"):
            role = UserRole.STUDENT
        else:
            raise ValueError(f"Unauthorized email domain: {email}")
            
        return cls(
            id=user_info.get("sub") or email,
            email=email,
            role=role,
            name=user_info.get("name"),
            profile_picture=user_info.get("picture")
        )
    
    def is_teacher(self) -> bool:
        """Check if the user is a teacher."""
        return self.role == UserRole.TEACHER
    
    def is_student(self) -> bool:
        """Check if the user is a student."""
        return self.role == UserRole.STUDENT
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the user to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role.value,
            "name": self.name,
            "profile_picture": self.profile_picture,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a user from a dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            A new User instance
        """
        role_value = data.get("role")
        role = UserRole.TEACHER if role_value == "teacher" else UserRole.STUDENT
        
        return cls(
            id=data["id"],
            email=data["email"],
            role=role,
            name=data.get("name"),
            profile_picture=data.get("profile_picture"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def get_session_user(cls) -> Optional['User']:
        """
        Get the currently logged in user from the session state.
        
        Returns:
            User instance if logged in, None otherwise
        """
        import streamlit as st
        
        if not (st.session_state.get("user_email") and st.session_state.get("user_role")):
            return None
            
        return cls(
            id=st.session_state.get("user_id", st.session_state.user_email),
            email=st.session_state.user_email,
            role=UserRole.TEACHER if st.session_state.user_role == "teacher" else UserRole.STUDENT
        )