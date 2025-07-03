import pytest
from datetime import datetime, timedelta

from infrastructure.models.UserModel import UserModel
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository

def test_create_user(db_session):
    """
    Test that a user can be created.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Check that the user was created
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_verified is False
    
    # Check that the user is in the database
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    assert db_user is not None
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"
    assert db_user.is_active is True
    assert db_user.is_verified is False
    
    # Check that the password was hashed
    assert db_user.password_hash is not None
    assert db_user.password_hash != "password123"

def test_create_user_duplicate_username(db_session):
    """
    Test that creating a user with a duplicate username raises an error.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Try to create another user with the same username
    with pytest.raises(ValueError):
        repo.create_user(
            username="testuser",
            email="another@example.com",
            password="password123"
        )

def test_create_user_duplicate_email(db_session):
    """
    Test that creating a user with a duplicate email raises an error.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    repo.create_user(
        username="testuser1",
        email="test@example.com",
        password="password123"
    )
    
    # Try to create another user with the same email
    with pytest.raises(ValueError):
        repo.create_user(
            username="testuser2",
            email="test@example.com",
            password="password123"
        )

def test_get_by_username(db_session):
    """
    Test that a user can be retrieved by username.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Get the user by username
    user = repo.get_by_username("testuser")
    
    # Check that the user was retrieved
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    
    # Check that a non-existent user returns None
    assert repo.get_by_username("nonexistent") is None

def test_get_by_email(db_session):
    """
    Test that a user can be retrieved by email.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Get the user by email
    user = repo.get_by_email("test@example.com")
    
    # Check that the user was retrieved
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    
    # Check that a non-existent email returns None
    assert repo.get_by_email("nonexistent@example.com") is None

def test_verify_user(db_session):
    """
    Test that a user can be verified.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Verify the user
    repo.verify_user(user.id)
    
    # Check that the user is verified
    user = repo.get_by_username("testuser")
    assert user.is_verified is True
    
    # Check that the verification token is cleared
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    assert db_user.verification_token is None
    assert db_user.verification_token_expires_at is None

def test_update_password(db_session):
    """
    Test that a user's password can be updated.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Get the original password hash
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    original_hash = db_user.password_hash
    
    # Update the password
    repo.update_password(user.id, "newpassword123")
    
    # Check that the password hash was updated
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    assert db_user.password_hash != original_hash
    
    # Check that the password reset token is cleared
    assert db_user.password_reset_token is None
    assert db_user.password_reset_token_expires_at is None

def test_set_verification_token(db_session):
    """
    Test that a verification token can be set for a user.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Set a verification token
    token = "test-verification-token"
    expires_at = datetime.utcnow() + timedelta(days=1)
    repo.set_verification_token(user.id, token, expires_at)
    
    # Check that the token was set
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    assert db_user.verification_token == token
    assert db_user.verification_token_expires_at == expires_at

def test_set_password_reset_token(db_session):
    """
    Test that a password reset token can be set for a user.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Set a password reset token
    token = "test-reset-token"
    expires_at = datetime.utcnow() + timedelta(hours=1)
    repo.set_password_reset_token(user.id, token, expires_at)
    
    # Check that the token was set
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    assert db_user.password_reset_token == token
    assert db_user.password_reset_token_expires_at == expires_at

def test_get_by_verification_token(db_session):
    """
    Test that a user can be retrieved by verification token.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Set a verification token
    token = "test-verification-token"
    expires_at = datetime.utcnow() + timedelta(days=1)
    repo.set_verification_token(user.id, token, expires_at)
    
    # Get the user by verification token
    retrieved_user = repo.get_by_verification_token(token)
    
    # Check that the user was retrieved
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    
    # Check that an expired token returns None
    expired_token = "expired-token"
    expired_at = datetime.utcnow() - timedelta(days=1)
    repo.set_verification_token(user.id, expired_token, expired_at)
    assert repo.get_by_verification_token(expired_token) is None
    
    # Check that a non-existent token returns None
    assert repo.get_by_verification_token("nonexistent-token") is None

def test_get_by_password_reset_token(db_session):
    """
    Test that a user can be retrieved by password reset token.
    """
    # Create a repository
    repo = SQLAlchemyUserRepository(db_session)
    
    # Create a user
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Set a password reset token
    token = "test-reset-token"
    expires_at = datetime.utcnow() + timedelta(hours=1)
    repo.set_password_reset_token(user.id, token, expires_at)
    
    # Get the user by password reset token
    retrieved_user = repo.get_by_password_reset_token(token)
    
    # Check that the user was retrieved
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    
    # Check that an expired token returns None
    expired_token = "expired-token"
    expired_at = datetime.utcnow() - timedelta(hours=1)
    repo.set_password_reset_token(user.id, expired_token, expired_at)
    assert repo.get_by_password_reset_token(expired_token) is None
    
    # Check that a non-existent token returns None
    assert repo.get_by_password_reset_token("nonexistent-token") is None