from secure import Secure
from secure.headers import (
    ContentSecurityPolicy, StrictTransportSecurity, XFrameOptions,
    ReferrerPolicy, PermissionsPolicy, XContentTypeOptions
)
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


# Define security policies
csp = ContentSecurityPolicy().default_src("'self'").script_src("'self'").style_src("'self'").img_src("'self'", "data:").font_src("'self'").connect_src("'self'", "http://localhost:5175", "http://localhost:5176", "http://localhost:5178").frame_src("'none'").object_src("'none'").base_uri("'self'").form_action("'self'")
hsts = StrictTransportSecurity().max_age(31536000).include_subdomains()
xfo = XFrameOptions().deny()
referrer = ReferrerPolicy().no_referrer_when_downgrade()
permissions = PermissionsPolicy().geolocation("'none'").camera("'none'").microphone("'none'")
content_type = XContentTypeOptions().nosniff()

# Compose the secure config object
secure_headers = Secure(
    csp=csp,
    hsts=hsts,
    xfo=xfo,
    referrer=referrer,
    permissions=permissions,
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all responses.

    Applied security headers:
    - Content-Security-Policy: Controls which resources can be loaded
    - Strict-Transport-Security: Forces HTTPS connections
    - X-Frame-Options: Prevents clickjacking attacks
    - Referrer-Policy: Controls how much referrer information is included
    - Permissions-Policy: Controls which browser features can be used
    - X-Content-Type-Options: Prevents MIME type sniffing

    Note: X-XSS-Protection header is intentionally not included as it is deprecated
    in modern browsers. Content Security Policy (CSP) provides more robust protection
    against XSS attacks.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Manually apply each header
        headers = secure_headers.headers
        for k, v in headers.items():
            response.headers[k] = v

        return response
