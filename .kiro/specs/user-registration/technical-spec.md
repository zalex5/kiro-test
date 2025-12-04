# User Registration Technical Specification

## Database Schema

### DynamoDB Tables

#### Users Table
- **Table Name**: `Users`
- **Partition Key**: `userId` (String)
- **Attributes**:
  - `userId`: String
  - `name`: String
  - `createdAt`: String (ISO 8601)

#### Registrations Table
- **Table Name**: `Registrations`
- **Partition Key**: `eventId` (String)
- **Sort Key**: `userId` (String)
- **Attributes**:
  - `registrationId`: String
  - `eventId`: String
  - `userId`: String
  - `status`: String (enum: "registered", "waitlisted")
  - `registeredAt`: String (ISO 8601)
  - `position`: Number (for waitlist ordering)
- **GSI**: `UserIdIndex`
  - Partition Key: `userId`
  - Sort Key: `eventId`
  - Purpose: Query all events for a specific user

#### Events Table (Extended)
- Add new attributes to existing Events table:
  - `capacity`: Number
  - `waitlistEnabled`: Boolean
  - `currentRegistrations`: Number
  - `waitlistCount`: Number

## API Implementation

### Endpoints to Add
1. `POST /v1/users` - Create user
2. `GET /v1/users/{userId}` - Get user details
3. `POST /v1/events/{eventId}/registrations` - Register for event
4. `DELETE /v1/events/{eventId}/registrations/{userId}` - Unregister from event
5. `GET /v1/users/{userId}/events` - List user's registered events
6. `GET /v1/events/{eventId}/registrations` - List event registrations

### Registration Logic Flow
```
1. Validate user exists
2. Validate event exists
3. Check for duplicate registration
4. If currentRegistrations < capacity:
   - Create registration with status="registered"
   - Increment currentRegistrations
   - Return 201 Created
5. Else if waitlistEnabled:
   - Create registration with status="waitlisted"
   - Set position = current waitlistCount + 1
   - Increment waitlistCount
   - Return 200 OK with waitlist position
6. Else:
   - Return 403 Forbidden
```

### Unregistration Logic Flow
```
1. Validate registration exists
2. Get registration status
3. Delete registration record
4. If status == "registered":
   - Decrement currentRegistrations
   - Query first waitlisted user (lowest position)
   - If waitlist user exists:
     - Update their status to "registered"
     - Increment currentRegistrations
     - Decrement waitlistCount
5. Else if status == "waitlisted":
   - Decrement waitlistCount
6. Return 204 No Content
```

## Error Handling
- 400: Invalid request data
- 403: Event full, no waitlist available
- 404: User or event not found
- 409: User already registered for event

## Testing Scenarios
1. Register user when event has capacity
2. Register user when event is full with waitlist enabled
3. Deny registration when event is full without waitlist
4. Prevent duplicate registrations
5. Automatic waitlist promotion on unregistration
6. List user's registered and waitlisted events
