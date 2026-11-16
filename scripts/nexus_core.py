#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEXUS Core Engine - Motor central de persistencia, lógica y sincronización
Versión: 1.0.0
Tecnología: Python 3 Standard Library + SQLite 3
"""

import sys
import os
import sqlite3
import argparse
import json
import shutil
import re
from datetime import datetime, date, timedelta
from pathlib import Path

# Asegurar soporte UTF-8 en salida estándar de Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Configuración de rutas base
NEXUS_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = NEXUS_ROOT / "data"
DB_PATH = DATA_DIR / "nexus.db"
SCHEMA_PATH = DATA_DIR / "schema.sql"
BACKUP_DIR = DATA_DIR / "backups"
TASKS_DIR = NEXUS_ROOT / "tasks"
PROJECTS_DIR = NEXUS_ROOT / "projects"
MEMORY_DIR = NEXUS_ROOT / "memory"
LOGS_DIR = NEXUS_ROOT / "logs"
REPORTS_DIR = NEXUS_ROOT / "reports"

def get_connection():
    """Obtiene una conexión a SQLite con soporte de llaves foráneas y tipos por defecto."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def now_iso():
    """Devuelve la fecha y hora actual en formato ISO 8601."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def today_iso():
    """Devuelve la fecha actual en formato YYYY-MM-DD."""
    return date.today().strftime("%Y-%m-%d")

def log_audit(conn, action_type, entity_type, entity_id, details):
    """Registra una operación en audit_log."""
    conn.execute(
        "INSERT INTO audit_log (timestamp, action_type, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?)",
        (now_iso(), action_type, entity_type, entity_id, details)
    )

def log_operation_file(action_desc):
    """Escribe en logs/operations.log."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "operations.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{now_iso()}] {action_desc}\n")

# ==========================================
# 1. INICIALIZACIÓN Y MANTENIMIENTO
# ==========================================

def init_db():
    """Crea la base de datos y aplica el esquema si no existe."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not SCHEMA_PATH.exists():
        print(f"Error: No se encontró el esquema en {SCHEMA_PATH}")
        sys.exit(1)
        
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection() as conn:
        conn.executescript(schema_sql)
        log_audit(conn, "INIT", "system", 0, "Base de datos inicializada con éxito")
        conn.commit()

    log_operation_file("Base de datos SQLite inicializada o verificada")
    print(f"Base de datos NEXUS lista en: {DB_PATH}")

def backup_db():
    """Crea una copia de seguridad timestamped de la base de datos."""
    if not DB_PATH.exists():
        print("La base de datos aún no existe.")
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"nexus_backup_{ts}.db"
    shutil.copy2(DB_PATH, backup_file)
    with get_connection() as conn:
        log_audit(conn, "BACKUP", "system", 0, f"Copia de seguridad: {backup_file.name}")
        conn.commit()
    log_operation_file(f"Copia de seguridad creada: {backup_file.name}")
    print(f"Respaldo creado: {backup_file}")
    return backup_file

def integrity_check():
    """Verifica la integridad de la base de datos y reporta recuentos."""
    if not DB_PATH.exists():
        print("Base de datos no encontrada.")
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        res = cursor.fetchone()[0]
        print(f"Estado de integridad física SQLite: {res}")
        
        tables = ["projects", "tasks", "commitments", "notes", "decisions", "sessions", "audit_log"]
        print("\nRecuento de registros:")
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cursor.fetchone()[0]
            print(f"  - {t}: {cnt} registros")

# ==========================================
# 2. GESTIÓN DE PROYECTOS
# ==========================================

def project_add(name, category="personal", priority="P3", target_date=None, description=""):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    created = now_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM projects WHERE slug = ? OR name = ?", (slug, name))
        existing = cursor.fetchone()
        if existing:
            pid = existing[0]
            print(f"El proyecto ya existe. ID: {pid} | Slug: {slug}")
            return pid
        cursor.execute(
            """INSERT INTO projects (name, slug, description, category, priority, target_date, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, slug, description, category, priority, target_date, created, created)
        )
        pid = cursor.lastrowid
        log_audit(conn, "INSERT", "project", pid, f"Proyecto creado: {name}")
        conn.commit()
    log_operation_file(f"Proyecto añadido [ID:{pid}] '{name}' ({category}, {priority})")
    print(f"Proyecto creado con éxito. ID: {pid} | Slug: {slug}")
    sync_markdown()
    return pid

