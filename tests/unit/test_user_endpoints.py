from fastapi import status
from datetime import datetime, timedelta

from infrastructure.models.UserModel import UserModel
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository

def test_register_user_endpoint(client, db_session, csrf_token):
    """
    Test registering a new user through the users endpoint.
    """
    # Register a new user
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the registration was successful
    assert response.status_code == status.HTTP_201_CREATED
    
    # Check the response structure
    data = response.json()
    assert "message" in data
    assert "user" in data
    assert "id" in data["user"]
    assert "username" in data["user"]
    assert "email" in data["user"]
    assert "is_active" in data["user"]
    assert "is_verified" in data["user"]
    assert "created_at" in data["user"]
    
    # Check the user data
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["is_active"] is True
    assert data["user"]["is_verified"] is False
    
    # Check that the user was created in the database
    db_user = db_session.query(UserModel).filter(UserModel.username == "newuser").first()
    assert db_user is not None
    assert db_user.username == "newuser"
    assert db_user.email == "new@example.com"
    assert db_user.is_active is True
    assert db_user.is_verified is False

def test_register_user_duplicate_username(client, db_session, csrf_token):
    """
    Test registering a user with a duplicate username.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Try to register a user with the same username
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the registration failed
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Check the error message
    data = response.json()
    assert "detail" in data
    assert "already registered" in data["detail"] or "already taken" in data["detail"]

def test_register_user_duplicate_email(client, db_session, csrf_token):
    """
    Test registering a user with a duplicate email.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Try to register a user with the same email
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "newuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the registration failed
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Check the error message
    data = response.json()
    assert "detail" in data
    assert "already registered" in data["detail"] or "already taken" in data["detail"]

def test_register_user_invalid_data(client, db_session, csrf_token):
    """
    Test registering a user with invalid data.
    """
    # Try to register with a short username
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "ab",  # Too short
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the registration failed
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Check the error message
    data = response.json()
    assert "detail" in data
    assert any("username" in error["loc"] for error in data["detail"])
    
    # Try to register with a short password
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "short",  # Too short
            "confirm_password": "short"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the registration failed
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Check the error message
    data = response.json()
    assert "detail" in data
    assert any("password" in error["loc"] for error in data["detail"])
    
    # Try to register with non-alphanumeric username
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "user@name",  # Contains special characters
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the registration failed
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Check the error message
    data = response.json()
    assert "detail" in data
    assert any("username" in error["loc"] for error in data["detail"])

def test_verify_email(client, db_session, csrf_token):
    """
    Test verifying a user's email.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Set a verification token
    token = "test-verification-token"
    expires_at = datetime.utcnow() + timedelta(days=1)
    repo.set_verification_token(user.id, token, expires_at)
    
    # Verify the email
    response = client.post(
        f"/api/v1/users/verify-email/{token}",
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the verification was successful
    assert response.status_code == status.HTTP_200_OK
    
    # Check the response message
    data = response.json()
    assert "message" in data
    assert "verified" in data["message"]
    
    # Check that the user is verified in the database
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    assert db_user.is_verified is True
    assert db_user.verification_token is None
    assert db_user.verification_token_expires_at is None

def test_verify_email_invalid_token(client, db_session, csrf_token):
    """
    Test verifying a user's email with an invalid token.
    """
    # Try to verify with an invalid token
    response = client.post(
        "/api/v1/users/verify-email/invalid-token",
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the verification failed
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Check the error message
    data = response.json()
    assert "detail" in data
    assert "Invalid" in data["detail"] or "expired" in data["detail"]

def test_request_password_reset(client, db_session, csrf_token):
    """
    Test requesting a password reset.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Request a password reset
    response = client.post(
        "/api/v1/users/request-password-reset",
        params={"email": "test@example.com"},
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the request was successful
    assert response.status_code == status.HTTP_200_OK
    
    # Check the response message
    data = response.json()
    assert "message" in data
    assert "reset" in data["message"]
    
    # Check that a password reset token was set in the database
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    assert db_user.password_reset_token is not None
    assert db_user.password_reset_token_expires_at is not None

def test_reset_password(client, db_session, csrf_token):
    """
    Test resetting a password.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Set a password reset token
    token = "test-reset-token"
    expires_at = datetime.utcnow() + timedelta(hours=1)
    repo.set_password_reset_token(user.id, token, expires_at)
    
    # Get the original password hash
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    original_hash = db_user.password_hash
    
    # Reset the password
    response = client.post(
        f"/api/v1/users/reset-password/{token}",
        params={"new_password": "newpassword123"},
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the reset was successful
    assert response.status_code == status.HTTP_200_OK
    
    # Check the response message
    data = response.json()
    assert "message" in data
    assert "reset" in data["message"]
    
    # Check that the password was updated in the database
    db_user = db_session.query(UserModel).filter(UserModel.username == "testuser").first()
    assert db_user.password_hash != original_hash
    assert db_user.password_reset_token is None
    assert db_user.password_reset_token_expires_at is None