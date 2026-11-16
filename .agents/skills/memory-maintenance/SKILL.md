---
name: memory-maintenance
description: >-
  Mantiene la persistencia y salud del agente NEXUS: sincroniza base de datos SQLite con vistas Markdown,
  genera copias de seguridad versionadas, audita la integridad y consolida la memoria. Usa esta habilidad
  al cerrar la sesión, al detectar discrepancias entre archivos o cuando el usuario pida hacer backup o revisar el estado del sistema.
---

# Habilidad: Mantenimiento y Actualización de Memoria (memory-maintenance)

Esta habilidad asegura que la memoria de NEXUS sea resiliente frente a fallos, reinicios o cierres de sesión de Antigravity, garantizando integridad física y consistencia documental.

## 1. Tareas de Mantenimiento

### A. Sincronización Manual DB -> Markdown
Si se han realizado cambios directos o se desea refrescar los archivos de consulta rápida:
```powershell
python scripts/nexus_core.py sync
```
Actualiza:
- `tasks/today.md`
- `tasks/backlog.md`
- `memory/operational/current_state.md`
- `memory/historical/decisions_log.md`

### B. Creación de Copia de Seguridad (Backup)
```powershell
python scripts/nexus_core.py backup
```
- Genera un archivo con marca de tiempo en `data/backups/nexus_backup_YYYYMMDD_HHMMSS.db`.
- Registra el evento en `audit_log`.

### C. Comprobación de Integridad Física
```powershell
python scripts/nexus_core.py integrity
```
- Ejecuta `PRAGMA integrity_check` en SQLite.
- Reporta el recuento de registros en todas las tablas del sistema.

### D. Protocolo de Cierre de Sesión Seguro
Al terminar la sesión o jornada de trabajo:
```powershell
python scripts/nexus_core.py session-end --summary "Resumen de lo trabajado en esta sesión"
```
Este comando ejecuta automáticamente la sincronización, el respaldo versionado y el cierre de sesión en `sessions`.

## 2. Criterios de Finalización
- `PRAGMA integrity_check` responde `ok`.
- Copia de seguridad válida creada en `data/backups/`.
- Archivos en `memory/` y `tasks/` reflejan el estado exacto de SQLite.
