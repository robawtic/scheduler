from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from domain.entities.user import User

class UserRepositoryInterface(ABC):
    """Interface for user repository."""
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The ID of the user to get
            
        Returns:
            The user if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: The username to look up
            
        Returns:
            The user if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: The email to look up
            
        Returns:
            The user if found, None otherwise
        """
        pass
    
    @abstractmethod
    def create_user(self, username: str, email: str, password: str) -> User:
        """
        Create a new user.
        
        Args:
            username: The username for the new user
            email: The email for the new user
            password: The plain text password for the new user
            
        Returns:
            The created user
            
        Raises:
            ValueError: If the username or email is already taken
        """
        pass
    
    @abstractmethod
    def verify_user(self, user_id: int) -> None:
        """
        Mark a user as verified.
        
        Args:
            user_id: The ID of the user to verify
        """
        pass
    
    @abstractmethod
    def update_password(self, user_id: int, password: str) -> None:
        """
        Update a user's password.
        
        Args:
            user_id: The ID of the user
            password: The new plain text password
        """
        pass
    
    @abstractmethod
    def set_verification_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        """
        Set a verification token for a user.
        
        Args:
            user_id: The ID of the user
            token: The verification token
            expires_at: When the token expires
        """
        pass
    
    @abstractmethod
    def set_password_reset_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        """
        Set a password reset token for a user.
        
        Args:
            user_id: The ID of the user
            token: The password reset token
            expires_at: When the token expires
        """
        pass
    
    @abstractmethod
    def get_by_verification_token(self, token: str) -> Optional[User]:
        """
        Get a user by verification token.
        
        Args:
            token: The verification token
            
        Returns:
            The user if found and token is valid, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_password_reset_token(self, token: str) -> Optional[User]:
        """
        Get a user by password reset token.
        
        Args:
            token: The password reset token
            
        Returns:
            The user if found and token is valid, None otherwise
        """
        pass