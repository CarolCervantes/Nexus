from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    project_id: Optional[int] = None
    priority: Optional[str] = "P3"
    status: Optional[str] = "pendiente"
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_minutes: Optional[int] = 30
    is_recurring: Optional[bool] = False
    recurrence_rule: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_minutes: Optional[int] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    user_id: int
    project_id: Optional[int]
    title: str
    description: str
    priority: str
    status: str
    due_date: Optional[date]
    due_time: Optional[time]
    estimated_minutes: int
    is_recurring: bool
    recurrence_rule: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
