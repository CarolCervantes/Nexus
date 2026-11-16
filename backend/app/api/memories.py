from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryUpdate, MemoryResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/memories", tags=["Memoria Persistente"])

@router.get("/", response_model=List[MemoryResponse])
def list_memories(
    level: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Memory).filter(Memory.user_id == current_user.id, Memory.is_active == True)
    if level:
        query = query.filter(Memory.level == level)
    if category:
        query = query.filter(Memory.category == category)
    return query.order_by(Memory.updated_at.desc()).all()

@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    mem_in: MemoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar si ya existe esa key para el usuario y actualizarla o crear
    existing = db.query(Memory).filter(
        Memory.user_id == current_user.id,
        Memory.key == mem_in.key,
        Memory.is_active == True
    ).first()
    
    if existing:
        existing.value = mem_in.value
        existing.level = mem_in.level or existing.level
        existing.category = mem_in.category or existing.category
        db.commit()
        db.refresh(existing)
        return existing
        
    mem = Memory(
        user_id=current_user.id,
        level=mem_in.level or "permanent",
        category=mem_in.category or "preferencia",
        key=mem_in.key,
        value=mem_in.value,
        confidence=mem_in.confidence or 1.0,
        is_active=True
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem

@router.put("/{memory_id}", response_model=MemoryResponse)
def update_memory(
    memory_id: int,
    mem_in: MemoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mem = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")
        
    update_data = mem_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(mem, field, val)
        
    db.commit()
    db.refresh(mem)
    return mem

@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mem = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Recuerdo no encontrado")
    mem.is_active = False # Soft delete seguro
    db.commit()
    return None
