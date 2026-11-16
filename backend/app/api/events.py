from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/events", tags=["Agenda y Calendario"])

@router.get("/", response_model=List[EventResponse])
def list_events(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Event).filter(Event.user_id == current_user.id)
    if project_id:
        query = query.filter(Event.project_id == project_id)
    if start:
        query = query.filter(Event.end_time >= start)
    if end:
        query = query.filter(Event.start_time <= end)
    return query.order_by(Event.start_time.asc()).all()

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    ev_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = Event(
        user_id=current_user.id,
        project_id=ev_in.project_id,
        title=ev_in.title,
        description=ev_in.description or "",
        start_time=ev_in.start_time,
        end_time=ev_in.end_time,
        location=ev_in.location or "",
        is_all_day=ev_in.is_all_day or False
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event

@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    ev_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    update_data = ev_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(event, field, val)
        
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    db.delete(event)
    db.commit()
    return None
