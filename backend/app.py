from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
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
table = dynamodb.Table(table_name)

class Event(BaseModel):
    eventId: Optional[str] = None
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    date: str
    location: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)
    organizer: str = Field(..., min_length=1)
    status: str

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    organizer: Optional[str] = None
    status: Optional[str] = None

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
            'status': event.status
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

handler = Mangum(app)
