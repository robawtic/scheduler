from datetime import datetime
from typing import Optional
import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from domain.entities.user import User
from infrastructure.models.UserModel import UserModel
from domain.repositories.interfaces.user_repository import UserRepositoryInterface
from infrastructure.exceptions import RepositoryError

# Module-level function for password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password

    Returns:
        True if the password matches, False otherwise
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

class SQLAlchemyUserRepository(UserRepositoryInterface):
    """SQLAlchemy implementation of UserRepositoryInterface."""

    def __init__(self, db: Session):
        """
        Initialize the repository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: The ID of the user to get

        Returns:
            The user if found, None otherwise
        """
        try:
            user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if user_model:
                return user_model.to_domain()
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to get user by ID: {str(e)}")

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: The username to look up

        Returns:
            The user if found, None otherwise
        """
        try:
            user_model = self.db.query(UserModel).filter(UserModel.username == username).first()
            if user_model:
                return user_model.to_domain()
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to get user by username: {str(e)}")

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: The email to look up

        Returns:
            The user if found, None otherwise
        """
        try:
            user_model = self.db.query(UserModel).filter(UserModel.email == email).first()
            if user_model:
                return user_model.to_domain()
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to get user by email: {str(e)}")

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
        try:
            # Check if username already exists
            if self.get_by_username(username):
                raise ValueError(f"Username '{username}' is already taken")

            # Check if email already exists
            if email and self.get_by_email(email):
                raise ValueError(f"Email '{email}' is already registered")

            # Hash the password
            password_hash = self._hash_password(password)

            # Create the user model
            user_model = UserModel(
                username=username,
                email=email,
                password_hash=password_hash,
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Add to database
            self.db.add(user_model)
            self.db.commit()
            self.db.refresh(user_model)

            return user_model.to_domain()
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Username '{username}' or email '{email}' is already taken")
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to create user: {str(e)}")

    def verify_user(self, user_id: int) -> None:
        """
        Mark a user as verified.

        Args:
            user_id: The ID of the user to verify
        """
        try:
            user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user_model:
                raise ValueError(f"User with ID {user_id} not found")

            user_model.is_verified = True
            user_model.verification_token = None
            user_model.verification_token_expires_at = None
            user_model.updated_at = datetime.utcnow()

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to verify user: {str(e)}")

    def update_password(self, user_id: int, password: str) -> None:
        """
        Update a user's password.

        Args:
            user_id: The ID of the user
            password: The new plain text password
        """
        try:
            user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user_model:
                raise ValueError(f"User with ID {user_id} not found")

            user_model.password_hash = self._hash_password(password)
            user_model.password_reset_token = None
            user_model.password_reset_token_expires_at = None
            user_model.updated_at = datetime.utcnow()

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to update password: {str(e)}")

    def set_verification_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        """
        Set a verification token for a user.

        Args:
            user_id: The ID of the user
            token: The verification token
            expires_at: When the token expires
        """
        try:
            user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user_model:
                raise ValueError(f"User with ID {user_id} not found")

            user_model.verification_token = token
            user_model.verification_token_expires_at = expires_at
            user_model.updated_at = datetime.utcnow()

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to set verification token: {str(e)}")

    def set_password_reset_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        """
        Set a password reset token for a user.

        Args:
            user_id: The ID of the user
            token: The password reset token
            expires_at: When the token expires
        """
        try:
            user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user_model:
                raise ValueError(f"User with ID {user_id} not found")

            user_model.password_reset_token = token
            user_model.password_reset_token_expires_at = expires_at
            user_model.updated_at = datetime.utcnow()

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to set password reset token: {str(e)}")

    def get_by_verification_token(self, token: str) -> Optional[User]:
        """
        Get a user by verification token.

        Args:
            token: The verification token

        Returns:
            The user if found and token is valid, None otherwise
        """
        try:
            now = datetime.utcnow()
            user_model = self.db.query(UserModel).filter(
                UserModel.verification_token == token,
                UserModel.verification_token_expires_at > now
            ).first()

            if user_model:
                return user_model.to_domain()
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to get user by verification token: {str(e)}")

    def get_by_password_reset_token(self, token: str) -> Optional[User]:
        """
        Get a user by password reset token.

        Args:
            token: The password reset token

        Returns:
            The user if found and token is valid, None otherwise
        """
        try:
            now = datetime.utcnow()
            user_model = self.db.query(UserModel).filter(
                UserModel.password_reset_token == token,
                UserModel.password_reset_token_expires_at > now
            ).first()

            if user_model:
                return user_model.to_domain()
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to get user by password reset token: {str(e)}")

    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: The plain text password

        Returns:
            The hashed password
        """
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            plain_password: The plain text password
            hashed_password: The hashed password

        Returns:
            True if the password matches, False otherwise
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
