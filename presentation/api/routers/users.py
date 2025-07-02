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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
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

@router.post("/verify-email/{token}")
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

@router.post("/request-password-reset")
async def request_password_reset(
    email: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Request a password reset.
    
    This endpoint sends a password reset link to the user's email address.
    """
    if user_service.request_password_reset(email):
        return {"message": "Password reset instructions sent to your email"}
    else:
        # For security reasons, don't reveal whether the email exists
        return {"message": "If the email is registered, password reset instructions will be sent"}

@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    new_password: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Reset a user's password.
    
    This endpoint resets a user's password using the reset token sent to their email.
    """
    try:
        if user_service.reset_password(token, new_password):
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