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
- 404: Resource not found
- 500: Internal server error

## Error Response Format
```json
{
  "error": "Error message",
  "detail": "Detailed description",
  "status": 400
}
```

## Success Response Format
- Always return JSON
- Use consistent field naming (camelCase)
- Include relevant data in response body
- POST should return created resource
- GET should return resource or array of resources
