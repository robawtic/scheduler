from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from domain.services.user_service import UserService
from presentation.api.models import UserRegistrationRequest, UserRegistrationResponse, UserResponse
from presentation.api.dependencies import get_user_service
from infrastructure.api.dependencies_csrf import csrf_protection

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserRegistrationResponse, status_code=status.HTTP_201_CREATED, dependencies=[csrf_protection])
async def register_user(
    user_data: UserRegistrationRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Register a new user.

    This endpoint allows users to register with a username, email, and password.
    The password must be at least 8 characters long and match the confirm_password field.

    Required fields:
    - username: Alphanumeric, 3-50 characters
    - email: Valid email address
    - password: Minimum 8 characters
    - confirm_password: Must match password
    """
    try:
        # Register the user
        user = user_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )

        # Create the response
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )

        return UserRegistrationResponse(
            message="User registered successfully. Please check your email to verify your account.",
            user=user_response
        )
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IntegrityError:
        # Handle database integrity errors (e.g., duplicate username or email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    except Exception as e:
        # Handle other errors
        # Log the detailed error for debugging
        import logging
        logger = logging.getLogger("scheduler_api")
        logger.error(
            f"Error during user registration: {str(e)}",
            extra={
                "username": user_data.username,
                "email": user_data.email,
                "error_type": type(e).__name__,
                "error_details": str(e)
            },
            exc_info=True
        )
        # Return a generic error message to the client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration. Please try again later or contact support."
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    # This would use the current user from the token
    # current_user: User = Depends(get_current_user)
):
    """
    Get the current user's profile.

    This endpoint returns the profile of the currently authenticated user.
    """
    # This is a placeholder - in a real implementation, we would use the current user from the token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="This endpoint is not yet implemented"
    )

@router.post("/verify-email/{token}", dependencies=[csrf_protection])
async def verify_email(
    token: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Verify a user's email address.

    This endpoint verifies a user's email address using the verification token sent to their email.
    """
    if user_service.verify_email(token):
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

@router.post("/request-password-reset", dependencies=[csrf_protection])
async def request_password_reset(
    email: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Request a password reset.

    This endpoint sends a password reset link to the user's email address.

    Query Parameters:
    - email: A valid email address
    """
    # Validate and sanitize the email
    from infrastructure.api.query_validation import validate_email
    sanitized_email = validate_email(email)

    if user_service.request_password_reset(sanitized_email):
        return {"message": "Password reset instructions sent to your email"}
    else:
        # For security reasons, don't reveal whether the email exists
        return {"message": "If the email is registered, password reset instructions will be sent"}

@router.post("/reset-password/{token}", dependencies=[csrf_protection])
async def reset_password(
    token: str,
    new_password: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Reset a user's password.

    This endpoint resets a user's password using the reset token sent to their email.

    Path Parameters:
    - token: The password reset token sent to the user's email

    Query Parameters:
    - new_password: The new password (minimum 8 characters)
    """
    # Validate and sanitize the token
    from infrastructure.api.query_validation import validate_query_param, validate_password

    # Validate the token (basic sanitization)
    sanitized_token = validate_query_param(token, "token")

    # Validate and sanitize the new password
    sanitized_password = validate_password(new_password)

    try:
        if user_service.reset_password(sanitized_token, sanitized_password):
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
