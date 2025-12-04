# User Registration Implementation Tasks

## Task 1: Database Schema Updates
- [ ] Add capacity, waitlistEnabled, currentRegistrations, waitlistCount to Events table
- [ ] Create Users DynamoDB table with userId as partition key
- [ ] Create Registrations DynamoDB table with eventId as PK and userId as SK
- [ ] Create GSI on Registrations table (UserIdIndex) for querying by userId
- [ ] Update CDK infrastructure code

## Task 2: User Management Endpoints
- [ ] Implement POST /v1/users endpoint to create users
- [ ] Implement GET /v1/users/{userId} endpoint to retrieve user details
- [ ] Add Pydantic models for User validation
- [ ] Add DynamoDB operations for user CRUD

## Task 3: Registration Logic
- [ ] Implement POST /v1/events/{eventId}/registrations endpoint
- [ ] Add validation for user and event existence
- [ ] Add duplicate registration check
- [ ] Implement capacity checking logic
- [ ] Implement waitlist logic when event is full
- [ ] Add Pydantic models for Registration validation
- [ ] Update event counters (currentRegistrations, waitlistCount)

## Task 4: Unregistration Logic
- [ ] Implement DELETE /v1/events/{eventId}/registrations/{userId} endpoint
- [ ] Add logic to remove registration
- [ ] Implement automatic waitlist promotion
- [ ] Update event counters appropriately
- [ ] Handle waitlist position reordering

## Task 5: User Events Listing
- [ ] Implement GET /v1/users/{userId}/events endpoint
- [ ] Query registrations using UserIdIndex GSI
- [ ] Join with events data to return full event details
- [ ] Include registration status in response

## Task 6: Error Handling
- [ ] Add 404 handling for non-existent users/events
- [ ] Add 409 handling for duplicate registrations
- [ ] Add 403 handling for full events without waitlist
- [ ] Add validation error handling with detailed messages

## Task 7: Testing
- [ ] Test user creation
- [ ] Test registration when capacity available
- [ ] Test registration when event full with waitlist
- [ ] Test registration denial when event full without waitlist
- [ ] Test duplicate registration prevention
- [ ] Test unregistration with waitlist promotion
- [ ] Test user events listing

## Task 8: Deployment
- [ ] Deploy updated CDK stack with new tables
- [ ] Deploy updated Lambda function
- [ ] Verify all endpoints are accessible
- [ ] Test end-to-end flows in deployed environment
