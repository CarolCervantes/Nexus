---
name: task-management
description: >-
  Gestiona tareas pendientes, prioridades (P1-P4), estados (pendiente, en_progreso, completada, cancelada),
  fechas y tiempos límite en NEXUS. Usa esta habilidad cuando el usuario pida añadir una tarea, listar pendientes,
  marcar una tarea como terminada, cambiar prioridades o reorganizar actividades.
---

# Habilidad: Gestión de Tareas (task-management)

Esta habilidad permite a NEXUS crear, consultar, actualizar y completar tareas de manera persistente en la base de datos SQLite y sincronizar las vistas Markdown correspondientes.

## 1. Clasificación de Prioridades
- **P1 (Urgente e Importante)**: Requiere atención hoy mismo. Bloquea otras tareas no esenciales.
- **P2 (Importante)**: Tareas estratégicas o con fecha de entrega próxima.
- **P3 (Normal / Rutinaria)**: Actividades operativas habituales sin urgencia crítica.
- **P4 (Baja)**: Tareas secundarias o del backlog opcional.

## 2. Procedimiento de Ejecución

### A. Añadir una nueva tarea
Ejecuta en consola:
```powershell
python scripts/nexus_core.py task-add --title "Título descriptivo" --priority P2 --due-date YYYY-MM-DD --est-minutes 45
```
*Si la tarea pertenece a un proyecto, incluye `--project-id <ID>`.*

### B. Listar tareas activas o filtrar
```powershell
# Listar todas las pendientes
python scripts/nexus_core.py task-list --status pendiente

# Filtrar por prioridad
python scripts/nexus_core.py task-list --priority P1

# Filtrar por tareas que vencen antes o en una fecha
python scripts/nexus_core.py task-list --due-before YYYY-MM-DD
```

### C. Marcar una tarea como completada
```powershell
python scripts/nexus_core.py task-done <ID_TAREA>
```
*Esto actualiza la fecha `completed_at`, recalcula métricas y sincroniza las vistas Markdown.*

### D. Modificar atributos de una tarea existente
```powershell
python scripts/nexus_core.py task-update <ID_TAREA> --priority P1 --due-date YYYY-MM-DD
```

## 3. Criterios de Finalización
- La tarea se encuentra insertada o actualizada en la tabla `tasks` de `data/nexus.db`.
- Se registró la operación en `logs/operations.log` y en `audit_log`.
- Se generó o actualizó `tasks/today.md` o `tasks/backlog.md`.
- El agente responde al usuario confirmando el ID asignado, título, prioridad y fecha límite de forma concisa.
