from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    start_time: datetime
    end_time: datetime
    location: Optional[str] = ""
    is_all_day: Optional[bool] = False
    project_id: Optional[int] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    is_all_day: Optional[bool] = None
    project_id: Optional[int] = None

class EventResponse(BaseModel):
    id: int
    user_id: int
    project_id: Optional[int]
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    is_all_day: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
