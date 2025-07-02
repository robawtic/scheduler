from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose.exceptions import JWTError
import logging

from infrastructure.exceptions import RepositoryError
from presentation.api.models import ErrorResponse, ErrorDetail

# Configure logging
logger = logging.getLogger("scheduler_api.exceptions")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors from FastAPI's request validation.
    """
    logger.warning(
        f"Validation error: {str(exc)}",
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "error_count": len(exc.errors())
        }
    )

    details = [
        ErrorDetail(
            loc=error.get("loc", []),
            msg=error.get("msg", ""),
            type=error.get("type", "")
        )
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation Error",
            details=details
        ).model_dump()
    )

async def repository_exception_handler(request: Request, exc: RepositoryError):
    """
    Handle custom repository exceptions.
    """
    logger.error(
        f"Repository error: {str(exc)}",
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "error_code": exc.code if hasattr(exc, 'code') and exc.code else "unknown"
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(exc),
            details={"code": exc.code} if hasattr(exc, 'code') and exc.code else None
        ).model_dump()
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle SQLAlchemy database exceptions.
    """
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "error_type": type(exc).__name__
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database Error",
            details={"error": str(exc)}
        ).model_dump()
    )

async def jwt_exception_handler(request: Request, exc: JWTError):
    """
    Handle JWT authentication exceptions.
    """
    logger.warning(
        f"JWT authentication error: {str(exc)}",
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "error_type": type(exc).__name__
        }
    )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ErrorResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Authentication Error",
            details={"error": str(exc)}
        ).model_dump(),
        headers={"WWW-Authenticate": "Bearer"}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTPExceptions and convert them to standardized ErrorResponse objects.
    """
    log_level = logging.WARNING if exc.status_code < 500 else logging.ERROR
    logger.log(
        log_level,
        f"HTTP exception: {exc.detail}",
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "status_code": exc.status_code
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status_code=exc.status_code,
            message=str(exc.detail),
            details=getattr(exc, "details", None)
        ).model_dump(),
        headers=exc.headers
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle any unhandled exceptions.
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "error_type": type(exc).__name__,
            "traceback": True  # This will include the traceback in the log
        },
        exc_info=True  # Include exception info in the log
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal Server Error",
            details={"error": str(exc)}
        ).model_dump()
    )