def project_list(status=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT p.*,
                   COUNT(t.id) as total_tasks,
                   SUM(CASE WHEN t.status = 'completada' THEN 1 ELSE 0 END) as done_tasks
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
        """
        params = []
        if status:
            query += " WHERE p.status = ?"
            params.append(status)
        query += " GROUP BY p.id ORDER BY p.priority ASC, p.created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            print("No se encontraron proyectos.")
            return []
        
        print(f"\n{'ID':<4} | {'Prioridad':<9} | {'Estado':<10} | {'Categoría':<11} | {'Avance':<8} | {'Nombre'}")
        print("-" * 80)
        for r in rows:
            total = r["total_tasks"] or 0
            done = r["done_tasks"] or 0
            pct = f"{(done/total*100):.0f}%" if total > 0 else "0/0"
            print(f"{r['id']:<4} | {r['priority']:<9} | {r['status']:<10} | {r['category']:<11} | {pct:<8} | {r['name']}")
        return [dict(r) for r in rows]

# ==========================================
# 3. GESTIÓN DE TAREAS
# ==========================================

def task_add(title, project_id=None, priority="P3", due_date=None, due_time=None, est_minutes=30, description=""):
    created = now_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (project_id, title, description, priority, status, due_date, due_time, estimated_minutes, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'pendiente', ?, ?, ?, ?, ?)""",
            (project_id, title, description, priority, due_date, due_time, est_minutes, created, created)
        )
        tid = cursor.lastrowid
        log_audit(conn, "INSERT", "task", tid, f"Tarea: {title}")
        conn.commit()
    log_operation_file(f"Tarea añadida [ID:{tid}] '{title}' (Prioridad: {priority}, Fecha: {due_date or 'Sin fecha'})")
    print(f"Tarea añadida con éxito. ID: {tid} | Título: {title} | Prioridad: {priority}")
    sync_markdown()
    return tid

def task_list(status=None, priority=None, project_id=None, due_before=None, as_json=False):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT t.*, p.name as project_name
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND t.status = ?"
            params.append(status)
        if priority:
            query += " AND t.priority = ?"
            params.append(priority)
        if project_id:
            query += " AND t.project_id = ?"
            params.append(project_id)
        if due_before:
            query += " AND t.due_date <= ?"
            params.append(due_before)
            
        query += " ORDER BY t.priority ASC, CASE WHEN t.due_date IS NULL THEN 1 ELSE 0 END, t.due_date ASC, t.id ASC"
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        
        if as_json:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
            return rows
            
        if not rows:
            print("No se encontraron tareas con los filtros indicados.")
            return []
            
        print(f"\n{'ID':<4} | {'Prio':<4} | {'Estado':<11} | {'Vence':<10} | {'Proyecto':<15} | {'Título'}")
        print("-" * 80)
        for r in rows:
            due = r['due_date'] or "Sin fecha"
            proj = (r['project_name'][:14] + "..") if r['project_name'] and len(r['project_name']) > 14 else (r['project_name'] or "-")
            print(f"{r['id']:<4} | {r['priority']:<4} | {r['status']:<11} | {due:<10} | {proj:<15} | {r['title']}")
        return rows

def task_done(task_id):
    now_ts = now_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, status FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            print(f"Error: No existe la tarea con ID {task_id}")
            return False
        cursor.execute(
            "UPDATE tasks SET status = 'completada', completed_at = ?, updated_at = ? WHERE id = ?",
            (now_ts, now_ts, task_id)
        )
        log_audit(conn, "UPDATE", "task", task_id, f"Marcada como completada: {row['title']}")
        conn.commit()
    log_operation_file(f"Tarea completada [ID:{task_id}] '{row['title']}'")
    print(f"Tarea {task_id} completada exitosamente.")
    sync_markdown()
    return True

def task_update(task_id, title=None, status=None, priority=None, due_date=None, due_time=None, description=None):
    fields = []
    params = []
    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if status is not None:
        fields.append("status = ?")
        params.append(status)
        if status == "completada":
            fields.append("completed_at = ?")
            params.append(now_iso())
    if priority is not None:
        fields.append("priority = ?")
        params.append(priority)
    if due_date is not None:
        fields.append("due_date = ?")
        params.append(due_date)
    if due_time is not None:
        fields.append("due_time = ?")
        params.append(due_time)
    if description is not None:
        fields.append("description = ?")
        params.append(description)
        
    if not fields:
        print("No se especificaron campos para actualizar.")
        return False
        
    fields.append("updated_at = ?")
    params.append(now_iso())
    params.append(task_id)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            print(f"No se encontró la tarea ID {task_id}")
            return False
        log_audit(conn, "UPDATE", "task", task_id, f"Campos actualizados: {', '.join(fields)}")
        conn.commit()
    log_operation_file(f"Tarea actualizada [ID:{task_id}]")
    print(f"Tarea {task_id} actualizada.")
    sync_markdown()
    return True

