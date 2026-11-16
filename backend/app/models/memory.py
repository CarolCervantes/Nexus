from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from datetime import datetime, timezone
from app.core.database import Base

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(String(32), default="permanent", index=True)  # 'permanent', 'operational', 'historical'
    category = Column(String(64), default="preferencia", index=True) # 'preferencia', 'objetivo', 'dato_personal', 'decision'
    key = Column(String(128), nullable=False)
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
