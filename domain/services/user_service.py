from datetime import datetime, timedelta
import uuid
from typing import Optional

from domain.entities.user import User
from domain.repositories.interfaces.user_repository import UserRepositoryInterface

class UserService:
    """Service for user-related operations."""
    
    def __init__(self, user_repository: UserRepositoryInterface):
        """
        Initialize the user service.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def register_user(self, username: str, email: str, password: str) -> User:
        """
        Register a new user.
        
        Args:
            username: The username for the new user
            email: The email for the new user
            password: The plain text password for the new user
            
        Returns:
            The created user
            
        Raises:
            ValueError: If the username or email is already taken
        """
        # Validate inputs
        if not username or not username.strip():
            raise ValueError("Username is required")
        
        if not email or not email.strip():
            raise ValueError("Email is required")
        
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Create the user
        user = self.user_repository.create_user(
            username=username.strip(),
            email=email.strip(),
            password=password
        )
        
        # Generate and set verification token
        self._generate_verification_token(user.id)
        
        return user
    
    def verify_email(self, token: str) -> bool:
        """
        Verify a user's email using a verification token.
        
        Args:
            token: The verification token
            
        Returns:
            True if verification was successful, False otherwise
        """
        user = self.user_repository.get_by_verification_token(token)
        if not user:
            return False
        
        self.user_repository.verify_user(user.id)
        return True
    
    def request_password_reset(self, email: str) -> bool:
        """
        Request a password reset for a user.
        
        Args:
            email: The email of the user
            
        Returns:
            True if the request was successful, False if the user was not found
        """
        user = self.user_repository.get_by_email(email)
        if not user:
            return False
        
        # Generate and set password reset token
        self._generate_password_reset_token(user.id)
        
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset a user's password using a reset token.
        
        Args:
            token: The password reset token
            new_password: The new password
            
        Returns:
            True if the reset was successful, False otherwise
        """
        if not new_password or len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        user = self.user_repository.get_by_password_reset_token(token)
        if not user:
            return False
        
        self.user_repository.update_password(user.id, new_password)
        return True
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id: The ID of the user
            current_password: The current password
            new_password: The new password
            
        Returns:
            True if the change was successful, False otherwise
        """
        if not new_password or len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
        
        # This would require a method to verify the current password
        # For now, we'll assume it's correct
        self.user_repository.update_password(user_id, new_password)
        return True
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The user if found, None otherwise
        """
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: The username to look up
            
        Returns:
            The user if found, None otherwise
        """
        return self.user_repository.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: The email to look up
            
        Returns:
            The user if found, None otherwise
        """
        return self.user_repository.get_by_email(email)
    
    def _generate_verification_token(self, user_id: int) -> str:
        """
        Generate and set a verification token for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The generated token
        """
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=1)  # Token expires in 24 hours
        
        self.user_repository.set_verification_token(user_id, token, expires_at)
        
        return token
    
    def _generate_password_reset_token(self, user_id: int) -> str:
        """
        Generate and set a password reset token for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The generated token
        """
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        
        self.user_repository.set_password_reset_token(user_id, token, expires_at)
        
        return token