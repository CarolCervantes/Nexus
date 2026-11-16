from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Date
from datetime import datetime, timezone
from app.core.database import Base

class FinancialRecord(Base):
    __tablename__ = "financial_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(16), nullable=False, index=True) # 'ingreso', 'gasto'
    category = Column(String(64), nullable=False, index=True) # 'alimentacion', 'transporte', 'servicios', 'educacion', etc.
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="COP")
    description = Column(String(255), default="")
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
