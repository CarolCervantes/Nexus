from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone, date
from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tareas"])

@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    project_id: Optional[int] = None,
    due_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task).filter(Task.user_id == current_user.id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if due_date:
        query = query.filter(Task.due_date == due_date)
    return query.order_by(
        Task.priority.asc(),
        Task.due_date.asc().nullslast(),
        Task.created_at.desc()
    ).all()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = Task(
        user_id=current_user.id,
        project_id=task_in.project_id,
        title=task_in.title,
        description=task_in.description or "",
        priority=task_in.priority or "P3",
        status=task_in.status or "pendiente",
        due_date=task_in.due_date,
        due_time=task_in.due_time,
        estimated_minutes=task_in.estimated_minutes or 30,
        is_recurring=task_in.is_recurring or False,
        recurrence_rule=task_in.recurrence_rule
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    update_data = task_in.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == "completada" and task.status != "completada":
        task.completed_at = datetime.now(timezone.utc)
    elif "status" in update_data and update_data["status"] != "completada":
        task.completed_at = None
        
    for field, val in update_data.items():
        setattr(task, field, val)
        
    db.commit()
    db.refresh(task)
    return task

@router.post("/{task_id}/complete", response_model=TaskResponse)
def toggle_task_complete(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    if task.status == "completada":
        task.status = "pendiente"
        task.completed_at = None
    else:
        task.status = "completada"
        task.completed_at = datetime.now(timezone.utc)
        
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db.delete(task)
    db.commit()
    return None
