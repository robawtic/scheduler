import pytest
from fastapi import status
import time

def test_complete_auth_flow(client, csrf_token):
    """
    Test the complete authentication flow:
    1. Register a new user
    2. Login with the new user
    3. Refresh the token
    """
    # Step 1: Register a new user
    register_response = client.post(
        "/api/v1/users/register",
        json={
            "username": "testflow",
            "email": "testflow@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that registration was successful
    assert register_response.status_code == status.HTTP_201_CREATED
    register_data = register_response.json()
    assert "user" in register_data
    assert register_data["user"]["username"] == "testflow"
    
    # Step 2: Login with the new user
    login_response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testflow",
            "password": "password123"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRF-Token": csrf_token
        }
    )
    
    # Check that login was successful
    assert login_response.status_code == status.HTTP_200_OK
    login_data = login_response.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert "token_type" in login_data
    assert "expires_at" in login_data
    
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]
    
    # Step 3: Use the access token to access a protected endpoint
    protected_response = client.get(
        "/api/v1/schedules",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-CSRF-Token": csrf_token
        }
    )
    
    # Check that access to protected resource was successful
    assert protected_response.status_code == status.HTTP_200_OK
    
    # Step 4: Refresh the token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that token refresh was successful
    assert refresh_response.status_code == status.HTTP_200_OK
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert "refresh_token" in refresh_data
    assert "token_type" in refresh_data
    assert "expires_at" in refresh_data
    
    # Verify the new tokens are different from the old ones
    assert refresh_data["access_token"] != access_token
    assert refresh_data["refresh_token"] != refresh_token
    
    # Step 5: Use the new access token
    new_access_token = refresh_data["access_token"]
    new_protected_response = client.get(
        "/api/v1/schedules",
        headers={
            "Authorization": f"Bearer {new_access_token}",
            "X-CSRF-Token": csrf_token
        }
    )
    
    # Check that access with the new token is successful
    assert new_protected_response.status_code == status.HTTP_200_OK

def test_csrf_protection(client):
    """
    Test that CSRF protection is working:
    1. Request without CSRF token should be rejected
    2. Request with valid CSRF token should be accepted
    """
    # Step 1: Get a CSRF token
    csrf_response = client.get("/api/v1/csrf-token")
    assert csrf_response.status_code == status.HTTP_200_OK
    
    # Extract the CSRF token from cookies
    csrf_cookie = next((cookie for cookie in client.cookies if cookie.name == "csrftoken"), None)
    assert csrf_cookie is not None
    csrf_token = csrf_cookie.value
    
    # Step 2: Try to register without CSRF token
    no_csrf_response = client.post(
        "/api/v1/users/register",
        json={
            "username": "nocsfr",
            "email": "nocsfr@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )
    
    # Check that the request was rejected
    assert no_csrf_response.status_code == status.HTTP_403_FORBIDDEN
    no_csrf_data = no_csrf_response.json()
    assert "detail" in no_csrf_data
    assert "CSRF" in no_csrf_data["detail"]
    
    # Step 3: Try to register with CSRF token
    with_csrf_response = client.post(
        "/api/v1/users/register",
        json={
            "username": "withcsfr",
            "email": "withcsfr@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the request was accepted
    assert with_csrf_response.status_code == status.HTTP_201_CREATED

def test_error_handling(client, csrf_token):
    """
    Test that error handling is working correctly:
    1. Validation errors
    2. Database errors
    3. Authentication errors
    """
    # Test validation error
    validation_response = client.post(
        "/api/v1/users/register",
        json={
            "username": "te",  # Too short
            "email": "invalid-email",  # Invalid email
            "password": "short",  # Too short
            "confirm_password": "different"  # Doesn't match
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the response is a validation error
    assert validation_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    validation_data = validation_response.json()
    assert "detail" in validation_data
    assert isinstance(validation_data["detail"], list)
    assert len(validation_data["detail"]) > 0
    
    # Test authentication error
    auth_response = client.get(
        "/api/v1/schedules",
        headers={"Authorization": "Bearer invalid-token"}
    )
    
    # Check that the response is an authentication error
    assert auth_response.status_code == status.HTTP_401_UNAUTHORIZED
    auth_data = auth_response.json()
    assert "detail" in auth_data
    
    # Test database error (try to register the same user twice)
    # First registration
    first_reg_response = client.post(
        "/api/v1/users/register",
        json={
            "username": "duperror",
            "email": "duperror@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    assert first_reg_response.status_code == status.HTTP_201_CREATED
    
    # Second registration with the same username
    second_reg_response = client.post(
        "/api/v1/users/register",
        json={
            "username": "duperror",
            "email": "another@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the response is a database error
    assert second_reg_response.status_code == status.HTTP_400_BAD_REQUEST
    second_reg_data = second_reg_response.json()
    assert "detail" in second_reg_data
    assert "already" in second_reg_data["detail"]