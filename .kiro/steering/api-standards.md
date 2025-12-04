---
fileMatchPattern: "**/*{api,route,endpoint,handler}*.{py,js,ts}"
---

# API Standards

## HTTP Methods
- GET: Retrieve resources (200 OK, 404 Not Found)
- POST: Create resources (201 Created with Location header)
- PUT: Full update (200 OK or 204 No Content)
- PATCH: Partial update (200 OK or 204 No Content)
- DELETE: Remove resources (204 No Content)

## Status Codes
- 200: Success with response body
- 201: Resource created (include resource in body)
- 204: Success without response body
- 400: Bad request (validation errors)
- 401: Unauthorized (missing or invalid authentication)
- 403: Forbidden (insufficient permissions)
- 404: Resource not found
- 429: Too many requests (rate limit exceeded)
- 500: Internal server error

## Authentication & Authorization
- Use Bearer token authentication: `Authorization: Bearer <token>`
- Include authentication header in all protected endpoints
- Implement role-based access control (RBAC) for resource permissions
- Return 401 for missing/invalid tokens, 403 for insufficient permissions

## Request Headers
- `Content-Type: application/json` for request body
- `Accept: application/json` for response format
- `Authorization: Bearer <token>` for authenticated requests

## Response Headers
- `Content-Type: application/json`
- `X-RateLimit-Limit`: Total requests allowed per window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Timestamp when limit resets

## Error Response Format
Single error:
```json
{
  "error": "Validation failed",
  "detail": "Invalid input data",
  "status": 400
}
```

Multiple validation errors:
```json
{
  "error": "Validation failed",
  "errors": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "date", "message": "Date must be in future"}
  ],
  "status": 400
}
```

## Success Response Format
- Always return JSON with `Content-Type: application/json`
- Use camelCase for field names
- Use ISO 8601 format for timestamps (e.g., "2025-12-04T02:22:53Z")
- POST should return created resource with 201 status
- GET should return resource or array of resources

## Pagination & Filtering
List endpoints must support:
- `?page=1&limit=10` for pagination (default limit: 20, max: 100)
- `?sort=fieldName` or `?sort=-fieldName` for sorting (- prefix for descending)
- `?filter[status]=active` for filtering by field values

Response format for paginated lists:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "totalPages": 5
  }
}
```

## API Versioning
- Use URL path versioning: `/v1/events`, `/v2/events`
- Maintain backward compatibility within major versions
- Deprecate old versions with 6-month notice

## Rate Limiting
- Implement rate limiting per API key/user
- Standard limit: 1000 requests per hour
- Return 429 status with `Retry-After` header when exceeded

## Practical Examples

### Create Event
```
POST /v1/events
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "title": "AWS re:Invent 2025",
  "description": "Annual AWS conference",
  "date": "2025-12-01T09:00:00Z",
  "location": "Las Vegas, NV",
  "capacity": 50000,
  "organizer": "AWS",
  "status": "active"
}

Response: 201 Created
{
  "eventId": "evt_123",
  "title": "AWS re:Invent 2025",
  "description": "Annual AWS conference",
  "date": "2025-12-01T09:00:00Z",
  "location": "Las Vegas, NV",
  "capacity": 50000,
  "organizer": "AWS",
  "status": "active",
  "createdAt": "2025-12-04T02:22:53Z"
}
```

### Get Event
```
GET /v1/events/evt_123
Authorization: Bearer eyJhbGc...

Response: 200 OK
{
  "eventId": "evt_123",
  "title": "AWS re:Invent 2025",
  "date": "2025-12-01T09:00:00Z",
  "status": "active"
}
```

### Update Event
```
PATCH /v1/events/evt_123
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "status": "cancelled"
}

Response: 200 OK
{
  "eventId": "evt_123",
  "status": "cancelled",
  "updatedAt": "2025-12-04T02:22:53Z"
}
```

### List Events with Filtering
```
GET /v1/events?status=active&page=1&limit=10&sort=-date
Authorization: Bearer eyJhbGc...

Response: 200 OK
{
  "data": [
    {"eventId": "evt_123", "title": "AWS re:Invent 2025", "status": "active"}
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1,
    "totalPages": 1
  }
}
```
