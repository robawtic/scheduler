from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.refresh_token import RefreshToken

class RefreshTokenRepositoryInterface(ABC):
    """Interface for refresh token repository."""
    
    @abstractmethod
    def add(self, refresh_token: RefreshToken) -> None:
        """
        Add a refresh token to the repository.
        
        Args:
            refresh_token: The refresh token to add
        """
        pass
    
    @abstractmethod
    def get_by_token_id(self, token_id: str) -> Optional[RefreshToken]:
        """
        Get a refresh token by its ID.
        
        Args:
            token_id: The ID of the token to get
            
        Returns:
            The refresh token if found, None otherwise
        """
        pass
    
    @abstractmethod
    def revoke(self, token_id: str) -> None:
        """
        Revoke a refresh token.
        
        Args:
            token_id: The ID of the token to revoke
        """
        pass
    
    @abstractmethod
    def revoke_all_for_user(self, user_id: int) -> None:
        """
        Revoke all refresh tokens for a user.
        
        Args:
            user_id: The ID of the user
        """
        pass
    
    @abstractmethod
    def delete_expired(self) -> int:
        """
        Delete all expired refresh tokens.
        
        Returns:
            The number of tokens deleted
        """
        pass