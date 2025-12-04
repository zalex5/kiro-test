# User Registration Design

## Architecture

### Database Design

#### Users Table
- Partition Key: `userId`
- Attributes: `userId`, `name`, `createdAt`

#### Registrations Table
- Partition Key: `eventId`
- Sort Key: `userId`
- Attributes: `registrationId`, `eventId`, `userId`, `status`, `registeredAt`, `position`
- GSI: `UserIdIndex` (PK: `userId`, SK: `eventId`) for querying user's events

#### Events Table (Extended)
- Add attributes: `capacity`, `waitlistEnabled`, `currentRegistrations`, `waitlistCount`

## API Design

### Endpoints

**POST /v1/users**
- Create new user
- Request: `{"userId": "user_123", "name": "John Doe"}`
- Response: 201 Created

**POST /v1/events/{eventId}/registrations**
- Register user for event
- Request: `{"userId": "user_123"}`
- Response: 201 (registered), 200 (waitlisted), 403 (denied)

**DELETE /v1/events/{eventId}/registrations/{userId}**
- Unregister user from event
- Response: 204 No Content

**GET /v1/users/{userId}/events**
- List user's registered events
- Response: 200 OK with events array

## Registration Flow

```
1. Validate user exists
2. Validate event exists
3. Check for duplicate registration
4. Get current event capacity status
5. If capacity available:
   - Create registration (status="registered")
   - Increment currentRegistrations
6. Else if waitlist enabled:
   - Create registration (status="waitlisted")
   - Set position = waitlistCount + 1
   - Increment waitlistCount
7. Else:
   - Return 403 Forbidden
```

## Unregistration Flow

```
1. Get registration record
2. Delete registration
3. If status was "registered":
   - Decrement currentRegistrations
   - Query first waitlisted user (position=1)
   - If found:
     - Update status to "registered"
     - Increment currentRegistrations
     - Decrement waitlistCount
     - Reorder remaining waitlist positions
4. Else if status was "waitlisted":
   - Decrement waitlistCount
   - Reorder remaining waitlist positions
```

## Data Models

### User
```json
{
  "userId": "user_123",
  "name": "John Doe",
  "createdAt": "2025-12-04T02:25:21Z"
}
```

### Registration
```json
{
  "registrationId": "reg_123",
  "eventId": "evt_123",
  "userId": "user_123",
  "status": "registered",
  "registeredAt": "2025-12-04T02:25:21Z",
  "position": null
}
```

### Event (Extended)
```json
{
  "eventId": "evt_123",
  "capacity": 100,
  "waitlistEnabled": true,
  "currentRegistrations": 95,
  "waitlistCount": 5
}
```
