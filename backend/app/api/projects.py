from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import re
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/projects", tags=["Proyectos"])

def enrich_project(p: Project, db: Session) -> ProjectResponse:
    total = db.query(Task).filter(Task.project_id == p.id).count()
    done = db.query(Task).filter(Task.project_id == p.id, Task.status == "completada").count()
    pct = int((done / total * 100)) if total > 0 else 0
    return ProjectResponse(
        id=p.id,
        user_id=p.user_id,
        name=p.name,
        slug=p.slug,
        description=p.description or "",
        category=p.category,
        status=p.status,
        priority=p.priority,
        target_date=p.target_date,
        created_at=p.created_at,
        updated_at=p.updated_at,
        total_tasks=total,
        completed_tasks=done,
        progress_percentage=pct
    )

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Project).filter(Project.user_id == current_user.id)
    if status:
        query = query.filter(Project.status == status)
    projects = query.order_by(Project.priority.asc(), Project.created_at.desc()).all()
    return [enrich_project(p, db) for p in projects]

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    p_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    slug = re.sub(r"[^a-z0-9]+", "-", p_in.name.lower()).strip("-")
    project = Project(
        user_id=current_user.id,
        name=p_in.name,
        slug=slug,
        description=p_in.description or "",
        category=p_in.category or "personal",
        status=p_in.status or "activo",
        priority=p_in.priority or "P3",
        target_date=p_in.target_date
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return enrich_project(project, db)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return enrich_project(project, db)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    p_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    update_data = p_in.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"]:
        project.slug = re.sub(r"[^a-z0-9]+", "-", update_data["name"].lower()).strip("-")
        
    for field, val in update_data.items():
        setattr(project, field, val)
        
    db.commit()
    db.refresh(project)
    return enrich_project(project, db)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.delete(project)
    db.commit()
    return None
