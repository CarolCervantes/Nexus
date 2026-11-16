# Regla 02: Protocolo del Sistema de Memoria Tripartita

NEXUS implementa una jerarquía de memoria estructurada para garantizar relevancia sin saturar el contexto del modelo.

## 1. Niveles de Memoria

### Nivel A: Memoria Permanente (`memory/permanent/`)
- **Contenido**: Perfil del usuario, horarios de trabajo, metodologías preferidas (Pomodoro, Timeblocking, Eisenhower), convenciones fijas.
- **Acceso**: Lectura obligatoria al inicio de la sesión.
- **Modificación**: Solo cuando el usuario exprese una preferencia duradera o cambie su forma de trabajo habitual.

### Nivel B: Memoria Operativa (`memory/operational/` y `tasks/`)
- **Contenido**: Estado vivo del día (`current_state.md`, `tasks/today.md`), tareas activas, compromisos de la semana, proyectos en ejecución.
- **Acceso**: Lectura al inicio y actualización en tiempo real con cada adición o cambio de estado.
- **Modificación**: Continua durante la jornada.

### Nivel C: Memoria Histórica (`memory/historical/` y `reports/`)
- **Contenido**: Bitácora inmutable de decisiones tomadas (`decisions_log.md`), archivo de tareas completadas (`completed_archive.md`) e informes pasados.
- **Acceso**: Bajo demanda cuando el usuario pregunte "¿Por qué decidimos...?", "¿Qué acordamos sobre...?" o al generar balances retrospectivos.
- **Modificación**: Al registrar formalmente una decisión o al cerrar proyectos e hitos.

## 2. Reglas de Filtrado y Deduplicación
- **No guardar transcripciones crudas**: Extraer únicamente hechos atómicos, compromisos, plazos y directivas.
- **Evitar duplicados**: Antes de insertar una tarea o nota, verificar si ya existe un registro similar. Si existe, actualizar el registro existente en lugar de duplicarlo.
- **Sincronización**: Mantener sincronizados SQLite y los archivos Markdown ejecutando `python scripts/nexus_core.py sync`.
