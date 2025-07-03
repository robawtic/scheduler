# Query Parameter Validation Summary

## Overview

This document summarizes the changes made to harden input sanitization for query parameters in the Scheduler API. Since middleware cannot mutate query parameters, we've implemented validation and sanitization at the endpoint handler level.

## Endpoints Updated

### 1. User Password Reset Endpoints

#### `request_password_reset` Endpoint

**Path**: `/api/v1/users/request-password-reset`  
**Method**: POST  
**Query Parameters**:
- `email`: Email address to send password reset link to

**Validation Added**:
- Email format validation using regex pattern
- Removal of potentially dangerous characters
- Required parameter validation

**Example**:
```python
@router.post("/request-password-reset", dependencies=[csrf_protection])
async def request_password_reset(
    email: str,
    user_service: UserService = Depends(get_user_service)
):
    # Validate and sanitize the email
    from infrastructure.api.query_validation import validate_email
    sanitized_email = validate_email(email)
    
    if user_service.request_password_reset(sanitized_email):
        return {"message": "Password reset instructions sent to your email"}
    else:
        # For security reasons, don't reveal whether the email exists
        return {"message": "If the email is registered, password reset instructions will be sent"}
```

#### `reset_password` Endpoint

**Path**: `/api/v1/users/reset-password/{token}`  
**Method**: POST  
**Path Parameters**:
- `token`: Password reset token

**Query Parameters**:
- `new_password`: New password to set

**Validation Added**:
- Token sanitization to remove dangerous characters
- Password validation (minimum length of 8 characters)
- Removal of potentially dangerous characters from password

**Example**:
```python
@router.post("/reset-password/{token}", dependencies=[csrf_protection])
async def reset_password(
    token: str,
    new_password: str,
    user_service: UserService = Depends(get_user_service)
):
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
```

### 2. Schedule Listing Endpoint

**Path**: `/api/v1/schedules`  
**Method**: GET  
**Query Parameters**:
- `start_date`: Optional start date in ISO format (YYYY-MM-DD)
- `end_date`: Optional end date in ISO format (YYYY-MM-DD)
- `days`: Optional number of days to include (default: 7)

**Validation Added**:
- Date format validation using regex pattern
- Numeric validation for days parameter
- Range validation for days parameter (1-90)
- Removal of potentially dangerous characters

**Example**:
```python
@router.get("/", response_model=List[ScheduleResponse])
@router.get("", response_model=List[ScheduleResponse])
async def list_schedules(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = None,
    current_user: dict = Security(get_viewer_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> List[ScheduleResponse]:
    from infrastructure.api.query_validation import validate_query_param
    
    # Set default end date to today
    current_end_date = datetime.now()
    
    # Validate and parse the end_date if provided
    if end_date:
        try:
            # Sanitize the end_date parameter
            sanitized_end_date = validate_query_param(
                end_date, 
                "end_date", 
                required=False, 
                pattern=r'^\d{4}-\d{2}-\d{2}$'
            )
            current_end_date = datetime.fromisoformat(sanitized_end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid end_date format. Use YYYY-MM-DD."
            )
    
    # Validate and parse the days parameter if provided
    days_value = 7  # Default
    if days:
        try:
            # Sanitize and convert to integer
            sanitized_days = validate_query_param(days, "days", required=False)
            days_value = int(sanitized_days)
            if days_value < 1 or days_value > 90:
                raise ValueError("Days must be between 1 and 90")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
    
    # Calculate the start date based on end_date and days if start_date not provided
    current_start_date = current_end_date - timedelta(days=days_value)
    
    # Validate and parse the start_date if provided
    if start_date:
        try:
            # Sanitize the start_date parameter
            sanitized_start_date = validate_query_param(
                start_date, 
                "start_date", 
                required=False, 
                pattern=r'^\d{4}-\d{2}-\d{2}$'
            )
            current_start_date = datetime.fromisoformat(sanitized_start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid start_date format. Use YYYY-MM-DD."
            )
    
    # Get schedules for the specified date range
    schedules = schedule_service.schedule_repository.get_by_date_range(current_start_date, current_end_date)
    return [map_schedule_to_response(schedule) for schedule in schedules]
```

## Validation Utilities Created

We've created a comprehensive set of validation utilities in `infrastructure/api/query_validation.py`:

1. `sanitize_string`: Removes potentially dangerous characters from strings
2. `validate_email`: Validates and sanitizes email addresses
3. `validate_password`: Validates and sanitizes passwords
4. `validate_query_param`: Generic function for validating and sanitizing query parameters
5. `PaginationQueryParams`: Pydantic model for pagination parameters
6. `SearchQueryParams`: Pydantic model for search parameters

## Tests Added

We've added comprehensive tests in `tests/unit/test_query_validation.py` to verify that our validation utilities work correctly:

1. Basic functionality tests for each validation function
2. Tests for handling dangerous characters
3. Tests for required parameter validation
4. Tests for parameter length and format validation
5. Tests for custom validation logic
6. Tests for Pydantic model validation
7. Tests for XSS injection attempts with common payloads
8. Tests for SQL injection attempts with common payloads

## Documentation Created

We've created a comprehensive guide for query parameter security in `docs/query_parameter_security.md` that explains:

1. Why middleware can't sanitize query parameters
2. Our validation and sanitization approach
3. How to use the query validation utilities
4. Examples of updating endpoints
5. Best practices for query parameter security
6. Testing approach

## Conclusion

By implementing validation and sanitization at the endpoint handler level, we've hardened the Scheduler API against query parameter injection attacks. The validation utilities we've created provide a consistent and secure way to handle query parameters across the API.