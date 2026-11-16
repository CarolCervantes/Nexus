import json
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.project import Project
from app.models.note import Note
from app.models.memory import Memory
from app.models.finance import FinancialRecord

def execute_tool(db: Session, user_id: int, tool_name: str, args: dict) -> dict:
    """Ejecuta una herramienta real sobre la base de datos para el usuario."""
    try:
        if tool_name == "create_task":
            t_date = None
            if args.get("due_date"):
                try:
                    t_date = date.fromisoformat(args["due_date"])
                except Exception:
                    t_date = date.today()
            task = Task(
                user_id=user_id,
                title=args.get("title", "Tarea sin título"),
                description=args.get("description", ""),
                priority=args.get("priority", "P3"),
                due_date=t_date,
                estimated_minutes=int(args.get("estimated_minutes", 30)),
                project_id=args.get("project_id")
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return {"success": True, "message": f"Tarea creada exitosamente con ID {task.id}", "task_id": task.id, "title": task.title}

        elif tool_name == "list_pending_tasks":
            tasks = db.query(Task).filter(
                Task.user_id == user_id,
                Task.status.in_(["pendiente", "en_progreso"])
            ).order_by(Task.priority.asc(), Task.due_date.asc()).limit(15).all()
            return {
                "success": True,
                "count": len(tasks),
                "tasks": [
                    {"id": t.id, "title": t.title, "priority": t.priority, "due_date": t.due_date.isoformat() if t.due_date else None}
                    for t in tasks
                ]
            }

        elif tool_name == "mark_task_completed":
            tid = int(args.get("task_id", 0))
            task = db.query(Task).filter(Task.id == tid, Task.user_id == user_id).first()
            if not task:
                return {"success": False, "error": f"No se encontró la tarea con ID {tid}"}
            task.status = "completada"
            task.completed_at = datetime.now(timezone.utc)
            db.commit()
            return {"success": True, "message": f"Tarea ID {tid} '{task.title}' marcada como completada"}

        elif tool_name == "create_note":
            note = Note(
                user_id=user_id,
                title=args.get("title", "Nota sin título"),
                content=args.get("content", ""),
                category=args.get("category", "nota"),
                tags=args.get("tags", "")
            )
            db.add(note)
            db.commit()
            db.refresh(note)
            return {"success": True, "message": f"Nota guardada con ID {note.id}", "note_id": note.id, "title": note.title}

        elif tool_name == "save_memory":
            key = args.get("key", "").strip()
            val = args.get("value", "").strip()
            level = args.get("level", "permanent")
            cat = args.get("category", "preferencia")
            if not key or not val:
                return {"success": False, "error": "Se requiere key y value"}
                
            existing = db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.key == key,
                Memory.is_active == True
            ).first()
            if existing:
                existing.value = val
                existing.level = level
                existing.category = cat
                db.commit()
                return {"success": True, "message": f"Recuerdo '{key}' actualizado correctamente"}
            else:
                mem = Memory(user_id=user_id, level=level, category=cat, key=key, value=val)
                db.add(mem)
                db.commit()
                return {"success": True, "message": f"Recuerdo '{key}' guardado en memoria persistente"}

        elif tool_name == "add_financial_record":
            rec = FinancialRecord(
                user_id=user_id,
                type=args.get("type", "gasto").lower(),
                category=args.get("category", "general").lower(),
                amount=float(args.get("amount", 0.0)),
                description=args.get("description", ""),
                date=date.today()
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
            return {"success": True, "message": f"Registro financiero de {rec.amount} ({rec.type}) guardado"}

        else:
            return {"success": False, "error": f"Herramienta desconocida: {tool_name}"}

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
