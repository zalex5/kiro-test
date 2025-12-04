# Event Management API

A serverless REST API for managing events, built with FastAPI and deployed on AWS using Lambda and API Gateway.

## Project Structure

```
.
├── backend/           # FastAPI application code
├── infrastructure/    # AWS CDK infrastructure code
├── .kiro/            # Kiro workspace configuration
│   └── settings/
│       └── mcp.json  # MCP server configuration
└── README.md
```

## API Endpoint

**Base URL:** `https://my4s8zht11.execute-api.us-west-2.amazonaws.com/prod/`

## Features

- ✅ Full CRUD operations for events
- ✅ Query filtering by status
- ✅ Custom event IDs support
- ✅ Partial updates
- ✅ Input validation with Pydantic
- ✅ CORS enabled for web access
- ✅ Serverless architecture (Lambda + API Gateway)
- ✅ DynamoDB for data persistence

## Event Schema

```json
{
  "eventId": "string (optional, auto-generated if not provided)",
  "title": "string (required, min 1 char)",
  "description": "string (required, min 1 char)",
  "date": "string (required, ISO format)",
  "location": "string (required, min 1 char)",
  "capacity": "integer (required, > 0)",
  "organizer": "string (required, min 1 char)",
  "status": "string (required)"
}
```

## API Endpoints

### Health Check
```bash
GET /
```

### Create Event
```bash
POST /events
Content-Type: application/json

{
  "eventId": "my-event-123",  # Optional
  "title": "AWS re:Invent 2025",
  "description": "Annual AWS conference",
  "date": "2025-12-01T09:00:00Z",
  "location": "Las Vegas, NV",
  "capacity": 50000,
  "organizer": "Amazon Web Services",
  "status": "active"
}

# Returns: 201 Created
```

### List All Events
```bash
GET /events

# Returns: 200 OK
```

### List Events by Status
```bash
GET /events?status=active

# Returns: 200 OK
```

### Get Single Event
```bash
GET /events/{eventId}

# Returns: 200 OK or 404 Not Found
```

### Update Event (Partial)
```bash
PUT /events/{eventId}
Content-Type: application/json

{
  "title": "Updated Title",
  "capacity": 60000
}

# Returns: 200 OK or 404 Not Found
```

### Delete Event
```bash
DELETE /events/{eventId}

# Returns: 204 No Content or 404 Not Found
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js (for AWS CDK)
- AWS CLI configured with credentials
- AWS CDK CLI: `npm install -g aws-cdk`

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Infrastructure Setup

```bash
cd infrastructure
pip install -r requirements.txt
```

### Deploy to AWS

```bash
cd infrastructure
cdk bootstrap  # First time only
cdk deploy
```

The deployment will output your API Gateway endpoint URL.

## Local Development

The backend uses FastAPI with Mangum adapter for AWS Lambda compatibility.

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Run Tests
```bash
# Test the deployed API
curl https://my4s8zht11.execute-api.us-west-2.amazonaws.com/prod/events
```

## Infrastructure

- **Runtime**: Python 3.12
- **Framework**: FastAPI with Mangum
- **Database**: DynamoDB (pay-per-request)
- **API**: API Gateway REST API
- **Compute**: AWS Lambda
- **IaC**: AWS CDK (Python)

## Environment Variables

The Lambda function uses:
- `TABLE_NAME`: DynamoDB table name (set automatically by CDK)

## Documentation

API documentation is available in `backend/docs/` (generated with pdoc).

## MCP Configuration

This project uses Kiro with the following MCP servers:
- AWS Knowledge MCP Server
- AWS Frontend MCP Server
- AWS CDK MCP Server
- Brave Search
- Fetch
- Context7

Configuration: `.kiro/settings/mcp.json`

## License

MIT
