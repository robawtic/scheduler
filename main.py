from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose.exceptions import JWTError

from presentation.api.routers import schedules, auth
from infrastructure.database import create_database
from scripts.kill_api_process import find_and_kill_process_by_port

# Import infrastructure/api modules
from infrastructure.api.exception_handlers import (
    validation_exception_handler, repository_exception_handler,
    sqlalchemy_exception_handler, jwt_exception_handler, general_exception_handler
)
from infrastructure.api.rate_limiter import RateLimiter
from infrastructure.api.sanitization import InputSanitizationMiddleware
from infrastructure.api.security import SecurityHeadersMiddleware
from infrastructure.api.csrf import setup_csrf, set_csrf_cookie
from infrastructure.exceptions import RepositoryError

# Create database tables
create_database()

app = FastAPI(
    title="Heijunka Scheduling System",
    description="A workforce management system that optimizes employee scheduling across workstations.",
    version="1.0.0",
    # Disable automatic redirects to prevent CORS issues with trailing slashes
    redirect_slashes=False,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://localhost:5176", "http://localhost:5178"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token", "X-API-Key"],
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputSanitizationMiddleware)
app.add_middleware(RateLimiter, limit=100, window=60)

# Setup CSRF protection
setup_csrf(app)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RepositoryError, repository_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add CSRF token route
@app.get("/api/v1/csrf-token")
async def get_csrf_token(response: Response):
    set_csrf_cookie(response)
    return {"message": "CSRF token set"}

# Include routers
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    import socket

    def find_available_port(start_port, max_attempts=10):
        """Find an available port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            try:
                # Try to create a socket with the port
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("127.0.0.1", port))
                    return port
            except OSError:
                continue
        # If no ports are available, return None
        return None


    find_and_kill_process_by_port(8080)
    # Try to use port 8080, or find an available port
    port = find_available_port(8080)
    if port:
        print(f"Starting server on port {port}")
        uvicorn.run(app, host="127.0.0.1", port=port)
    else:
        print("No available ports found in the range 8080-8089")
