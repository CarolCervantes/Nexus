from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = "nota"
    tags: Optional[str] = ""
    project_id: Optional[int] = None
    is_pinned: Optional[bool] = False

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    project_id: Optional[int] = None
    is_pinned: Optional[bool] = None

class NoteResponse(BaseModel):
    id: int
    user_id: int
    project_id: Optional[int]
    title: str
    content: str
    category: str
    tags: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
