
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose.exceptions import JWTError

import asyncio
from starlette_prometheus import PrometheusMiddleware
from infrastructure.monitoring.metrics import MetricsMiddleware
from infrastructure.cache.config import setup_cache
from fastapi_csrf_protect import CsrfProtect
from infrastructure.config.csrf_config import get_csrf_config
from infrastructure.api.rate_limiter import RedisRateLimiter
from infrastructure.api.dependencies import get_refresh_token_repository
from infrastructure.config.settings import settings
from infrastructure.api.security import SecurityHeadersMiddleware
from infrastructure.api.sanitization import InputSanitizationMiddleware
from presentation.api.routers import router
from infrastructure.exceptions import RepositoryError
from infrastructure.api.exception_handlers import (
    validation_exception_handler,
    repository_exception_handler,
    sqlalchemy_exception_handler,
    jwt_exception_handler,
    general_exception_handler
)

from fastapi import status
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await setup_cache(app)
    asyncio.create_task(setup_token_cleanup())
    yield
    # Shutdown
    try:
        if hasattr(app.state, "redis_cache") and app.state.redis_cache:
            await app.state.redis_cache.close()
    except Exception:
        pass

    try:
        if hasattr(app.state, "redis_rate_limiter") and app.state.redis_rate_limiter:
            await app.state.redis_rate_limiter.close()
    except Exception:
        pass

app = FastAPI(
    title="Scheduler API",
    description="API for the Scheduler system",
    version="1.0.0",
    lifespan=lifespan
)

# Periodic task for token cleanup
async def setup_token_cleanup():
    CLEANUP_INTERVAL = 24 * 60 * 60  # 24 hours

    async def cleanup_expired_tokens():
        try:
            refresh_token_repository = get_refresh_token_repository()
            refresh_token_repository.delete_expired_tokens()
        except Exception:
            pass

    async def periodic_task():
        while True:
            await cleanup_expired_tokens()
            await asyncio.sleep(CLEANUP_INTERVAL)

    asyncio.create_task(periodic_task())

# Add middlewares
app.add_middleware(MetricsMiddleware)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token", "X-API-Key"],
)
app.add_middleware(
    RedisRateLimiter,
    limit=100,  # 100 requests
    window=60,  # per minute
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    InputSanitizationMiddleware,
    allowed_tags=['p', 'b', 'i', 'em', 'strong', 'a', 'ul', 'ol', 'li', 'br', 'hr'],
    allowed_attributes={'a': ['href', 'title']},
    strip=True
)

# CSRF protection is now handled by fastapi-csrf-protect (dependency-injected)
@CsrfProtect.load_config
def get_csrf_config_wrapper():
    return get_csrf_config()

# Prometheus metrics endpoint
#not implemented.

# Exception handlers
from fastapi import HTTPException
from infrastructure.api.exception_handlers import (
    validation_exception_handler, repository_exception_handler,
    sqlalchemy_exception_handler, jwt_exception_handler,
    http_exception_handler, general_exception_handler
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RepositoryError, repository_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Example CSRF token route for clients (optional)
@app.get("/api/v1/csrf-token")
async def get_csrf_token(response: Response, csrf_protect: CsrfProtect = CsrfProtect()):
    csrf_token = csrf_protect.generate_csrf()
    response.set_cookie(key="csrf_token", value=csrf_token, httponly=True)
    return {"csrf_token": csrf_token}

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
        version=settings.version,
        description="""
        # Scheduler API

        API for the Scheduler system, providing endpoints for managing schedules.

        ## Authentication

        This API uses JWT tokens for authentication. To authenticate:
        1. Call the `/api/v1/auth/token` endpoint with your credentials
        2. Use the returned token in the Authorization header: `Bearer {token}`

        ## API Key Authentication (API Clients)

        For non-browser clients, the API supports authentication using API keys:
        1. Create an API key using the `/api/v1/api-keys` endpoint (requires JWT authentication)
        2. Include the API key in the `X-API-Key` header for subsequent requests
        3. API clients using API keys are exempt from CSRF protection

        ## CSRF Protection

        All state-changing endpoints (POST, PUT, PATCH, DELETE) require CSRF protection for browser clients.

        ## Rate Limiting

        The API implements Redis-based distributed rate limiting to prevent abuse. Limits are:
        - 100 requests per minute per client across all API instances

        ## Error Handling

        All errors follow a consistent format with status code, message, and details.

        ## Caching

        The API implements caching for read-only endpoints to improve performance.
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
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        }
    }

    # Add global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}, {"apiKeyAuth": []}]

    # Add tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "Authentication operations"
        },
        {
            "name": "schedules",
            "description": "Operations related to schedules"
        },
        {
            "name": "teams",
            "description": "Operations related to teams"
        },
        {
            "name": "employees",
            "description": "Operations related to employees"
        },
        {
            "name": "workstations",
            "description": "Operations related to workstations"
        },
        {
            "name": "assignments",
            "description": "Operations related to assignments"
        },
        {
            "name": "status",
            "description": "Operations related to system status"
        },
        {
            "name": "tasks",
            "description": "Operations related to background tasks"
        },
        {
            "name": "api-keys",
            "description": "Operations related to API keys for non-browser clients"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi