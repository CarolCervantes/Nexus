from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models.user import User
from app.models.finance import FinancialRecord
from app.schemas.finance import FinanceCreate, FinanceResponse, FinanceSummary
from app.api.deps import get_current_user

router = APIRouter(prefix="/finances", tags=["Finanzas Personales"])

@router.get("/", response_model=List[FinanceResponse])
def list_finances(
    type: Optional[str] = None,
    month: Optional[str] = None, # Formato YYYY-MM
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FinancialRecord).filter(FinancialRecord.user_id == current_user.id)
    if type:
        query = query.filter(FinancialRecord.type == type)
    if month:
        # Filtrar por año y mes
        try:
            year, m = map(int, month.split("-"))
            query = query.filter(
                func.extract('year', FinancialRecord.date) == year,
                func.extract('month', FinancialRecord.date) == m
            )
        except Exception:
            pass
    return query.order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc()).all()

@router.get("/summary", response_model=FinanceSummary)
def get_finance_summary(
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FinancialRecord).filter(FinancialRecord.user_id == current_user.id)
    if month:
        try:
            year, m = map(int, month.split("-"))
            query = query.filter(
                func.extract('year', FinancialRecord.date) == year,
                func.extract('month', FinancialRecord.date) == m
            )
        except Exception:
            pass
            
    records = query.all()
    total_income = sum(r.amount for r in records if r.type == "ingreso")
    total_expense = sum(r.amount for r in records if r.type == "gasto")
    net_balance = total_income - total_expense
    
    by_category = {}
    for r in records:
        if r.type == "gasto":
            by_category[r.category] = by_category.get(r.category, 0.0) + r.amount
            
    return FinanceSummary(
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net_balance=round(net_balance, 2),
        by_category={k: round(v, 2) for k, v in by_category.items()},
        currency="COP"
    )

@router.post("/", response_model=FinanceResponse, status_code=status.HTTP_201_CREATED)
def create_finance(
    f_in: FinanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = FinancialRecord(
        user_id=current_user.id,
        type=f_in.type.lower(),
        category=f_in.category.lower(),
        amount=f_in.amount,
        currency=f_in.currency or "COP",
        description=f_in.description or "",
        date=f_in.date or date.today()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_finance(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(FinancialRecord).filter(FinancialRecord.id == record_id, FinancialRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro financiero no encontrado")
    db.delete(record)
    db.commit()
    return None