# ==========================================
# 4. GESTIÓN DE COMPROMISOS
# ==========================================

def commitment_add(counterparty, title, due_date, importance="alta", description="", project_id=None):
    created = now_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO commitments (counterparty, title, description, due_date, status, importance, related_project_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'pendiente', ?, ?, ?, ?)""",
            (counterparty, title, description, due_date, importance, project_id, created, created)
        )
        cid = cursor.lastrowid
        log_audit(conn, "INSERT", "commitment", cid, f"Compromiso con {counterparty}: {title}")
        conn.commit()
    log_operation_file(f"Compromiso adquirido [ID:{cid}] con '{counterparty}': '{title}' (Vence: {due_date})")
    print(f"Compromiso registrado. ID: {cid} | Con: {counterparty} | Vence: {due_date}")
    sync_markdown()
    return cid

def commitment_list(status=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM commitments"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY due_date ASC, importance DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        if not rows:
            print("No hay compromisos registrados.")
            return []
        print(f"\n{'ID':<4} | {'Vence':<10} | {'Importancia':<11} | {'Estado':<10} | {'Contraparte':<15} | {'Título'}")
        print("-" * 80)
        for r in rows:
            print(f"{r['id']:<4} | {r['due_date']:<10} | {r['importance']:<11} | {r['status']:<10} | {r['counterparty']:<15} | {r['title']}")
        return [dict(r) for r in rows]

# ==========================================
# 5. GESTIÓN DE NOTAS Y DECISIONES
# ==========================================

def note_add(title, content, category="nota", tags="", project_id=None):
    created = now_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO notes (title, content, category, tags, project_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, content, category, tags, project_id, created, created)
        )
        nid = cursor.lastrowid
        log_audit(conn, "INSERT", "note", nid, f"Nota añadida: {title}")
        conn.commit()
    log_operation_file(f"Nota guardada [ID:{nid}] '{title}' ({category}) [tags: {tags}]")
    print(f"Nota guardada. ID: {nid} | Categoría: {category} | Título: {title}")
    sync_markdown()
    return nid

def note_list(search=None, category=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, title, category, tags, created_at FROM notes WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if search:
            query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
            s = f"%{search}%"
            params.extend([s, s, s])
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        if not rows:
            print("No se encontraron notas.")
            return []
        print(f"\n{'ID':<4} | {'Categoría':<10} | {'Fecha':<19} | {'Tags':<15} | {'Título'}")
        print("-" * 75)
        for r in rows:
            tags = r['tags'] or "-"
            print(f"{r['id']:<4} | {r['category']:<10} | {r['created_at']:<19} | {tags:<15} | {r['title']}")
        return [dict(r) for r in rows]

def decision_add(title, context, decision_made, rationale="", impact="", project_id=None):
    created = now_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO decisions (title, context, decision_made, rationale, impact, project_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, context, decision_made, rationale, impact, project_id, created)
        )
        did = cursor.lastrowid
        log_audit(conn, "INSERT", "decision", did, f"Decisión: {title}")
        conn.commit()
    log_operation_file(f"Decisión registrada [ID:{did}] '{title}'")
    print(f"Decisión registrada en memoria histórica. ID: {did} | Título: {title}")
    sync_markdown()
    return did

def decision_list():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM decisions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        if not rows:
            print("No hay decisiones registradas.")
            return []
        print(f"\n{'ID':<4} | {'Fecha':<19} | {'Título':<30} | {'Decisión tomada'}")
        print("-" * 80)
        for r in rows:
            print(f"{r['id']:<4} | {r['created_at']:<19} | {r['title'][:29]:<30} | {r['decision_made'][:35]}")
        return [dict(r) for r in rows]

# ==========================================
# 6. PLANIFICACIÓN Y DETECCIÓN DE CONFLICTOS
# ==========================================

def plan_day(target_date_str=None):
    t_date = target_date_str or today_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tareas para la fecha
        cursor.execute("""
            SELECT t.*, p.name as project_name
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.status IN ('pendiente', 'en_progreso')
              AND (t.due_date = ? OR (t.due_date < ? AND t.due_date IS NOT NULL))
            ORDER BY t.priority ASC, t.due_date ASC
        """, (t_date, t_date))
        tasks = cursor.fetchall()
        
        # Compromisos para la fecha o vencidos
        cursor.execute("""
            SELECT * FROM commitments
            WHERE status = 'pendiente'
              AND (due_date = ? OR due_date < ?)
            ORDER BY due_date ASC, importance DESC
        """, (t_date, t_date))
        commitments = cursor.fetchall()
        
    print(f"\n========================================================")
    print(f"   PLAN DEL DÍA - {t_date}")
    print(f"========================================================\n")
    
    overdue_tasks = [t for t in tasks if t['due_date'] and t['due_date'] < t_date]
    today_tasks = [t for t in tasks if t['due_date'] == t_date]
    overdue_commits = [c for c in commitments if c['due_date'] < t_date]
    today_commits = [c for c in commitments if c['due_date'] == t_date]
    
    total_est_minutes = sum(t['estimated_minutes'] or 30 for t in today_tasks) + sum(t['estimated_minutes'] or 30 for t in overdue_tasks)
    hours = total_est_minutes / 60.0
    
    # Detección de sobrecarga o conflictos
    if overdue_tasks or overdue_commits:
        print("⚠️ ALERTA: ELEMENTOS ATRASADOS QUE REQUIEREN ATENCIÓN INMEDIATA:")
        for ot in overdue_tasks:
            print(f"   - [Tarea ID {ot['id']}] {ot['title']} (Venció: {ot['due_date']}, Prio: {ot['priority']})")
        for oc in overdue_commits:
            print(f"   - [Compromiso ID {oc['id']}] {oc['title']} con {oc['counterparty']} (Venció: {oc['due_date']})")
        print()
        
    if hours > 7.0:
        print(f"⚠️ ALERTA DE CARGA: La carga estimada de trabajo para hoy es de {hours:.1f} horas.")
        print("   Recomendación: Mueve tareas P3/P4 no críticas a los próximos días.\n")
    else:
        print(f"ℹ️ Carga estimada de trabajo: {hours:.1f} horas ({len(today_tasks) + len(overdue_tasks)} tareas totales).\n")
        
    print("📋 COMPROMISOS CRÍTICOS HOY:")
    if today_commits:
        for c in today_commits:
            print(f"   ⭐ [{c['importance'].upper()}] {c['title']} (Con: {c['counterparty']})")
    else:
        print("   (Ningún compromiso externo vence hoy)")
    print()
    
    print("🎯 SECUENCIA RECOMENDADA DE EJECUCIÓN (Por prioridad y urgencia):")
    all_actionable = overdue_tasks + today_tasks
    if not all_actionable:
        print("   No hay tareas asignadas para hoy. Puedes avanzar en el backlog o proyectos.")
    else:
        for idx, t in enumerate(all_actionable, 1):
            tag = "VENCIDA" if (t['due_date'] and t['due_date'] < t_date) else t['priority']
            print(f"   {idx}. [{tag}] ID:{t['id']} | {t['title']} (~{t['estimated_minutes']} min)")
    print("\n========================================================\n")

# ==========================================
# 7. SINCRONIZACIÓN Y EXPORTACIÓN A MARKDOWN
# ==========================================

def sync_markdown():
    """Exporta y actualiza las vistas Markdown para que sean legibles y accesibles."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    (MEMORY_DIR / "operational").mkdir(parents=True, exist_ok=True)
    (MEMORY_DIR / "historical").mkdir(parents=True, exist_ok=True)
    
    t_today = today_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. tasks/today.md
        cursor.execute("""
            SELECT t.*, p.name as project_name
            FROM tasks t LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.status IN ('pendiente', 'en_progreso')
              AND (t.due_date = ? OR t.due_date < ?)
            ORDER BY t.priority ASC, t.due_date ASC
        """, (t_today, t_today))
        today_tasks = cursor.fetchall()
        
        with open(TASKS_DIR / "today.md", "w", encoding="utf-8") as f:
            f.write(f"# Tareas Para Hoy ({t_today})\n\n")
            f.write(f"*Última sincronización: {now_iso()}*\n\n")
            if not today_tasks:
                f.write("No hay tareas pendientes asignadas para hoy.\n")
            else:
                f.write("| ID | Prio | Estado | Vence | Proyecto | Título |\n")
                f.write("|---|---|---|---|---|---|\n")
                for t in today_tasks:
                    pname = t['project_name'] or "-"
                    f.write(f"| {t['id']} | {t['priority']} | {t['status']} | {t['due_date'] or '-'} | {pname} | {t['title']} |\n")

        # 2. tasks/backlog.md
        cursor.execute("""
            SELECT t.*, p.name as project_name
            FROM tasks t LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.status IN ('pendiente', 'en_progreso')
              AND (t.due_date IS NULL OR t.due_date > ?)
            ORDER BY t.priority ASC, t.due_date ASC
        """, (t_today,))
        backlog_tasks = cursor.fetchall()
        
        with open(TASKS_DIR / "backlog.md", "w", encoding="utf-8") as f:
            f.write(f"# Backlog y Tareas Futuras\n\n")
            f.write(f"*Última sincronización: {now_iso()}*\n\n")
            if not backlog_tasks:
                f.write("El backlog está vacío.\n")
            else:
                f.write("| ID | Prio | Estado | Fecha Límite | Proyecto | Título |\n")
                f.write("|---|---|---|---|---|---|\n")
                for t in backlog_tasks:
                    pname = t['project_name'] or "-"
                    f.write(f"| {t['id']} | {t['priority']} | {t['status']} | {t['due_date'] or 'Sin fecha'} | {pname} | {t['title']} |\n")

        # 3. memory/operational/current_state.md
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('pendiente', 'en_progreso')")
        pending_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completada'")
        done_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'activo'")
        active_projects_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM commitments WHERE status = 'pendiente'")
        pending_commits = cursor.fetchone()[0]
        
        with open(MEMORY_DIR / "operational" / "current_state.md", "w", encoding="utf-8") as f:
            f.write(f"# Memoria Operativa: Estado Actual de NEXUS\n\n")
            f.write(f"**Fecha actual**: {t_today} | **Hora**: {now_iso()}\n\n")
            f.write(f"### Métricas Clave\n")
            f.write(f"- **Proyectos activos**: {active_projects_count}\n")
            f.write(f"- **Tareas pendientes/en progreso**: {pending_count}\n")
            f.write(f"- **Tareas completadas**: {done_count}\n")
            f.write(f"- **Compromisos pendientes**: {pending_commits}\n\n")
            f.write(f"### Foco Inmediato (Tareas Hoy / Vencidas)\n")
            if not today_tasks:
                f.write("- Al día. No hay tareas vencidas ni asignadas para hoy.\n")
            else:
                for t in today_tasks:
                    f.write(f"- [{t['priority']}] ID {t['id']}: **{t['title']}** (Vence: {t['due_date']})\n")

        # 4. memory/historical/decisions_log.md
        cursor.execute("SELECT * FROM decisions ORDER BY created_at DESC")
        decisions = cursor.fetchall()
        with open(MEMORY_DIR / "historical" / "decisions_log.md", "w", encoding="utf-8") as f:
            f.write("# Bitácora Histórica de Decisiones\n\n")
            f.write("*Registro inmutable de decisiones estratégicas, técnicas y de organización.*\n\n")
            if not decisions:
                f.write("Aún no se han registrado decisiones clave.\n")
            else:
                for d in decisions:
                    f.write(f"### {d['title']} (Fecha: {d['created_at']})\n")
                    f.write(f"- **Contexto**: {d['context']}\n")
                    f.write(f"- **Decisión tomada**: {d['decision_made']}\n")
                    if d['rationale']:
                        f.write(f"- **Justificación**: {d['rationale']}\n")
                    if d['impact']:
                        f.write(f"- **Impacto previsto**: {d['impact']}\n")
                    f.write("\n---\n\n")

    log_operation_file("Vistas Markdown sincronizadas correctamente")

