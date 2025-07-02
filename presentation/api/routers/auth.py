from datetime import timedelta, datetime
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from infrastructure.api.auth import (
    create_access_token, create_refresh_token, validate_refresh_token
)
from infrastructure.config.settings import settings
from domain.repositories.interfaces.refresh_token_repository import RefreshTokenRepositoryInterface
from domain.repositories.interfaces.user_repository import UserRepositoryInterface
from infrastructure.api.dependencies import get_refresh_token_repository, get_user_repository, get_user_service
from infrastructure.api.dependencies_csrf import csrf_protection
from presentation.api.models import TokenResponse, UserRegistrationRequest, UserRegistrationResponse, UserResponse
from domain.services.user_service import UserService
from infrastructure.repositories.user_repository import verify_password
from domain.entities.user import User as UserEntity

router = APIRouter(prefix="/auth", tags=["authentication"])

class RefreshRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str

@router.post("/token", response_model=TokenResponse, response_model_exclude_unset=True, dependencies=[csrf_protection])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(get_refresh_token_repository),
    user_repository: UserRepositoryInterface = Depends(get_user_repository)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user_model = user_repository.get_user_for_auth(form_data.username)
    if not user_model or not verify_password(form_data.password, user_model.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_entity = UserEntity.from_orm(user_model)

    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={"sub": user_entity.username},
        roles=["viewer"],  # Default role
        expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": user_entity.username},
        user_id=user_entity.id,
        refresh_token_repository=refresh_token_repository,
        device_info=None,
        ip_address=None
    )

    # Calculate token expiration time
    expires_at = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_at=expires_at
    )

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

@router.post("/refresh", response_model=TokenResponse, response_model_exclude_unset=True, dependencies=[csrf_protection])
async def refresh_access_token(
    request: RefreshRequest,
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(get_refresh_token_repository)
):
    """
    Refresh access token using a refresh token.
    """
    # Validate refresh token
    try:
        user_data = await validate_refresh_token(request.refresh_token, refresh_token_repository)
    except HTTPException as e:
        raise e

    # Create new access token
    access_token_expires = timedelta(minutes=settings.jwt_expiration_minutes)
    access_token = create_access_token(
        data={"sub": user_data["username"]},
        roles=["viewer"],  # Default role
        expires_delta=access_token_expires
    )

    # Create new refresh token
    refresh_token = create_refresh_token(
        data={"sub": user_data["username"]},
        user_id=user_data["user_id"],
        refresh_token_repository=refresh_token_repository,
        device_info=None,
        ip_address=None
    )

    # Calculate token expiration time
    expires_at = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_at=expires_at
    )
