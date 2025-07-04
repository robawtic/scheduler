from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from domain.entities.refresh_token import RefreshToken
from infrastructure.models.RefreshTokenModel import RefreshTokenModel
from domain.repositories.interfaces.refresh_token_repository import RefreshTokenRepositoryInterface
from infrastructure.exceptions import RepositoryError

class RefreshTokenRepository(RefreshTokenRepositoryInterface):
    """Implementation of RefreshTokenRepositoryInterface."""

    def __init__(self, db: Session):
        """
        Initialize the repository.

        Args:
            db: database session
        """
        self.db = db

    def add(self, refresh_token: RefreshToken) -> None:
        """
        Add a refresh token to the repository.

        Args:
            refresh_token: The refresh token to add
        """
        try:
            db_token = RefreshTokenModel(
                token_id=refresh_token.token_id,
                user_id=refresh_token.user_id,
                expires_at=refresh_token.expires_at,
                is_revoked=refresh_token.is_revoked,
                device_info=refresh_token.device_info,
                ip_address=refresh_token.ip_address,
                created_at=refresh_token.created_at
            )
            self.db.add(db_token)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to add refresh token: {str(e)}")

    def get_by_token_id(self, token_id: str) -> Optional[RefreshToken]:
        """
        Get a refresh token by its ID.

        Args:
            token_id: The ID of the token to get

        Returns:
            The refresh token if found, None otherwise
        """
        try:
            db_token = self.db.query(RefreshTokenModel).filter(
                RefreshTokenModel.token_id == token_id
            ).first()

            if db_token is None:
                return None

            return RefreshToken(
                token_id=db_token.token_id,
                user_id=db_token.user_id,
                expires_at=db_token.expires_at,
                is_revoked=db_token.is_revoked,
                device_info=db_token.device_info,
                ip_address=db_token.ip_address,
                created_at=db_token.created_at
            )
        except Exception as e:
            raise RepositoryError(f"Failed to get refresh token: {str(e)}")

    def revoke(self, token_id: str) -> None:
        """
        Revoke a refresh token.

        Args:
            token_id: The ID of the token to revoke
        """
        try:
            db_token = self.db.query(RefreshTokenModel).filter(
                RefreshTokenModel.token_id == token_id
            ).first()

            if db_token is None:
                raise RepositoryError(f"Refresh token with ID {token_id} not found")

            db_token.is_revoked = True
            self.db.commit()
        except RepositoryError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to revoke refresh token: {str(e)}")

    def revoke_all_for_user(self, user_id: int) -> None:
        """
        Revoke all refresh tokens for a user.

        Args:
            user_id: The ID of the user
        """
        try:
            self.db.query(RefreshTokenModel).filter(
                RefreshTokenModel.user_id == user_id
            ).update({"is_revoked": True})
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to revoke refresh tokens for user: {str(e)}")

    def delete_expired(self) -> int:
        """
        Delete all expired refresh tokens.

        Returns:
            The number of tokens deleted
        """
        try:
            now = datetime.utcnow()
            result = self.db.query(RefreshTokenModel).filter(
                and_(
                    RefreshTokenModel.expires_at < now,
                    RefreshTokenModel.is_revoked == False
                )
            ).delete()
            self.db.commit()
            return result
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to delete expired refresh tokens: {str(e)}")