# ==========================================
# 8. INFORMES Y RESÚMENES
# ==========================================

def report_daily():
    t_today = today_iso()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "daily").mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / "daily" / f"{t_today}.md"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE status = 'completada' AND completed_at LIKE ?", (f"{t_today}%",))
        completed_today = cursor.fetchall()
        
        cursor.execute("SELECT * FROM tasks WHERE status IN ('pendiente', 'en_progreso') AND (due_date = ? OR due_date < ?)", (t_today, t_today))
        remaining_today = cursor.fetchall()
        
        cursor.execute("SELECT * FROM notes WHERE created_at LIKE ?", (f"{t_today}%",))
        notes_today = cursor.fetchall()
        
        cursor.execute("SELECT * FROM decisions WHERE created_at LIKE ?", (f"{t_today}%",))
        decisions_today = cursor.fetchall()
        
    content = f"""# Resumen Diario NEXUS - {t_today}
*Generado automáticamente el {now_iso()}*

## 1. Actividades Completadas Hoy ({len(completed_today)})
"""
    if completed_today:
        for t in completed_today:
            content += f"- ✅ [ID {t['id']}] **{t['title']}** (Completada a las {t['completed_at']})\n"
    else:
        content += "- Ninguna tarea marcada como completada en esta fecha.\n"
        
    content += f"\n## 2. Pendientes y Alertas ({len(remaining_today)})\n"
    if remaining_today:
        for t in remaining_today:
            content += f"- ⏳ [{t['priority']}] [ID {t['id']}] **{t['title']}** (Vence: {t['due_date'] or 'Hoy'})\n"
    else:
        content += "- No quedan tareas pendientes urgentes para hoy.\n"
        
    content += f"\n## 3. Notas e Ideas Registradas ({len(notes_today)})\n"
    if notes_today:
        for n in notes_today:
            content += f"- 💡 [{n['category']}] **{n['title']}**: {n['content'][:80]}...\n"
    else:
        content += "- Sin notas registradas hoy.\n"

    content += f"\n## 4. Decisiones Clave del Día ({len(decisions_today)})\n"
    if decisions_today:
        for d in decisions_today:
            content += f"- ⚖️ **{d['title']}**: {d['decision_made']}\n"
    else:
        content += "- Sin decisiones formalmente registradas hoy.\n"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Informe diario generado con éxito en: {report_file}")
    log_operation_file(f"Informe diario generado para {t_today}")

