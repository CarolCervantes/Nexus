from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.models.event import Event
from app.models.finance import FinancialRecord
from app.models.memory import Memory
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    now_utc = datetime.now(timezone.utc)
    
    # 1. Tareas de hoy y vencidas
    overdue_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status.in_(["pendiente", "en_progreso"]),
        Task.due_date < today
    ).order_by(Task.priority.asc(), Task.due_date.asc()).all()
    
    today_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status.in_(["pendiente", "en_progreso"]),
        Task.due_date == today
    ).order_by(Task.priority.asc()).all()
    
    total_pending = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status.in_(["pendiente", "en_progreso"])
    ).count()
    
    # Completadas hoy
    completed_today = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == "completada",
        func.date(Task.completed_at) == today
    ).count()
    
    # 2. Proyectos activos
    active_projects = db.query(Project).filter(
        Project.user_id == current_user.id,
        Project.status == "activo"
    ).count()
    
    # 3. Próximos eventos (próximos 3 días)
    upcoming_events = db.query(Event).filter(
        Event.user_id == current_user.id,
        Event.start_time >= now_utc,
        Event.start_time <= now_utc + timedelta(days=3)
    ).order_by(Event.start_time.asc()).limit(5).all()
    
    # 4. Finanzas del mes actual
    current_month_records = db.query(FinancialRecord).filter(
        FinancialRecord.user_id == current_user.id,
        func.extract('year', FinancialRecord.date) == today.year,
        func.extract('month', FinancialRecord.date) == today.month
    ).all()
    income = sum(r.amount for r in current_month_records if r.type == "ingreso")
    expense = sum(r.amount for r in current_month_records if r.type == "gasto")
    
    # 5. Memorias clave (preferencias)
    key_memories = db.query(Memory).filter(
        Memory.user_id == current_user.id,
        Memory.is_active == True,
        Memory.level == "permanent"
    ).limit(5).all()

    # Cálculo de carga de trabajo
    total_est_minutes = sum(t.estimated_minutes or 30 for t in today_tasks) + sum(t.estimated_minutes or 30 for t in overdue_tasks)
    hours = round(total_est_minutes / 60.0, 1)

    return {
        "user_name": current_user.full_name,
        "date": today.isoformat(),
        "workload_hours": hours,
        "is_overloaded": hours > 7.0,
        "metrics": {
            "overdue_tasks_count": len(overdue_tasks),
            "today_tasks_count": len(today_tasks),
            "total_pending_tasks": total_pending,
            "completed_today": completed_today,
            "active_projects": active_projects,
            "month_income": round(income, 2),
            "month_expense": round(expense, 2),
            "month_balance": round(income - expense, 2)
        },
        "overdue_tasks": [
            {"id": t.id, "title": t.title, "priority": t.priority, "due_date": t.due_date.isoformat() if t.due_date else None}
            for t in overdue_tasks
        ],
        "today_tasks": [
            {"id": t.id, "title": t.title, "priority": t.priority, "estimated_minutes": t.estimated_minutes}
            for t in today_tasks
        ],
        "upcoming_events": [
            {"id": e.id, "title": e.title, "start_time": e.start_time.isoformat(), "location": e.location}
            for e in upcoming_events
        ],
        "key_memories": [
            {"key": m.key, "value": m.value, "category": m.category}
            for m in key_memories
        ]
    }
