---
name: reporting
description: >-
  Genera informes ejecutivos diarios y semanales de avance, productividad, tareas completadas,
  actividades atrasadas y decisiones tomadas en NEXUS. Usa esta habilidad cuando el usuario pida
  "Hazme un resumen del día", "Reporte de la semana", "¿Cómo fue mi progreso?" o "Genera un balance".
---

# Habilidad: Elaboración de Informes (reporting)

Esta habilidad sintetiza el trabajo realizado, compara lo completado con lo planificado y archiva formalmente los informes en `reports/daily/` y `reports/weekly/`.

## 1. Contenido de los Informes
Cada informe diario incluye 4 secciones claras:
1. **Actividades Completadas Hoy**: Listado con hora de cierre y proyecto.
2. **Pendientes y Alertas**: Tareas que siguen abiertas y elementos urgentes para el día siguiente.
3. **Notas e Ideas Registradas**: Nuevas entradas de conocimiento ingresadas.
4. **Decisiones Clave**: Acuerdos o determinaciones estratégicas del día.

## 2. Procedimiento de Ejecución

### A. Generar el informe del día
Ejecuta:
```powershell
python scripts/nexus_core.py report-daily
```
*El sistema generará el archivo `reports/daily/YYYY-MM-DD.md` y presentará un resumen ejecutivo al usuario.*

### B. Consulta de informes anteriores
Para revisar el balance de una fecha previa:
- Lee el archivo correspondiente en `reports/daily/<fecha>.md`.

## 3. Criterios de Finalización
- Archivo Markdown generado y guardado en `reports/daily/` o `reports/weekly/`.
- Estadísticas precisas calculadas a partir de la base de datos real (sin invención de cifras).
- Presentación concisa al usuario destacando logros del día y alertas para la siguiente jornada.