# ==========================================
# 9. CONTINUIDAD DE SESIONES (START / END)
# ==========================================

def session_start():
    """Inicia la sesión, asegurando lectura del contexto relevante y persistencia."""
    init_db()
    sync_markdown()
    
    t_today = today_iso()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (session_start) VALUES (?)", (now_iso(),))
        session_id = cursor.lastrowid
        conn.commit()
        
    log_operation_file(f"Sesión iniciada [ID:{session_id}]")
    print(f"\n========================================================")
    print(f"   🟢 NEXUS INICIADO - SESIÓN ID: {session_id}")
    print(f"   Fecha: {t_today} | Modo: Persistencia Activa")
    print(f"========================================================\n")
    plan_day()
    return session_id

def session_end(summary="Cierre regular de sesión"):
    """Cierra la sesión, guarda cambios, genera respaldo y sincroniza vistas."""
    sync_markdown()
    backup_path = backup_db()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sessions WHERE session_end IS NULL ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            sid = row[0]
            cursor.execute("UPDATE sessions SET session_end = ?, summary_actions = ? WHERE id = ?", (now_iso(), summary, sid))
            conn.commit()
            
    log_operation_file(f"Sesión finalizada. Respaldo: {backup_path.name if backup_path else 'N/A'}")
    print(f"\n========================================================")
    print(f"   🔴 NEXUS: SESIÓN FINALIZADA Y PERSISTIDA")
    print(f"   Respaldo generado en: {backup_path}")
    print(f"   Archivos Markdown sincronizados.")
    print(f"========================================================\n")

