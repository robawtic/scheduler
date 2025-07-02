from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, EmailStr, validator, constr
from datetime import datetime

class ErrorDetail(BaseModel):
    """Model for detailed error information."""
    loc: List[str] = []
    msg: str = ""
    type: str = ""

class ErrorResponse(BaseModel):
    """Standard error response model."""
    status_code: int
    message: str
    details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "status_code": 400,
                "message": "Bad Request",
                "details": [
                    {
                        "loc": ["body", "username"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        }

class BaseResponse(BaseModel):
    """Base response model with common fields."""
    id: int = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class TokenRequest(BaseModel):
    """Model for token request."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    @validator('username')
    def sanitize_username(cls, v):
        """Sanitize username input."""
        return v.strip()

    @validator('password')
    def sanitize_password(cls, v):
        """Sanitize password input."""
        return v

class TokenResponse(BaseModel):
    """Model for token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_at: datetime = Field(..., description="Token expiration timestamp")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_at": "2023-01-01T00:00:00Z"
            }
        }

class UserRegistrationRequest(BaseModel):
    """Model for user registration request."""
    username: constr(min_length=3, max_length=50) = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: constr(min_length=8) = Field(..., description="Password")
    confirm_password: str = Field(..., description="Confirm password")

    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username is alphanumeric."""
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validate that passwords match."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

# Alias for backward compatibility
UserCreate = UserRegistrationRequest

class UserResponse(BaseModel):
    """Model for user response."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    is_active: bool = Field(..., description="Whether the user is active")
    is_verified: bool = Field(..., description="Whether the user is verified")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john.doe@example.com",
                "is_active": True,
                "is_verified": False,
                "created_at": "2023-01-01T00:00:00Z"
            }
        }

class UserRegistrationResponse(BaseModel):
    """Model for user registration response."""
    message: str = Field(..., description="Registration message")
    user: UserResponse = Field(..., description="User details")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "User registered successfully. Please check your email to verify your account.",
                "user": {
                    "id": 1,
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2023-01-01T00:00:00Z"
                }
            }
        }
