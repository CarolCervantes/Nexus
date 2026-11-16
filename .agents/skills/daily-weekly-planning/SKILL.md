---
name: daily-weekly-planning
description: >-
  Organiza y planifica agendas diarias y semanales en NEXUS, detecta tareas atrasadas,
  calcula sobrecarga de trabajo y propone el orden óptimo de ejecución. Usa esta habilidad cuando
  el usuario pida "Organiza mi día", "Planifica mi semana", "¿Qué debería hacer primero?" o "Revisa mis prioridades".
---

# Habilidad: Planificación Diaria y Semanal (daily-weekly-planning)

Esta habilidad analiza las tareas asignadas para una fecha, los compromisos con terceros y las actividades vencidas para estructurar un plan de trabajo realista y sin fricción.

## 1. Reglas de Planificación
1. **Límite de Carga Diaria**: El total estimado no debe superar las 7.0 horas efectivas de trabajo al día.
2. **Jerarquía de Ejecución**:
   - Primero: Tareas y compromisos **vencidos**.
   - Segundo: Tareas **P1** del día.
   - Tercero: Compromisos con terceros programados para la fecha.
   - Cuarto: Tareas **P2** y bloques de concentración.
   - Quinto: Tareas **P3** rutinarias si queda tiempo disponible.
3. **Detección de Conflictos**:
   - Si dos tareas coinciden en la misma hora o superan la capacidad disponible, NEXUS debe señalarlo de inmediato y sugerir mover las menos prioritarias.

## 2. Procedimiento de Ejecución

### A. Planificar la jornada actual
Ejecuta:
```powershell
python scripts/nexus_core.py plan-day
```
*Si se desea planificar un día futuro específico:*
```powershell
python scripts/nexus_core.py plan-day --date YYYY-MM-DD
```

### B. Evaluación de la salida
El comando reportará:
- Lista de elementos atrasados (alerta roja).
- Advertencia si la carga supera las 7 horas.
- Compromisos externos críticos del día.
- Secuencia ordenada recomendada de ejecución.

### C. Ajuste proactivo
Si se detecta sobrecarga, propone al usuario:
*"Hoy tienes X horas asignadas. Recomiendo aplazar la tarea ID Y (P3) al jueves para asegurar el cumplimiento de la entrega crítica P1."*

## 3. Criterios de Finalización
- Plan presentado con formato limpio, tiempos estimados y secuencia de acción clara.
- Ningún conflicto de horario o fecha límite ignorado.
- `memory/operational/current_state.md` refleja el foco del día.
