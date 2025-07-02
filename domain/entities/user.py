from datetime import datetime
from typing import List, Optional

class User:
    """Entity representing a user."""
    
    def __init__(
        self,
        id: Optional[int] = None,
        username: str = "",
        email: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login_at: Optional[datetime] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_verified: bool = False,
        last_login_ip: Optional[str] = None,
        verification_token: Optional[str] = None,
        verification_token_expires_at: Optional[datetime] = None,
        password_reset_token: Optional[str] = None,
        password_reset_token_expires_at: Optional[datetime] = None,
    ):
        """
        Initialize a user.
        
        Args:
            id: User ID
            username: Username
            email: Email address
            is_active: Whether the user is active
            created_at: Creation datetime
            updated_at: Last update datetime
            last_login_at: Last login datetime
            first_name: First name
            last_name: Last name
            is_verified: Whether the user is verified
            last_login_ip: Last login IP address
            verification_token: Token for email verification
            verification_token_expires_at: Expiration datetime for verification token
            password_reset_token: Token for password reset
            password_reset_token_expires_at: Expiration datetime for password reset token
        """
        self.id = id
        self.username = username
        self.email = email
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_login_at = last_login_at
        self.first_name = first_name
        self.last_name = last_name
        self.is_verified = is_verified
        self.last_login_ip = last_login_ip
        self.verification_token = verification_token
        self.verification_token_expires_at = verification_token_expires_at
        self.password_reset_token = password_reset_token
        self.password_reset_token_expires_at = password_reset_token_expires_at
        
        # Private attributes
        self._password_hash = None
        self._roles = []
        self._api_keys = []
        self._refresh_tokens = []
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""
    
    @property
    def roles(self) -> List:
        """Get the user's roles."""
        return self._roles
    
    @property
    def api_keys(self) -> List:
        """Get the user's API keys."""
        return self._api_keys
    
    @property
    def refresh_tokens(self) -> List:
        """Get the user's refresh tokens."""
        return self._refresh_tokens
    
    def add_role(self, role) -> None:
        """Add a role to the user."""
        if role not in self._roles:
            self._roles.append(role)
    
    def remove_role(self, role) -> None:
        """Remove a role from the user."""
        if role in self._roles:
            self._roles.remove(role)
    
    def add_api_key(self, api_key) -> None:
        """Add an API key to the user."""
        if api_key not in self._api_keys:
            self._api_keys.append(api_key)
    
    def remove_api_key(self, api_key) -> None:
        """Remove an API key from the user."""
        if api_key in self._api_keys:
            self._api_keys.remove(api_key)
    
    def add_refresh_token(self, refresh_token) -> None:
        """Add a refresh token to the user."""
        if refresh_token not in self._refresh_tokens:
            self._refresh_tokens.append(refresh_token)
    
    def remove_refresh_token(self, refresh_token) -> None:
        """Remove a refresh token from the user."""
        if refresh_token in self._refresh_tokens:
            self._refresh_tokens.remove(refresh_token)