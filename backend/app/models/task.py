from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    priority = Column(String(8), default="P3", index=True) # 'P1', 'P2', 'P3', 'P4'
    status = Column(String(32), default="pendiente", index=True) # 'pendiente', 'en_progreso', 'completada', 'cancelada'
    due_date = Column(Date, nullable=True, index=True)
    due_time = Column(Time, nullable=True)
    estimated_minutes = Column(Integer, default=30)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(64), nullable=True) # 'daily', 'weekly', 'monthly'
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    project = relationship("Project", back_populates="tasks")
