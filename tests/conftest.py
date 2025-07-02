import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
import sys
from typing import Generator, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domain.models.Base import Base
from infrastructure.database import get_db
from main import app

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Use the session in the tests
    yield session
    
    # Roll back the transaction and close the session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI TestClient with a database session.
    """
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Remove the dependency override
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def csrf_token(client: TestClient) -> str:
    """
    Get a CSRF token for testing.
    """
    response = client.get("/api/v1/csrf-token")
    assert response.status_code == 200
    
    # Extract the CSRF token from cookies
    csrf_cookie = next((cookie for cookie in client.cookies if cookie.name == "csrftoken"), None)
    assert csrf_cookie is not None
    
    return csrf_cookie.value

@pytest.fixture(scope="function")
def auth_headers(client: TestClient, csrf_token: str, db_session: Session) -> Dict[str, str]:
    """
    Get authentication headers for testing.
    
    This fixture:
    1. Creates a test user
    2. Logs in as the test user
    3. Returns the authentication headers
    """
    from infrastructure.repositories.user_repository import SQLAlchemyUserRepository
    
    # Create a test user
    repo = SQLAlchemyUserRepository(db_session)
    repo.create_user(
        username="testauth",
        email="testauth@example.com",
        password="password123"
    )
    
    # Login as the test user
    login_response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testauth",
            "password": "password123"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRF-Token": csrf_token
        }
    )
    
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    
    # Return the authentication headers
    return {
        "Authorization": f"Bearer {login_data['access_token']}",
        "X-CSRF-Token": csrf_token
    }

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> Dict[str, Any]:
    """
    Create a test user and return its details.
    """
    from infrastructure.repositories.user_repository import SQLAlchemyUserRepository
    
    # Create a test user
    repo = SQLAlchemyUserRepository(db_session)
    user = repo.create_user(
        username="testuser",
        email="testuser@example.com",
        password="password123"
    )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }