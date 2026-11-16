from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    category: Optional[str] = "personal"
    status: Optional[str] = "activo"
    priority: Optional[str] = "P3"
    target_date: Optional[date] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    target_date: Optional[date] = None

class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    slug: Optional[str]
    description: str
    category: str
    status: str
    priority: str
    target_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    total_tasks: Optional[int] = 0
    completed_tasks: Optional[int] = 0
    progress_percentage: Optional[int] = 0
    
    class Config:
        from_attributes = True
