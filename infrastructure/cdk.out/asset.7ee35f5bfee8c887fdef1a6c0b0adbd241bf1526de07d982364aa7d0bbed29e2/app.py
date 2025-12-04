from fastapi import FastAPI, HTTPException
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
table = dynamodb.Table(table_name)

class Event(BaseModel):
    eventId: Optional[str] = None
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    date: str
    location: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)
    organizer: str = Field(..., min_length=1)
    status: str = Field(..., pattern="^(draft|published|cancelled)$")

@app.get("/")
def root():
    return {"message": "Event Management API"}

@app.post("/events")
def create_event(event: Event):
    try:
        event_id = str(uuid.uuid4())
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
def list_events():
    try:
        response = table.scan()
        return response.get('Items', [])
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
def update_event(event_id: str, event: Event):
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        table.delete_item(Key={'eventId': event_id})
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = Mangum(app)
