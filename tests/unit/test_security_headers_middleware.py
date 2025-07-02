import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from infrastructure.api.security import SecurityHeadersMiddleware

def test_security_headers_middleware():
    """
    Test that the SecurityHeadersMiddleware adds the expected security headers to responses.
    """
    # Create a simple FastAPI app with the middleware
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    # Create a test client
    client = TestClient(app)
    
    # Make a request
    response = client.get("/test")
    
    # Check that the response has the expected security headers
    assert "Content-Security-Policy" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Permissions-Policy" in response.headers
    assert "X-Content-Type-Options" in response.headers
    
    # Check that X-XSS-Protection is not included (as it's deprecated)
    assert "X-XSS-Protection" not in response.headers

def test_security_headers_values():
    """
    Test that the security headers have the expected values.
    """
    # Create a simple FastAPI app with the middleware
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    # Create a test client
    client = TestClient(app)
    
    # Make a request
    response = client.get("/test")
    
    # Check the values of the security headers
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
    assert "DENY" in response.headers["X-Frame-Options"]
    assert "no-referrer-when-downgrade" in response.headers["Referrer-Policy"]
    assert "geolocation='none'" in response.headers["Permissions-Policy"]
    assert "nosniff" in response.headers["X-Content-Type-Options"]