# ==========================================
# 10. MODO INTERACTIVO DE CONSOLA
# ==========================================

def interactive_menu():
    """Lanza una interfaz de consola interactiva amigable cuando se ejecuta sin argumentos."""
    init_db()
    sync_markdown()
    while True:
        print("\n" + "=" * 60)
        print("          🤖 NEXUS - ASISTENTE PERSONAL INTERACTIVO")
        print("=" * 60)
        print("  1. 📋 Ver plan de hoy y recomendaciones de foco")
        print("  2. 📝 Ver todas las tareas pendientes")
        print("  3. ➕ Añadir una nueva tarea")
        print("  4. ✅ Marcar una tarea como completada")
        print("  5. 🤝 Registrar un compromiso con un tercero")
        print("  6. 💡 Guardar una idea o nota")
        print("  7. ⚖️ Registrar una decisión importante")
        print("  8. 📁 Ver proyectos y porcentaje de avance")
        print("  9. 📊 Generar informe del día")
        print(" 10. 💾 Crear copia de seguridad (backup)")
        print("  0. 🚪 Salir y guardar cambios")
        print("=" * 60)
        try:
            choice = input("Selecciona una opción [0-10]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta luego.")
            break
            
        if choice == "1":
            plan_day()
        elif choice == "2":
            task_list(status="pendiente")
        elif choice == "3":
            title = input("Título de la tarea: ").strip()
            if not title:
                print("Operación cancelada: el título es obligatorio.")
                continue
            prio = input("Prioridad (P1=Urgente, P2=Importante, P3=Normal, P4=Baja) [P3]: ").strip().upper()
            if prio not in ["P1", "P2", "P3", "P4"]:
                prio = "P3"
            due = input(f"Fecha límite (YYYY-MM-DD) [Presiona Enter para hoy {today_iso()}]: ").strip()
            if not due:
                due = today_iso()
            est = input("Minutos estimados [30]: ").strip()
            try:
                est_m = int(est) if est else 30
            except ValueError:
                est_m = 30
            desc = input("Descripción o notas adicionales (opcional): ").strip()
            task_add(title=title, priority=prio, due_date=due, est_minutes=est_m, description=desc)
        elif choice == "4":
            task_list(status="pendiente")
            tid = input("\nIngresa el ID de la tarea completada: ").strip()
            try:
                task_done(int(tid))
            except ValueError:
                print("ID no válido.")
        elif choice == "5":
            who = input("Persona o entidad (con quién): ").strip()
            title = input("Qué acordaron entregar o hacer: ").strip()
            due = input("Fecha límite (YYYY-MM-DD): ").strip()
            imp = input("Importancia (critica/alta/media/baja) [alta]: ").strip().lower()
            if imp not in ["critica", "alta", "media", "baja"]:
                imp = "alta"
            commitment_add(counterparty=who, title=title, due_date=due, importance=imp)
        elif choice == "6":
            title = input("Título de la idea/nota: ").strip()
            content = input("Detalle o contenido: ").strip()
            cat = input("Categoría (idea/nota/recurso/referencia) [nota]: ").strip().lower()
            if cat not in ["idea", "nota", "recurso", "referencia"]:
                cat = "nota"
            tags = input("Etiquetas separadas por comas (ej. tesis,ia): ").strip()
            note_add(title=title, content=content, category=cat, tags=tags)
        elif choice == "7":
            title = input("Título de la decisión: ").strip()
            ctx = input("Contexto o dilema: ").strip()
            dec = input("Decisión final adoptada: ").strip()
            rat = input("Razón o justificación: ").strip()
            decision_add(title=title, context=ctx, decision_made=dec, rationale=rat)
        elif choice == "8":
            project_list()
        elif choice == "9":
            report_daily()
        elif choice == "10":
            backup_db()
        elif choice == "0":
            session_end("Cierre interactivo desde consola")
            print("Sesión cerrada y guardada con éxito.")
            break
        else:
            print("Opción no reconocida. Intenta de nuevo.")

