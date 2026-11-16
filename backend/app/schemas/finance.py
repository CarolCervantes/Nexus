from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, datetime

class FinanceCreate(BaseModel):
    type: str # 'ingreso', 'gasto'
    category: str
    amount: float
    currency: Optional[str] = "COP"
    description: Optional[str] = ""
    date: Optional[date] = None

class FinanceResponse(BaseModel):
    id: int
    user_id: int
    type: str
    category: str
    amount: float
    currency: str
    description: str
    date: date
    created_at: datetime
    
    class Config:
        from_attributes = True

class FinanceSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    by_category: Dict[str, float]
    currency: str
