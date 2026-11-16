---
name: commitment-tracking
description: >-
  Realiza seguimiento de promesas, entregables, acuerdos y fechas críticas contraídas con terceros
  (clientes, profesores, equipos o familiares) en NEXUS. Usa esta habilidad cuando el usuario mencione
  un acuerdo con otra persona, prometa entregar algo para cierta fecha o pregunte qué compromisos tiene pendientes.
---

# Habilidad: Seguimiento de Compromisos (commitment-tracking)

Los compromisos representan acuerdos donde la reputación o el cumplimiento del usuario están en juego frente a una contraparte externa. Esta habilidad previene olvidos y anticipa vencimientos.

## 1. Niveles de Importancia
- `critica`: Compromisos con consecuencias legales, contractuales o académicas graves si se incumplen.
- `alta`: Entregas a clientes, jefes o profesores principales.
- `media`: Acuerdos con pares o entregables secundarios.
- `baja`: Promesas informales de baja fricción.

## 2. Procedimiento de Ejecución

### A. Registrar un nuevo compromiso
Ejecuta:
```powershell
python scripts/nexus_core.py commitment-add --counterparty "Prof. García" --title "Entrega del borrador de tesis" --due-date YYYY-MM-DD --importance critica --desc "Enviar PDF y código fuente por correo antes de las 18:00"
```

### B. Consultar compromisos pendientes
```powershell
# Listar todos los pendientes ordenados por urgencia
python scripts/nexus_core.py commitment-list --status pendiente
```

### C. Alertas de compromiso
Al iniciar el día o planificar (`plan-day`), NEXUS revisará automáticamente si hay compromisos que vencen en las próximas 48 horas o si alguno ha expirado sin registrar cumplimiento.

## 3. Criterios de Finalización
- El compromiso queda guardado en la tabla `commitments`.
- Se asigna contraparte obligatoria y fecha de vencimiento.
- Se integra en la memoria operativa (`current_state.md`) y en las alertas de planificación diaria.
