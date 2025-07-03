"""
Query parameter validation and sanitization utilities.

This module provides functions for validating and sanitizing query parameters
at the endpoint handler level, since middleware cannot mutate query parameters.
"""

import re
from typing import Optional, Any, Dict, List, Union, Callable
from fastapi import HTTPException, Query, status
from pydantic import BaseModel, EmailStr, validator, Field

# Regular expressions for validation
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
ALPHANUMERIC_REGEX = r'^[a-zA-Z0-9_]+$'
DANGEROUS_CHARS_REGEX = r'[<>\'"`;()]'

class SanitizedStr(str):
    """A string type that is automatically sanitized."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        return cls(sanitize_string(v))

def sanitize_string(value: str) -> str:
    """
    Sanitize a string by removing potentially dangerous characters.

    Args:
        value: The string to sanitize

    Returns:
        The sanitized string
    """
    if not value:
        return value

    # Remove dangerous characters
    return re.sub(DANGEROUS_CHARS_REGEX, '', value)

def validate_email(email: str) -> str:
    """
    Validate and sanitize an email address.

    Args:
        email: The email address to validate

    Returns:
        The sanitized email address

    Raises:
        HTTPException: If the email address is invalid
    """
    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email address is required"
        )

    # Sanitize the email
    sanitized_email = sanitize_string(email)

    # Validate the email format
    if not re.match(EMAIL_REGEX, sanitized_email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email address format"
        )

    return sanitized_email

def validate_password(password: str, min_length: int = 8) -> str:
    """
    Validate and sanitize a password.

    Args:
        password: The password to validate
        min_length: The minimum length of the password

    Returns:
        The sanitized password

    Raises:
        HTTPException: If the password is invalid
    """
    if not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password is required"
        )

    # Sanitize the password
    sanitized_password = sanitize_string(password)

    # Check minimum length
    if len(sanitized_password) < min_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at least {min_length} characters long"
        )

    return sanitized_password

def validate_query_param(
    param: str, 
    name: str, 
    required: bool = True,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    custom_validator: Optional[Callable[[str], Any]] = None
) -> str:
    """
    Validate and sanitize a generic query parameter.

    Args:
        param: The parameter value to validate
        name: The name of the parameter (for error messages)
        required: Whether the parameter is required
        min_length: The minimum length of the parameter
        max_length: The maximum length of the parameter
        pattern: A regex pattern that the parameter must match
        custom_validator: A custom validation function

    Returns:
        The sanitized parameter value

    Raises:
        HTTPException: If the parameter is invalid
    """
    # Check if required
    if required and not param:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{name} is required"
        )

    # If not required and empty, return empty
    if not required and not param:
        return param

    # Sanitize the parameter
    sanitized_param = sanitize_string(param)

    # Check minimum length
    if min_length is not None and len(sanitized_param) < min_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{name} must be at least {min_length} characters long"
        )

    # Check maximum length
    if max_length is not None and len(sanitized_param) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{name} must be at most {max_length} characters long"
        )

    # Check pattern
    if pattern is not None and not re.match(pattern, sanitized_param):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{name} has an invalid format"
        )

    # Apply custom validator
    if custom_validator is not None:
        try:
            sanitized_param = custom_validator(sanitized_param)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )

    return sanitized_param

# Pydantic models for common query parameters
class PaginationQueryParams(BaseModel):
    """
    Model for pagination query parameters.
    """
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(50, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field(s), format: field:direction (e.g., created_at:desc,name:asc)")

    @validator('sort_by')
    def validate_sort_by(cls, v):
        if not v:
            return v

        # Sanitize the sort_by parameter
        sanitized_sort_by = sanitize_string(v)

        # Validate the sort_by format
        for sort_item in sanitized_sort_by.split(','):
            if ':' in sort_item:
                field, direction = sort_item.split(':', 1)
                if direction.lower() not in ('asc', 'desc'):
                    raise ValueError(f"Invalid sort direction: {direction}. Must be 'asc' or 'desc'")

                # Validate field name (alphanumeric plus underscore)
                if not re.match(ALPHANUMERIC_REGEX, field.strip()):
                    raise ValueError(f"Invalid sort field: {field}. Must be alphanumeric")

        return sanitized_sort_by

class SearchQueryParams(BaseModel):
    """
    Model for search query parameters.
    """
    q: str = Field(..., min_length=1, max_length=100, description="Search query")
    fields: Optional[str] = Field(None, description="Fields to search, comma-separated")

    @validator('q')
    def validate_q(cls, v):
        return sanitize_string(v)

    @validator('fields')
    def validate_fields(cls, v):
        if not v:
            return v

        # Sanitize the fields parameter
        sanitized_fields = sanitize_string(v)

        # Validate each field name
        for field in sanitized_fields.split(','):
            if not re.match(ALPHANUMERIC_REGEX, field.strip()):
                raise ValueError(f"Invalid field name: {field}. Must be alphanumeric")

        return sanitized_fields
