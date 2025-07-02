import pytest
import time
from fastapi import FastAPI, status
from starlette.testclient import TestClient

from infrastructure.api.rate_limiter import RateLimiter

def test_rate_limiter_allows_requests_under_limit():
    """
    Test that the RateLimiter allows requests under the limit.
    """
    # Create a simple FastAPI app with the middleware
    app = FastAPI()
    app.add_middleware(RateLimiter, limit=5, window=1)  # 5 requests per second
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    # Create a test client
    client = TestClient(app)
    
    # Make multiple requests under the limit
    for _ in range(5):
        response = client.get("/test")
        assert response.status_code == 200
        
    # Check rate limit headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert response.headers["X-RateLimit-Limit"] == "5"
    assert int(response.headers["X-RateLimit-Remaining"]) >= 0

def test_rate_limiter_blocks_requests_over_limit():
    """
    Test that the RateLimiter blocks requests over the limit.
    """
    # Create a simple FastAPI app with the middleware
    app = FastAPI()
    app.add_middleware(RateLimiter, limit=3, window=1)  # 3 requests per second
    
    @app.get("/test-limit")
    async def test_endpoint():
        return {"message": "test"}
    
    # Create a test client
    client = TestClient(app)
    
    # Make requests up to the limit
    for _ in range(3):
        response = client.get("/test-limit")
        assert response.status_code == 200
    
    # Make one more request that should be blocked
    response = client.get("/test-limit")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    # Check error response
    assert "message" in response.json()
    assert "Too many requests" in response.json()["message"]

def test_rate_limiter_resets_after_window():
    """
    Test that the RateLimiter resets after the time window.
    """
    # Create a simple FastAPI app with the middleware
    app = FastAPI()
    app.add_middleware(RateLimiter, limit=2, window=1)  # 2 requests per 1 second
    
    @app.get("/test-reset")
    async def test_endpoint():
        return {"message": "test"}
    
    # Create a test client
    client = TestClient(app)
    
    # Make requests up to the limit
    for _ in range(2):
        response = client.get("/test-reset")
        assert response.status_code == 200
    
    # Make one more request that should be blocked
    response = client.get("/test-reset")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    # Wait for the window to reset
    time.sleep(1.1)  # Wait slightly longer than the window
    
    # Make another request that should now be allowed
    response = client.get("/test-reset")
    assert response.status_code == 200

def test_rate_limiter_different_clients():
    """
    Test that the RateLimiter tracks different clients separately.
    """
    # Create a simple FastAPI app with the middleware
    app = FastAPI()
    
    # Use a custom key function to identify clients by the X-Client-ID header
    def get_client_id(request):
        return request.headers.get("X-Client-ID", "default")
    
    app.add_middleware(RateLimiter, limit=2, window=1, key_func=get_client_id)
    
    @app.get("/test-clients")
    async def test_endpoint():
        return {"message": "test"}
    
    # Create a test client
    client = TestClient(app)
    
    # Make requests for client 1
    for _ in range(2):
        response = client.get("/test-clients", headers={"X-Client-ID": "client1"})
        assert response.status_code == 200
    
    # Client 1 should now be blocked
    response = client.get("/test-clients", headers={"X-Client-ID": "client1"})
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    # Client 2 should still be allowed
    for _ in range(2):
        response = client.get("/test-clients", headers={"X-Client-ID": "client2"})
        assert response.status_code == 200
    
    # Client 2 should now be blocked
    response = client.get("/test-clients", headers={"X-Client-ID": "client2"})
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS