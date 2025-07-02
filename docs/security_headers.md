# Security Headers in the Scheduler Application

This document explains the security headers used in the Scheduler application and the rationale behind their implementation.

## Overview

The Scheduler application uses a `SecurityHeadersMiddleware` to add security headers to all HTTP responses. These headers help protect against various web security vulnerabilities, such as Cross-Site Scripting (XSS), clickjacking, and MIME type sniffing.

## Implemented Security Headers

### Content-Security-Policy (CSP)

**Purpose**: Controls which resources can be loaded by the browser and from where.

**Implementation**:
```
default-src 'self';
script-src 'self';
style-src 'self';
img-src 'self' data:;
font-src 'self';
connect-src 'self' http://localhost:5175 http://localhost:5176;
frame-src 'none';
object-src 'none';
base-uri 'self';
form-action 'self'
```

**Benefits**:
- Prevents XSS attacks by controlling which scripts can be executed
- Restricts loading of resources to trusted sources
- Provides a defense-in-depth approach to security

### Strict-Transport-Security (HSTS)

**Purpose**: Forces browsers to use HTTPS instead of HTTP.

**Implementation**:
```
max-age=31536000; includeSubDomains
```

**Benefits**:
- Prevents man-in-the-middle attacks
- Protects against protocol downgrade attacks
- Ensures all communication is encrypted

### X-Frame-Options

**Purpose**: Prevents clickjacking attacks by controlling whether a page can be embedded in an iframe.

**Implementation**:
```
DENY
```

**Benefits**:
- Prevents attackers from embedding your site in a malicious frame
- Protects against UI redressing attacks

### Referrer-Policy

**Purpose**: Controls how much referrer information is included with requests.

**Implementation**:
```
no-referrer-when-downgrade
```

**Benefits**:
- Protects user privacy by limiting referrer information
- Prevents leaking sensitive information in the referrer header

### Permissions-Policy

**Purpose**: Controls which browser features and APIs can be used.

**Implementation**:
```
geolocation='none'; camera='none'; microphone='none'
```

**Benefits**:
- Restricts access to sensitive browser features
- Prevents abuse of browser APIs

### X-Content-Type-Options

**Purpose**: Prevents MIME type sniffing.

**Implementation**:
```
nosniff
```

**Benefits**:
- Prevents browsers from interpreting files as a different MIME type
- Mitigates MIME confusion attacks

## Why X-XSS-Protection is Not Included

The `X-XSS-Protection` header is intentionally not included in our security headers for the following reasons:

1. **Deprecated in Modern Browsers**: This header is largely deprecated in modern browsers. Chrome, Edge (Chromium-based), and Firefox no longer support it.

2. **Content Security Policy is Superior**: CSP provides a more robust and comprehensive protection against XSS attacks. It allows for fine-grained control over which scripts can be executed and from where.

3. **Potential Security Issues**: In some cases, the built-in XSS auditor controlled by this header can be bypassed or even exploited to enable XSS attacks rather than prevent them.

4. **Industry Best Practices**: Current security best practices recommend using CSP instead of relying on the X-XSS-Protection header.

## Implementation Details

The security headers are implemented using the `secure` Python package, which provides a clean API for defining security policies. The headers are applied to all responses by the `SecurityHeadersMiddleware` in `infrastructure/api/security.py`.

## Testing

The security headers are tested in `tests/unit/test_security_headers_middleware.py`. The tests verify that:

1. All expected security headers are present in responses
2. The X-XSS-Protection header is not included
3. The security headers have the expected values

## References

- [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [HTTP Strict Transport Security (HSTS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)
- [X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options)
- [Referrer-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy)
- [Permissions Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Feature-Policy)
- [X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options)
- [X-XSS-Protection (Deprecated)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection)