---
name: project-management
description: >-
  Administra proyectos personales, académicos y profesionales en NEXUS, organizando hitos,
  asociando tareas y calculando porcentajes de avance. Usa esta habilidad cuando el usuario pida
  crear un nuevo proyecto, consultar el avance de un proyecto, pausar o cerrar un proyecto o vincular tareas a un proyecto.
---

# Habilidad: Gestión de Proyectos (project-management)

Esta habilidad coordina la estructura global de proyectos, permitiendo agrupar tareas, notas y decisiones bajo un mismo objetivo con trazabilidad completa.

## 1. Categorías de Proyecto
- `personal`: Hábitos, salud, finanzas, viajes o iniciativas individuales.
- `académico`: Asignaturas, tesis, trabajos de investigación o cursos.
- `profesional`: Emprendimientos, clientes, entregables de trabajo o código.

## 2. Procedimiento de Ejecución

### A. Crear un nuevo proyecto
Ejecuta:
```powershell
python scripts/nexus_core.py project-add --name "Nombre del Proyecto" --category académico --priority P2 --target-date YYYY-MM-DD --desc "Objetivos y alcance del proyecto"
```

### B. Listar proyectos y verificar progreso
```powershell
# Listar todos los activos
python scripts/nexus_core.py project-list --status activo

# Listar todos los proyectos sin importar estado
python scripts/nexus_core.py project-list
```
El listado muestra:
- ID, prioridad, estado, categoría, porcentaje de avance (tareas completadas / total) y nombre.

### C. Vincular tareas a un proyecto existente
Al crear o actualizar una tarea, especifica el ID del proyecto:
```powershell
python scripts/nexus_core.py task-add --title "Capítulo 1 de la memoria técnica" --project-id 1 --priority P2 --due-date YYYY-MM-DD
```

## 3. Criterios de Finalización
- El proyecto queda registrado en la tabla `projects` con su slug e ID único.
- Las tareas vinculadas reflejan la llave foránea `project_id`.
- Se actualizan las vistas en `projects/` y el recuento en `memory/operational/current_state.md`.
- El agente informa el estado actual del proyecto de forma estructurada.
