"""
Message model for chat interactions between users and AI agents.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, ClassVar


@dataclass
class Message:
    """
    Represents a single message in a chat conversation.
    
    Attributes:
        content: The text content of the message
        role: The sender of the message ('user' or 'assistant')
        timestamp: When the message was created
        agent_id: ID of the agent this message is associated with
        user_id: ID of the user this message is associated with
        metadata: Additional data associated with the message
    """
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Class constants for role types
    ROLE_USER: ClassVar[str] = "user"
    ROLE_ASSISTANT: ClassVar[str] = "assistant"
    ROLE_SYSTEM: ClassVar[str] = "system"
    
    @classmethod
    def user_message(cls, content: str, user_id: str, agent_id: str) -> 'Message':
        """
        Create a message from the user.
        
        Args:
            content: Message content
            user_id: ID of the user sending the message
            agent_id: ID of the agent receiving the message
            
        Returns:
            A new Message instance with the user role
        """
        return cls(
            content=content,
            role=cls.ROLE_USER,
            user_id=user_id,
            agent_id=agent_id
        )
    
    @classmethod
    def assistant_message(cls, content: str, agent_id: str, user_id: Optional[str] = None) -> 'Message':
        """
        Create a message from the AI assistant.
        
        Args:
            content: Message content
            agent_id: ID of the agent sending the message
            user_id: Optional ID of the user receiving the message
            
        Returns:
            A new Message instance with the assistant role
        """
        return cls(
            content=content,
            role=cls.ROLE_ASSISTANT,
            agent_id=agent_id,
            user_id=user_id
        )
    
    @classmethod
    def system_message(cls, content: str, agent_id: Optional[str] = None) -> 'Message':
        """
        Create a system message (instructions, etc).
        
        Args:
            content: Message content
            agent_id: Optional ID of the agent this message is for
            
        Returns:
            A new Message instance with the system role
        """
        return cls(
            content=content,
            role=cls.ROLE_SYSTEM,
            agent_id=agent_id
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the message
        """
        return {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a message from a dictionary.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            A new Message instance
        """
        # Handle timestamp conversion if it's a string
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        else:
            timestamp = data.get("timestamp", datetime.now())
            
        return cls(
            content=data["content"],
            role=data["role"],
            timestamp=timestamp,
            agent_id=data.get("agent_id"),
            user_id=data.get("user_id"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def get_conversation_history(cls, messages: List['Message']) -> str:
        """
        Format a list of messages into a conversation history string.
        
        Args:
            messages: List of Message objects
            
        Returns:
            Formatted conversation history string
        """
        history = ""
        for msg in messages:
            if msg.role == cls.ROLE_USER:
                history += f"Human: {msg.content}\n"
            elif msg.role == cls.ROLE_ASSISTANT:
                history += f"AI: {msg.content}\n"
        return history