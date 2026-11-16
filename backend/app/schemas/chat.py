from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessageSend(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    voice_enabled: Optional[bool] = False

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender: str
    content: str
    tool_calls: Optional[str] = None
    tool_results: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    title: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class ConversationDetail(ConversationResponse):
    messages: List[MessageResponse] = []
