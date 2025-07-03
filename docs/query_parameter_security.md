# Query Parameter Security Guide

## Overview

This guide explains how to securely handle query parameters in FastAPI endpoints. Query parameters are particularly vulnerable to injection attacks because middleware cannot mutate them directly. This document outlines the approach to validate and sanitize query parameters at the endpoint handler level.

## Why Middleware Can't Sanitize Query Parameters

In FastAPI, middleware can intercept requests and responses, but it has limitations when it comes to query parameters:

1. **Immutability**: The `request.query_params` object is immutable, so middleware cannot modify it directly.
2. **Early Binding**: Query parameters are parsed and bound to endpoint function parameters before middleware can create a new request object.
3. **Type Conversion**: FastAPI performs type conversion based on function signatures, which happens after middleware processing.

This means that sanitization must happen at the endpoint handler level, where we have direct access to the parameter values.

## Validation and Sanitization Approach

We've implemented a comprehensive approach to query parameter validation and sanitization:

1. **Explicit Validation**: Each query parameter is explicitly validated at the endpoint handler level.
2. **Character Sanitization**: Potentially dangerous characters (`<`, `>`, `'`, `"`, `;`, etc.) are removed or escaped.
3. **Type Checking**: Parameters are validated against their expected types.
4. **Format Validation**: Parameters are checked against expected formats (e.g., email addresses, dates).
5. **Clear Error Messages**: Invalid input results in a `422 Unprocessable Entity` response with a clear error message.

## Using the Query Validation Utilities

### Basic String Sanitization

```python
from infrastructure.api.query_validation import sanitize_string

# Remove dangerous characters from a string
sanitized_value = sanitize_string(value)
```

### Validating Common Parameter Types

```python
from infrastructure.api.query_validation import validate_email, validate_password

# Validate and sanitize an email address
sanitized_email = validate_email(email)

# Validate and sanitize a password
sanitized_password = validate_password(password, min_length=8)
```

### Generic Parameter Validation

```python
from infrastructure.api.query_validation import validate_query_param

# Validate a required parameter
sanitized_param = validate_query_param(param, "parameter_name")

# Validate an optional parameter
sanitized_param = validate_query_param(param, "parameter_name", required=False)

# Validate with length constraints
sanitized_param = validate_query_param(param, "parameter_name", min_length=3, max_length=50)

# Validate with a regex pattern
sanitized_param = validate_query_param(param, "parameter_name", pattern=r'^[a-zA-Z0-9]+$')

# Validate with a custom validator function
def custom_validator(value):
    if not value.startswith("valid_"):
        raise ValueError("Value must start with 'valid_'")
    return value

sanitized_param = validate_query_param(param, "parameter_name", custom_validator=custom_validator)
```

### Using Pydantic Models for Complex Validation

```python
from fastapi import Depends
from infrastructure.api.query_validation import PaginationQueryParams, SearchQueryParams

@router.get("/items")
async def list_items(
    pagination: PaginationQueryParams = Depends(),
    search: SearchQueryParams = Depends()
):
    # Access validated and sanitized parameters
    page = pagination.page
    size = pagination.size
    sort_by = pagination.sort_by
    search_query = search.q
    search_fields = search.fields
    
    # Use the parameters to query the database
    # ...
```

## Example: Updating an Endpoint

### Before

```python
@router.get("/users")
async def list_users(
    search: str = None,
    page: int = 1,
    size: int = 50
):
    # No validation or sanitization
    # Vulnerable to injection attacks
    # ...
```

### After

```python
@router.get("/users")
async def list_users(
    search: str = None,
    page: int = 1,
    size: int = 50
):
    from infrastructure.api.query_validation import validate_query_param
    
    # Validate and sanitize the search parameter
    sanitized_search = validate_query_param(search, "search", required=False)
    
    # Validate page and size
    try:
        sanitized_page = int(validate_query_param(str(page), "page", required=False, pattern=r'^\d+$'))
        if sanitized_page < 1:
            raise ValueError("Page must be at least 1")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    try:
        sanitized_size = int(validate_query_param(str(size), "size", required=False, pattern=r'^\d+$'))
        if sanitized_size < 1 or sanitized_size > 100:
            raise ValueError("Size must be between 1 and 100")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    # Use the sanitized parameters
    # ...
```

## Best Practices

1. **Always Validate**: Never trust user input. Always validate and sanitize query parameters.
2. **Use Type Hints**: FastAPI uses type hints for basic validation. Use them as a first line of defense.
3. **Be Explicit**: Explicitly validate each parameter at the endpoint handler level.
4. **Sanitize Before Use**: Sanitize parameters before using them in database queries or other operations.
5. **Return Clear Errors**: Return clear error messages when validation fails.
6. **Test Thoroughly**: Test your validation with normal input, edge cases, and attack patterns.

## Testing

We've implemented comprehensive tests for our query parameter validation utilities:

1. **Unit Tests**: Test each validation function with normal input, edge cases, and attack patterns.
2. **Integration Tests**: Test endpoints with valid and invalid query parameters.
3. **Security Tests**: Test with common XSS and SQL injection payloads.

Run the tests with:

```bash
pytest tests/unit/test_query_validation.py
```

## Conclusion

By following this guide, you can ensure that your FastAPI endpoints are protected against query parameter injection attacks. Remember that middleware cannot sanitize query parameters, so validation and sanitization must happen at the endpoint handler level.