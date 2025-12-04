from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import boto3
import os
import uuid
from mangum import Mangum

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'events')
users_table_name = os.environ.get('USERS_TABLE_NAME', 'users')
registrations_table_name = os.environ.get('REGISTRATIONS_TABLE_NAME', 'registrations')

table = dynamodb.Table(table_name)
users_table = dynamodb.Table(users_table_name)
registrations_table = dynamodb.Table(registrations_table_name)

class Event(BaseModel):
    eventId: Optional[str] = None
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    date: str
    location: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)
    organizer: str = Field(..., min_length=1)
    status: str
    waitlistEnabled: Optional[bool] = False
    currentRegistrations: Optional[int] = 0
    waitlistCount: Optional[int] = 0

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    organizer: Optional[str] = None
    status: Optional[str] = None
    waitlistEnabled: Optional[bool] = None

class User(BaseModel):
    userId: str
    name: str

class Registration(BaseModel):
    userId: str

@app.get("/")
def root():
    return {"message": "Event Management API"}

@app.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(event: Event):
    try:
        event_id = event.eventId if event.eventId else str(uuid.uuid4())
        item = {
            'eventId': event_id,
            'title': event.title,
            'description': event.description,
            'date': event.date,
            'location': event.location,
            'capacity': event.capacity,
            'organizer': event.organizer,
            'status': event.status,
            'waitlistEnabled': event.waitlistEnabled,
            'currentRegistrations': event.currentRegistrations,
            'waitlistCount': event.waitlistCount
        }
        table.put_item(Item=item)
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events")
def list_events(status: Optional[str] = Query(None)):
    try:
        response = table.scan()
        items = response.get('Items', [])
        if status:
            items = [item for item in items if item.get('status') == status]
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}")
def get_event(event_id: str):
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        return response['Item']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/events/{event_id}")
def update_event(event_id: str, event: EventUpdate):
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        existing = response['Item']
        if event.title is not None:
            existing['title'] = event.title
        if event.description is not None:
            existing['description'] = event.description
        if event.date is not None:
            existing['date'] = event.date
        if event.location is not None:
            existing['location'] = event.location
        if event.capacity is not None:
            existing['capacity'] = event.capacity
        if event.organizer is not None:
            existing['organizer'] = event.organizer
        if event.status is not None:
            existing['status'] = event.status
        if event.waitlistEnabled is not None:
            existing['waitlistEnabled'] = event.waitlistEnabled
        
        table.put_item(Item=existing)
        return existing
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: str):
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        table.delete_item(Key={'eventId': event_id})
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    try:
        response = users_table.get_item(Key={'userId': user.userId})
        if 'Item' in response:
            raise HTTPException(status_code=409, detail="User already exists")
        
        item = {
            'userId': user.userId,
            'name': user.name,
            'createdAt': datetime.utcnow().isoformat() + 'Z'
        }
        users_table.put_item(Item=item)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}")
def get_user(user_id: str):
    try:
        response = users_table.get_item(Key={'userId': user_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="User not found")
        return response['Item']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/{event_id}/registrations")
def register_for_event(event_id: str, registration: Registration):
    try:
        user_response = users_table.get_item(Key={'userId': registration.userId})
        if 'Item' not in user_response:
            raise HTTPException(status_code=404, detail="User not found")
        
        event_response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in event_response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        event = event_response['Item']
        
        reg_response = registrations_table.get_item(Key={'eventId': event_id, 'userId': registration.userId})
        if 'Item' in reg_response:
            raise HTTPException(status_code=409, detail="User already registered for this event")
        
        current_regs = event.get('currentRegistrations', 0)
        capacity = event.get('capacity', 0)
        waitlist_enabled = event.get('waitlistEnabled', False)
        
        if current_regs < capacity:
            reg_item = {
                'registrationId': str(uuid.uuid4()),
                'eventId': event_id,
                'userId': registration.userId,
                'status': 'registered',
                'registeredAt': datetime.utcnow().isoformat() + 'Z'
            }
            registrations_table.put_item(Item=reg_item)
            table.update_item(
                Key={'eventId': event_id},
                UpdateExpression='SET currentRegistrations = currentRegistrations + :inc',
                ExpressionAttributeValues={':inc': 1}
            )
            return reg_item
        elif waitlist_enabled:
            waitlist_count = event.get('waitlistCount', 0)
            reg_item = {
                'registrationId': str(uuid.uuid4()),
                'eventId': event_id,
                'userId': registration.userId,
                'status': 'waitlisted',
                'registeredAt': datetime.utcnow().isoformat() + 'Z',
                'position': waitlist_count + 1
            }
            registrations_table.put_item(Item=reg_item)
            table.update_item(
                Key={'eventId': event_id},
                UpdateExpression='SET waitlistCount = waitlistCount + :inc',
                ExpressionAttributeValues={':inc': 1}
            )
            return reg_item
        else:
            raise HTTPException(status_code=403, detail="Event is full and waitlist is not enabled")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unregister_from_event(event_id: str, user_id: str):
    try:
        reg_response = registrations_table.get_item(Key={'eventId': event_id, 'userId': user_id})
        if 'Item' not in reg_response:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        registration = reg_response['Item']
        reg_status = registration.get('status')
        
        registrations_table.delete_item(Key={'eventId': event_id, 'userId': user_id})
        
        if reg_status == 'registered':
            table.update_item(
                Key={'eventId': event_id},
                UpdateExpression='SET currentRegistrations = currentRegistrations - :dec',
                ExpressionAttributeValues={':dec': 1}
            )
            
            waitlist_response = registrations_table.query(
                KeyConditionExpression='eventId = :eid',
                FilterExpression='#s = :status',
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={':eid': event_id, ':status': 'waitlisted'},
                Limit=1
            )
            
            if waitlist_response.get('Items'):
                first_waitlist = min(waitlist_response['Items'], key=lambda x: x.get('position', 999999))
                registrations_table.update_item(
                    Key={'eventId': event_id, 'userId': first_waitlist['userId']},
                    UpdateExpression='SET #s = :status REMOVE #p',
                    ExpressionAttributeNames={'#s': 'status', '#p': 'position'},
                    ExpressionAttributeValues={':status': 'registered'}
                )
                table.update_item(
                    Key={'eventId': event_id},
                    UpdateExpression='SET currentRegistrations = currentRegistrations + :inc, waitlistCount = waitlistCount - :dec',
                    ExpressionAttributeValues={':inc': 1, ':dec': 1}
                )
        elif reg_status == 'waitlisted':
            table.update_item(
                Key={'eventId': event_id},
                UpdateExpression='SET waitlistCount = waitlistCount - :dec',
                ExpressionAttributeValues={':dec': 1}
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/events")
def list_user_events(user_id: str):
    try:
        user_response = users_table.get_item(Key={'userId': user_id})
        if 'Item' not in user_response:
            raise HTTPException(status_code=404, detail="User not found")
        
        reg_response = registrations_table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        
        events = []
        for reg in reg_response.get('Items', []):
            event_response = table.get_item(Key={'eventId': reg['eventId']})
            if 'Item' in event_response:
                event = event_response['Item']
                events.append({
                    'eventId': event['eventId'],
                    'title': event['title'],
                    'date': event.get('date'),
                    'registrationStatus': reg['status']
                })
        
        return {'events': events}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = Mangum(app)
