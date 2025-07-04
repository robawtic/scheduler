import pytest
from datetime import datetime, timedelta
import uuid

from domain.entities.refresh_token import RefreshToken
from infrastructure.models.RefreshTokenModel import RefreshTokenModel
from infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from infrastructure.exceptions import RepositoryError

def test_add_refresh_token(db_session):
    """
    Test that a refresh token can be added to the repository.
    """
    # Create a repository
    repo = RefreshTokenRepository(db_session)

    # Create a refresh token
    token_id = str(uuid.uuid4())
    user_id = 1
    expires_at = datetime.utcnow() + timedelta(days=7)
    refresh_token = RefreshToken(
        token_id=token_id,
        user_id=user_id,
        expires_at=expires_at,
        device_info="Test Device",
        ip_address="127.0.0.1"
    )

    # Add the token to the repository
    repo.add(refresh_token)

    # Check that the token was added to the database
    db_token = db_session.query(RefreshTokenModel).filter(RefreshTokenModel.token_id == token_id).first()
    assert db_token is not None
    assert db_token.token_id == token_id
    assert db_token.user_id == user_id
    assert db_token.expires_at == expires_at
    assert db_token.device_info == "Test Device"
    assert db_token.ip_address == "127.0.0.1"
    assert db_token.is_revoked is False

def test_get_by_token_id(db_session):
    """
    Test that a refresh token can be retrieved by its ID.
    """
    # Create a repository
    repo = RefreshTokenRepository(db_session)

    # Create a refresh token
    token_id = str(uuid.uuid4())
    user_id = 1
    expires_at = datetime.utcnow() + timedelta(days=7)
    refresh_token = RefreshToken(
        token_id=token_id,
        user_id=user_id,
        expires_at=expires_at
    )

    # Add the token to the repository
    repo.add(refresh_token)

    # Get the token by ID
    retrieved_token = repo.get_by_token_id(token_id)

    # Check that the token was retrieved
    assert retrieved_token is not None
    assert retrieved_token.token_id == token_id
    assert retrieved_token.user_id == user_id
    assert retrieved_token.expires_at == expires_at

    # Check that a non-existent token returns None
    assert repo.get_by_token_id("nonexistent-token") is None

def test_revoke(db_session):
    """
    Test that a refresh token can be revoked.
    """
    # Create a repository
    repo = RefreshTokenRepository(db_session)

    # Create a refresh token
    token_id = str(uuid.uuid4())
    user_id = 1
    expires_at = datetime.utcnow() + timedelta(days=7)
    refresh_token = RefreshToken(
        token_id=token_id,
        user_id=user_id,
        expires_at=expires_at
    )

    # Add the token to the repository
    repo.add(refresh_token)

    # Revoke the token
    repo.revoke(token_id)

    # Check that the token is revoked
    db_token = db_session.query(RefreshTokenModel).filter(RefreshTokenModel.token_id == token_id).first()
    assert db_token.is_revoked is True

    # Check that the token is revoked in the domain entity
    retrieved_token = repo.get_by_token_id(token_id)
    assert retrieved_token.is_revoked is True

def test_revoke_nonexistent_token(db_session):
    """
    Test that revoking a non-existent token raises an error.
    """
    # Create a repository
    repo = RefreshTokenRepository(db_session)

    # Try to revoke a non-existent token
    with pytest.raises(RepositoryError):
        repo.revoke("nonexistent-token")

def test_revoke_all_for_user(db_session):
    """
    Test that all refresh tokens for a user can be revoked.
    """
    # Create a repository
    repo = RefreshTokenRepository(db_session)

    # Create multiple refresh tokens for the same user
    user_id = 1
    expires_at = datetime.utcnow() + timedelta(days=7)

    token1 = RefreshToken(
        token_id=str(uuid.uuid4()),
        user_id=user_id,
        expires_at=expires_at
    )

    token2 = RefreshToken(
        token_id=str(uuid.uuid4()),
        user_id=user_id,
        expires_at=expires_at
    )

    # Create a token for a different user
    token3 = RefreshToken(
        token_id=str(uuid.uuid4()),
        user_id=2,
        expires_at=expires_at
    )

    # Add the tokens to the repository
    repo.add(token1)
    repo.add(token2)
    repo.add(token3)

    # Revoke all tokens for user 1
    repo.revoke_all_for_user(user_id)

    # Check that the tokens for user 1 are revoked
    db_tokens = db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user_id).all()
    for token in db_tokens:
        assert token.is_revoked is True

    # Check that the token for user 2 is not revoked
    db_token3 = db_session.query(RefreshTokenModel).filter(RefreshTokenModel.token_id == token3.token_id).first()
    assert db_token3.is_revoked is False

def test_delete_expired(db_session):
    """
    Test that expired refresh tokens can be deleted.
    """
    # Create a repository
    repo = RefreshTokenRepository(db_session)

    # Create an expired token
    expired_token = RefreshToken(
        token_id=str(uuid.uuid4()),
        user_id=1,
        expires_at=datetime.utcnow() - timedelta(days=1)
    )

    # Create a valid token
    valid_token = RefreshToken(
        token_id=str(uuid.uuid4()),
        user_id=1,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    # Create an expired but revoked token (should not be deleted)
    expired_revoked_token = RefreshToken(
        token_id=str(uuid.uuid4()),
        user_id=1,
        expires_at=datetime.utcnow() - timedelta(days=1),
        is_revoked=True
    )

    # Add the tokens to the repository
    repo.add(expired_token)
    repo.add(valid_token)
    repo.add(expired_revoked_token)

    # Delete expired tokens
    deleted_count = repo.delete_expired()

    # Check that only the expired non-revoked token was deleted
    assert deleted_count == 1

    # Check that the expired token is gone
    assert repo.get_by_token_id(expired_token.token_id) is None

    # Check that the valid token is still there
    assert repo.get_by_token_id(valid_token.token_id) is not None

    # Check that the expired revoked token is still there
    assert repo.get_by_token_id(expired_revoked_token.token_id) is not None
