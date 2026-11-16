from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MemoryCreate(BaseModel):
    level: Optional[str] = "permanent"
    category: Optional[str] = "preferencia"
    key: str
    value: str
    confidence: Optional[float] = 1.0

class MemoryUpdate(BaseModel):
    level: Optional[str] = None
    category: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    confidence: Optional[float] = None
    is_active: Optional[bool] = None

class MemoryResponse(BaseModel):
    id: int
    user_id: int
    level: str
    category: str
    key: str
    value: str
    confidence: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
