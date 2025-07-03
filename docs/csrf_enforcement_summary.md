# CSRF Enforcement Summary

## Objective
Ensure all state-changing endpoints (POST, PUT, PATCH, DELETE) require and validate the `X-CSRF-Token` header.

## Implementation
CSRF protection is implemented using a double-submit cookie pattern:
1. Client requests a CSRF token from `/api/v1/csrf-token` endpoint
2. Server sets a CSRF token cookie
3. Client includes the same token in the `X-CSRF-Token` header for state-changing requests
4. Server verifies that the token in the header matches the one in the cookie

## Affected Endpoints

| Endpoint | Method | Before | After | Status |
|----------|--------|--------|-------|--------|
| `/api/v1/auth/token` | POST | Protected | Protected | ✅ |
| `/api/v1/auth/register` | POST | Protected | Protected | ✅ (Deprecated) |
| `/api/v1/auth/refresh` | POST | Protected | Protected | ✅ |
| `/api/v1/users/register` | POST | Protected | Protected | ✅ |
| `/api/v1/users/verify-email/{token}` | POST | Unprotected | Protected | ✅ |
| `/api/v1/users/request-password-reset` | POST | Unprotected | Protected | ✅ |
| `/api/v1/users/reset-password/{token}` | POST | Unprotected | Protected | ✅ |
| `/api/v1/schedules` | POST | Protected | Protected | ✅ |
| `/api/v1/schedules/{schedule_id}/publish` | POST | Protected | Protected | ✅ |
| `/api/v1/schedules/{schedule_id}/assignments/{assignment_id}/status` | POST | Protected | Protected | ✅ |

## Example Code

### Backend: Adding CSRF Protection to an Endpoint
```python
from infrastructure.api.dependencies_csrf import csrf_protection

@router.post("/endpoint", dependencies=[csrf_protection])
async def create_resource(...):
    # Endpoint implementation
    ...
```

### Frontend: Including CSRF Token in Requests
```typescript
// Get CSRF token first
await api.get('/api/v1/csrf-token');
// The token is automatically set as a cookie by the server

// Then make state-changing requests
// The token is automatically included in the header by the interceptor
const response = await api.post('/api/v1/users/register', userData);
```

## Error Response for Missing/Invalid CSRF Token
```json
{
  "status_code": 403,
  "message": "Forbidden",
  "details": "Missing CSRF token"
}
```

or

```json
{
  "status_code": 403,
  "message": "Forbidden",
  "details": "CSRF token mismatch"
}
```

or

```json
{
  "status_code": 403,
  "message": "Forbidden",
  "details": "Invalid CSRF token"
}
```

## Documentation Updates
- Added CSRF protection section to API documentation
- Added CSRF token security scheme to OpenAPI schema
- Updated global security requirements to include CSRF token

## Testing
All tests for state-changing endpoints include CSRF tokens in their requests, ensuring that the CSRF protection is properly tested.