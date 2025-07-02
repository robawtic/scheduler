from fastapi import Request, Response, HTTPException
from itsdangerous import URLSafeTimedSerializer, BadSignature
from starlette.status import HTTP_403_FORBIDDEN
from infrastructure.config.settings import settings

CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "x-csrf-token"

_signer = URLSafeTimedSerializer(secret_key=settings.secret_key)


def generate_csrf_token() -> str:
    return _signer.dumps("csrf")


def set_csrf_cookie(response: Response) -> None:
    token = generate_csrf_token()
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,
        secure=settings.cookie_secure,  # Use the setting from config
        samesite="lax",  # Less restrictive for development
        max_age=3600,
    )


def verify_csrf_token(request: Request):
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get(CSRF_HEADER_NAME)

    if not cookie_token or not header_token:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Missing CSRF token")

    if cookie_token != header_token:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="CSRF token mismatch")

    try:
        _signer.loads(cookie_token, max_age=3600)
    except BadSignature:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid CSRF token")


def setup_csrf(app):
    """
    Configure CSRF protection for the application.

    Note: This function is kept for backward compatibility but no longer adds middleware.
    CSRF protection is now handled through dependencies and token validation.
    """
    pass
