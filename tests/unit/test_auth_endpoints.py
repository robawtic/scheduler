from fastapi import status
from datetime import datetime

from infrastructure.models.UserModel import UserModel
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository

def test_login_success(client, db_session, csrf_token):
    """
    Test successful login with valid credentials.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )

    # Login with the user
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )

    # Check that the login was successful
    assert response.status_code == status.HTTP_200_OK

    # Check the response structure
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert "expires_at" in data
    assert data["token_type"] == "bearer"

    # Check that the tokens are not empty
    assert data["access_token"]
    assert data["refresh_token"]

    # Check that the expiration time is in the future
    expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
    assert expires_at > datetime.utcnow()

def test_login_invalid_credentials(client, db_session, csrf_token):
    """
    Test login with invalid credentials.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )

    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        },
        headers={"X-CSRF-Token": csrf_token}
    )

    # Check that the login failed
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Check the error message
    data = response.json()
    assert "detail" in data
    assert "Incorrect username or password" in data["detail"]

    # Try to login with non-existent user
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "nonexistent",
            "password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )

    # Check that the login failed
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_missing_csrf_token(client, db_session):
    """
    Test login without CSRF token.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )

    # Try to login without CSRF token
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "password123"
        }
    )

    # Check that the request was rejected
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Check the error message
    data = response.json()
    assert "detail" in data
    assert "CSRF" in data["detail"]

def test_refresh_token(client, db_session, csrf_token):
    """
    Test refreshing an access token with a refresh token.
    """
    # Create a user in the database
    repo = SQLAlchemyUserRepository(db_session)
    repo.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )

    # Login to get a refresh token
    login_response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )

    refresh_token = login_response.json()["refresh_token"]

    # Use the refresh token to get a new access token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
        headers={"X-CSRF-Token": csrf_token}
    )

    # Check that the refresh was successful
    assert refresh_response.status_code == status.HTTP_200_OK

    # Check the response structure
    data = refresh_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert "expires_at" in data

    # Check that the new tokens are different from the old ones
    assert data["access_token"] != login_response.json()["access_token"]
    assert data["refresh_token"] != refresh_token

def test_refresh_token_invalid(client, db_session, csrf_token):
    """
    Test refreshing with an invalid refresh token.
    """
    # Try to refresh with an invalid token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"},
        headers={"X-CSRF-Token": csrf_token}
    )

    # Check that the refresh failed
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Check the error message
    data = response.json()
    assert "detail" in data
    assert "Invalid refresh token" in data["detail"]

def test_register_user(client, db_session, csrf_token):
    """
    Test registering a new user.
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

    # Check that the user was created in the database
    db_user = db_session.query(UserModel).filter(UserModel.username == "newuser").first()
    assert db_user is not None
    assert db_user.username == "newuser"
    assert db_user.email == "new@example.com"

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
    assert "already registered" in data["detail"]

def test_register_user_password_mismatch(client, db_session, csrf_token):
    """
    Test registering a user with mismatched passwords.
    """
    # Try to register with mismatched passwords
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "different"
        },
        headers={"X-CSRF-Token": csrf_token}
    )

    # Check that the registration failed
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Check the error message
    data = response.json()
    assert "detail" in data
    assert any("Passwords do not match" in error["msg"] for error in data["detail"])

def test_register_user_invalid_email(client, db_session, csrf_token):
    """
    Test registering a user with an invalid email.
    """
    # Try to register with an invalid email
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "newuser",
            "email": "not-an-email",
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
    assert any("email" in error["loc"] for error in data["detail"])
