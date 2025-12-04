# User Registration Feature Specification

## Overview
Enable users to register for events with capacity management and waitlist support.

## Functional Requirements

### 1. User Management
- Users can be created with basic information:
  - `userId`: Unique identifier (string)
  - `name`: User's full name (string)
- User data persisted in DynamoDB

### 2. Event Capacity Configuration
- Events must support capacity constraints:
  - `capacity`: Maximum number of registered users (integer)
  - `waitlistEnabled`: Boolean flag to enable/disable waitlist (optional, default: false)
  - `currentRegistrations`: Current count of registered users
  - `waitlistCount`: Current count of users on waitlist

### 3. Event Registration
- Users can register for events via POST endpoint
- Registration logic:
  - If `currentRegistrations < capacity`: Register user successfully
  - If `currentRegistrations >= capacity` and `waitlistEnabled = false`: Deny registration (403 Forbidden)
  - If `currentRegistrations >= capacity` and `waitlistEnabled = true`: Add user to waitlist
- Prevent duplicate registrations (same user cannot register twice)

### 4. Event Unregistration
- Users can unregister from events via DELETE endpoint
- Unregistration logic:
  - Remove user from registered list
  - If waitlist exists and has users, automatically promote first waitlist user to registered
  - Decrement registration count appropriately

### 5. User Event Listing
- Users can retrieve list of events they are registered to
- Endpoint: GET /users/{userId}/events
- Response includes registration status (registered or waitlisted)

## API Endpoints

### Create User
```
POST /v1/users
{
  "userId": "user_123",
  "name": "John Doe"
}
Response: 201 Created
```

### Register for Event
```
POST /v1/events/{eventId}/registrations
{
  "userId": "user_123"
}
Response: 201 Created (registered) or 200 OK (waitlisted) or 403 Forbidden (full, no waitlist)
```

### Unregister from Event
```
DELETE /v1/events/{eventId}/registrations/{userId}
Response: 204 No Content
```

### List User's Events
```
GET /v1/users/{userId}/events
Response: 200 OK
{
  "events": [
    {
      "eventId": "evt_123",
      "title": "AWS re:Invent 2025",
      "registrationStatus": "registered"
    }
  ]
}
```

## Data Models

### User
```json
{
  "userId": "user_123",
  "name": "John Doe",
  "createdAt": "2025-12-04T02:23:57Z"
}
```

### Event (Extended)
```json
{
  "eventId": "evt_123",
  "title": "AWS re:Invent 2025",
  "capacity": 100,
  "waitlistEnabled": true,
  "currentRegistrations": 95,
  "waitlistCount": 5
}
```

### Registration
```json
{
  "registrationId": "reg_123",
  "eventId": "evt_123",
  "userId": "user_123",
  "status": "registered",
  "registeredAt": "2025-12-04T02:23:57Z"
}
```

## Business Rules
1. Users must exist before registering for events
2. Events must exist before accepting registrations
3. Capacity must be a positive integer
4. Waitlist promotion is automatic and follows FIFO order
5. Users cannot register for the same event twice
6. Unregistering from waitlist does not promote other users
