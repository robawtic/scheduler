from fastapi import status

from infrastructure.models.UserModel import UserModel


def test_register_user_standard_endpoint(client, db_session, csrf_token):
    """
    Test registering a new user using the standardized endpoint.
    
    This test verifies that the standardized user registration endpoint at
    `/api/v1/users/register` works correctly with all required fields:
    - username
    - email
    - password
    - confirm_password
    """
    # Register a new user
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "standarduser",
            "email": "standard@example.com",
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
    
    # Check that the user data is correct
    assert data["user"]["username"] == "standarduser"
    assert data["user"]["email"] == "standard@example.com"
    
    # Check that the user was created in the database
    db_user = db_session.query(UserModel).filter(UserModel.username == "standarduser").first()
    assert db_user is not None
    assert db_user.username == "standarduser"
    assert db_user.email == "standard@example.com"

def test_register_user_missing_fields(client, db_session, csrf_token):
    """
    Test registering a user with missing required fields.
    
    This test verifies that the endpoint properly validates that all required fields
    are present in the request.
    """
    # Try to register without username
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "missing@example.com",
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
    
    # Try to register without email
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "missingfields",
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
    
    # Try to register without password
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "missingfields",
            "email": "missing@example.com",
            "confirm_password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the registration failed
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Check the error message
    data = response.json()
    assert "detail" in data
    assert any("password" in error["loc"] for error in data["detail"])
    
    # Try to register without confirm_password
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "missingfields",
            "email": "missing@example.com",
            "password": "password123"
        },
        headers={"X-CSRF-Token": csrf_token}
    )
    
    # Check that the registration failed
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Check the error message
    data = response.json()
    assert "detail" in data
    assert any("confirm_password" in error["loc"] for error in data["detail"])