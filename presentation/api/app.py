from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose.exceptions import JWTError
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import asyncio

from infrastructure.config.settings import settings
from infrastructure.api.security import SecurityHeadersMiddleware
from infrastructure.api.sanitization import InputSanitizationMiddleware
from infrastructure.api.rate_limiter import RateLimiter
from infrastructure.api.dependencies import get_refresh_token_repository

from presentation.api.routers import router
from presentation.api.models import ErrorResponse, ErrorDetail

# Configure logging
logger = logging.getLogger("scheduler_api")

app = FastAPI(
    title="Scheduler API",
    description="API for the Scheduler system",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    # Initialize any startup tasks here
    # For example, setup cache, background tasks, etc.
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup resources on shutdown
    pass

# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        logger.info(f"Request started: {request.method} {request.url.path} (ID: {request_id})")

        start_time = time.time()
        try:
            response = await call_next(request)

            # Log response
            process_time = time.time() - start_time
            logger.info(f"Request completed: {request.method} {request.url.path} (ID: {request_id}, Status: {response.status_code}, Duration: {round(process_time * 1000)}ms)")

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url.path} (ID: {request_id}, Error: {str(e)}, Duration: {round(process_time * 1000)}ms)")
            raise

# Add middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://localhost:5176", "http://localhost:5178"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token", "X-API-Key"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputSanitizationMiddleware)
app.add_middleware(RateLimiter, limit=100, window=60)

# Import infrastructure/api modules
from infrastructure.api.exception_handlers import (
    validation_exception_handler, repository_exception_handler,
    sqlalchemy_exception_handler, jwt_exception_handler, 
    http_exception_handler, general_exception_handler
)
from infrastructure.exceptions import RepositoryError

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RepositoryError, repository_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add CSRF token route
@app.get("/api/v1/csrf-token")
async def get_csrf_token(response: Response):
    from infrastructure.api.csrf import set_csrf_cookie
    set_csrf_cookie(response)
    return {"message": "CSRF token set"}

# Include routers
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Scheduler API"}

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Scheduler API",
        version="1.0.0",
        description="""
        # Scheduler API

        API for the Scheduler system, providing endpoints for managing schedules.

        ## Authentication

        This API uses JWT tokens for authentication. To authenticate:
        1. Call the `/api/v1/auth/token` endpoint with your credentials
        2. Use the returned token in the Authorization header: `Bearer {token}`

        ## CSRF Protection

        All state-changing endpoints (POST, PUT, PATCH, DELETE) require CSRF protection:
        1. Call the `/api/v1/csrf-token` endpoint to get a CSRF token (set as a cookie)
        2. Include the token in the `X-CSRF-Token` header for all state-changing requests
        3. Missing or invalid CSRF tokens will result in a 403 Forbidden response

        ## Error Handling

        All errors follow a consistent format with status code, message, and details.
        """,
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        "csrfAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-CSRF-Token",
            "description": "CSRF token required for all state-changing operations (POST, PUT, PATCH, DELETE)"
        }
    }

    # Add global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}, {"csrfAuth": []}]

    # Add tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "Authentication operations"
        },
        {
            "name": "schedules",
            "description": "Operations related to schedules"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
