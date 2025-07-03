from datetime import datetime
from typing import Optional, List
import json

class ApiKey:
    """Entity representing an API key."""
    
    def __init__(
        self,
        key_id: str,
        key_value: str,
        user_id: int,
        name: str,
        expires_at: Optional[datetime] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_used_at: Optional[datetime] = None,
        scopes: Optional[List[str]] = None,
        allowed_ips: Optional[List[str]] = None,
        allowed_user_agents: Optional[List[str]] = None,
    ):
        """
        Initialize an API key.
        
        Args:
            key_id: Unique identifier for the API key
            key_value: The actual API key value
            user_id: ID of the user the API key belongs to
            name: A name for the API key (e.g., "Mobile App")
            expires_at: Expiration datetime
            is_active: Whether the API key is active
            created_at: Creation datetime
            updated_at: Last update datetime
            last_used_at: Last usage datetime
            scopes: List of permission scopes for this API key
            allowed_ips: List of IP addresses allowed to use this key
            allowed_user_agents: List of user agents allowed to use this key
        """
        self.key_id = key_id
        self.key_value = key_value
        self.user_id = user_id
        self.name = name
        self.expires_at = expires_at
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_used_at = last_used_at
        self.scopes = scopes or []
        self.allowed_ips = allowed_ips or []
        self.allowed_user_agents = allowed_user_agents or []
    
    def is_expired(self) -> bool:
        """Check if the API key is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def deactivate(self) -> None:
        """Deactivate the API key."""
        self.is_active = False
    
    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def update_last_used(self) -> None:
        """Update the last used timestamp to now."""
        self.last_used_at = datetime.utcnow()