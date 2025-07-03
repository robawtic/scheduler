from datetime import datetime
from typing import Optional

class RefreshToken:
    """Entity representing a refresh token."""
    
    def __init__(
        self,
        token_id: str,
        user_id: int,
        expires_at: datetime,
        is_revoked: bool = False,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        """
        Initialize a refresh token.
        
        Args:
            token_id: Unique identifier for the token
            user_id: ID of the user the token belongs to
            expires_at: Expiration datetime
            is_revoked: Whether the token has been revoked
            device_info: Information about the device that requested the token
            ip_address: IP address that requested the token
            created_at: Creation datetime
        """
        self.token_id = token_id
        self.user_id = user_id
        self.expires_at = expires_at
        self.is_revoked = is_revoked
        self.device_info = device_info
        self.ip_address = ip_address
        self.created_at = created_at or datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.utcnow() > self.expires_at
    
    def revoke(self) -> None:
        """Revoke the token."""
        self.is_revoked = True