# ==========================================
# 11. ENTRYPOINT CLI
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="NEXUS Core Engine - Asistente Personal Persistente")
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # Init
    subparsers.add_parser("init-db", help="Inicializa la base de datos")
    subparsers.add_parser("backup", help="Crea un respaldo de la base de datos")
    subparsers.add_parser("integrity", help="Verifica integridad y conteo de tablas")
    subparsers.add_parser("sync", help="Sincroniza bases de datos con archivos Markdown")
    
    # Sessions
    subparsers.add_parser("session-start", help="Inicia sesión y muestra el contexto")
    p_send = subparsers.add_parser("session-end", help="Cierra sesión y crea respaldo")
    p_send.add_argument("--summary", default="Cierre regular de sesión", help="Resumen de acciones")
    
    # Tasks
    p_tadd = subparsers.add_parser("task-add", help="Añade una tarea")
    p_tadd.add_argument("--title", required=True, help="Título de la tarea")
    p_tadd.add_argument("--project-id", type=int, help="ID de proyecto asociado")
    p_tadd.add_argument("--priority", choices=["P1", "P2", "P3", "P4"], default="P3", help="Prioridad")
    p_tadd.add_argument("--due-date", help="Fecha límite (YYYY-MM-DD)")
    p_tadd.add_argument("--due-time", help="Hora límite (HH:MM)")
    p_tadd.add_argument("--est-minutes", type=int, default=30, help="Minutos estimados")
    p_tadd.add_argument("--desc", default="", help="Descripción detallada")
    
    p_tlist = subparsers.add_parser("task-list", help="Lista tareas")
    p_tlist.add_argument("--status", choices=["pendiente", "en_progreso", "completada", "cancelada"])
    p_tlist.add_argument("--priority", choices=["P1", "P2", "P3", "P4"])
    p_tlist.add_argument("--project-id", type=int)
    p_tlist.add_argument("--due-before", help="Tareas que vencen hasta esta fecha")
    p_tlist.add_argument("--json", action="store_true", help="Salida en JSON")
    
    p_tdone = subparsers.add_parser("task-done", help="Marca tarea como completada")
    p_tdone.add_argument("id", type=int, help="ID de la tarea")
    
    p_tupd = subparsers.add_parser("task-update", help="Actualiza una tarea")
    p_tupd.add_argument("id", type=int, help="ID de la tarea")
    p_tupd.add_argument("--title")
    p_tupd.add_argument("--status", choices=["pendiente", "en_progreso", "completada", "cancelada"])
    p_tupd.add_argument("--priority", choices=["P1", "P2", "P3", "P4"])
    p_tupd.add_argument("--due-date")
    p_tupd.add_argument("--due-time")
    p_tupd.add_argument("--desc")
    
    # Projects
    p_padd = subparsers.add_parser("project-add", help="Añade un proyecto")
    p_padd.add_argument("--name", required=True, help="Nombre del proyecto")
    p_padd.add_argument("--category", choices=["personal", "académico", "profesional", "otro"], default="personal")
    p_padd.add_argument("--priority", choices=["P1", "P2", "P3", "P4"], default="P3")
    p_padd.add_argument("--target-date", help="Fecha objetivo (YYYY-MM-DD)")
    p_padd.add_argument("--desc", default="", help="Descripción")
    
    p_plist = subparsers.add_parser("project-list", help="Lista proyectos")
    p_plist.add_argument("--status", choices=["activo", "pausado", "completado", "cancelado"])
    
    # Commitments
    p_cadd = subparsers.add_parser("commitment-add", help="Añade un compromiso")
    p_cadd.add_argument("--counterparty", required=True, help="Persona o entidad con quien se tiene el compromiso")
    p_cadd.add_argument("--title", required=True, help="Título del compromiso")
    p_cadd.add_argument("--due-date", required=True, help="Fecha límite (YYYY-MM-DD)")
    p_cadd.add_argument("--importance", choices=["critica", "alta", "media", "baja"], default="alta")
    p_cadd.add_argument("--desc", default="", help="Detalles adicionales")
    p_cadd.add_argument("--project-id", type=int, help="ID de proyecto relacionado")
    
    p_clist = subparsers.add_parser("commitment-list", help="Lista compromisos")
    p_clist.add_argument("--status", choices=["pendiente", "cumplido", "renegociado", "cancelado"])
    
    # Notes & Decisions
    p_nadd = subparsers.add_parser("note-add", help="Añade una nota o idea")
    p_nadd.add_argument("--title", required=True, help="Título")
    p_nadd.add_argument("--content", required=True, help="Contenido")
    p_nadd.add_argument("--category", choices=["idea", "nota", "recurso", "referencia"], default="nota")
    p_nadd.add_argument("--tags", default="", help="Etiquetas separadas por comas")
    p_nadd.add_argument("--project-id", type=int)
    
    p_nlist = subparsers.add_parser("note-list", help="Busca notas")
    p_nlist.add_argument("--search", help="Término de búsqueda")
    p_nlist.add_argument("--category")
    
    p_dadd = subparsers.add_parser("decision-add", help="Registra una decisión clave")
    p_dadd.add_argument("--title", required=True, help="Título de la decisión")
    p_dadd.add_argument("--context", required=True, help="Contexto o problema")
    p_dadd.add_argument("--decision", required=True, help="Decisión adoptada")
    p_dadd.add_argument("--rationale", default="", help="Razón o justificación")
    p_dadd.add_argument("--impact", default="", help="Impacto esperado")
    p_dadd.add_argument("--project-id", type=int)
    
    subparsers.add_parser("decision-list", help="Lista decisiones históricas")
    
    # Planning & Reports
    p_plan = subparsers.add_parser("plan-day", help="Planifica el día y detecta conflictos")
    p_plan.add_argument("--date", help="Fecha objetivo (YYYY-MM-DD, por defecto hoy)")
    
    subparsers.add_parser("report-daily", help="Genera reporte del día")

    args = parser.parse_args()
    if not args.command:
        # Si se ejecuta sin parámetros, abre el menú interactivo amigable
        interactive_menu()
        return

    if args.command == "init-db":
        init_db()
    elif args.command == "backup":
        backup_db()
    elif args.command == "integrity":
        integrity_check()
    elif args.command == "sync":
        sync_markdown()
    elif args.command == "session-start":
        session_start()
    elif args.command == "session-end":
        session_end(args.summary)
    elif args.command == "task-add":
        task_add(args.title, args.project_id, args.priority, args.due_date, args.due_time, args.est_minutes, args.desc)
    elif args.command == "task-list":
        task_list(args.status, args.priority, args.project_id, args.due_before, args.json)
    elif args.command == "task-done":
        task_done(args.id)
    elif args.command == "task-update":
        task_update(args.id, args.title, args.status, args.priority, args.due_date, args.due_time, args.desc)
    elif args.command == "project-add":
        project_add(args.name, args.category, args.priority, args.target_date, args.desc)
    elif args.command == "project-list":
        project_list(args.status)
    elif args.command == "commitment-add":
        commitment_add(args.counterparty, args.title, args.due_date, args.importance, args.desc, args.project_id)
    elif args.command == "commitment-list":
        commitment_list(args.status)
    elif args.command == "note-add":
        note_add(args.title, args.content, args.category, args.tags, args.project_id)
    elif args.command == "note-list":
        note_list(args.search, args.category)
    elif args.command == "decision-add":
        decision_add(args.title, args.context, args.decision, args.rationale, args.impact, args.project_id)
    elif args.command == "decision-list":
        decision_list()
    elif args.command == "plan-day":
        plan_day(args.date)
    elif args.command == "report-daily":
        report_daily()

if __name__ == "__main__":
    main()
