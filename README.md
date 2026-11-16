# NEXUS: Agente Personal Persistente de Organización y Gestión Cotidiana

**NEXUS** es un asistente personal inteligente diseñado para acompañarte a largo plazo, organizar tu vida cotidiana, proyectos personales y académicos, preservar memoria útil y mantener continuidad real entre sesiones en Google Antigravity.

A diferencia de un chatbot convencional, NEXUS opera sobre un **sistema híbrido de persistencia real**: una base de datos relacional local en SQLite (`data/nexus.db`) como fuente de verdad atómica, sincronizada automáticamente con vistas legibles en Markdown (`memory/`, `tasks/`, `projects/`, `reports/`).

---

## 1. Estructura del Sistema

```text
nexus/
├── AGENTS.md                           # Instrucciones maestras de identidad y protocolos
├── README.md                           # Manual de usuario, arquitectura y administración
├── .agents/
│   ├── rules/                          # Reglas de comportamiento y seguridad de Antigravity
│   │   ├── 01-safety-and-integrity.md  # Veracidad, guardrails y confirmación de acciones
│   │   ├── 02-memory-protocol.md       # Jerarquía de memoria y deduplicación
│   │   └── 03-interaction-style.md     # Estilo conciso y mapeo de lenguaje natural
│   └── skills/                         # Habilidades especializadas con SKILL.md
│       ├── task-management/            # Gestión de tareas y prioridades (P1-P4)
│       ├── daily-weekly-planning/      # Planificación y resolución de conflictos de agenda
│       ├── project-management/         # Ciclo de vida y avance de proyectos
│       ├── knowledge-management/       # Notas, ideas y decisiones documentadas
│       ├── commitment-tracking/        # Seguimiento de acuerdos con terceros
│       ├── reporting/                  # Generación de informes diarios y semanales
│       └── memory-maintenance/         # Respaldo, sincronización y salud de la base de datos
├── memory/
│   ├── permanent/                      # Nivel A: Perfil del usuario y preferencias estables
│   │   ├── user_profile.md
│   │   └── preferences.md
│   ├── operational/                    # Nivel B: Foco del día y contexto vivo
│   │   ├── current_state.md
│   │   └── active_contexts.md
│   └── historical/                     # Nivel C: Bitácora inmutable de decisiones y archivo
│       ├── decisions_log.md
│       └── completed_archive.md
├── data/
│   ├── nexus.db                        # Base de datos relacional SQLite (ACID)
│   ├── schema.sql                      # Definición de tablas, índices y restricciones
│   └── backups/                        # Copias de seguridad automáticas versionadas
├── projects/                           # Fichas de proyectos
├── tasks/                              # Vistas legibles de tareas
│   ├── today.md                        # Tareas asignadas a hoy o vencidas
│   └── backlog.md                      # Tareas futuras o sin fecha asignada
├── logs/
│   ├── operations.log                  # Registro cronológico de operaciones
│   └── sessions.jsonl                  # Bitácora de sesiones
├── reports/                            # Informes y resúmenes estructurados
│   ├── daily/                          # Informes diarios (YYYY-MM-DD.md)
│   └── weekly/                         # Balances semanales
└── scripts/
    ├── nexus_core.py                   # Motor central autónomo en Python (librería estándar)
    ├── nexus_cli.bat                   # Acceso rápido en CMD de Windows
    ├── nexus.ps1                       # Wrapper para PowerShell
    └── test_nexus_suite.py             # Batería de pruebas y verificación de persistencia
```

---

## 2. Sistema de Memoria de Tres Niveles

NEXUS implementa una separación rigurosa para no saturar el contexto de la IA y asegurar que la información relevante siempre esté a mano:

1. **Nivel A: Memoria Permanente (`memory/permanent/`)**:
   - Contiene tu perfil (`user_profile.md`) y tus preferencias operativas (`preferences.md`).
   - Se consulta obligatoriamente al arrancar cualquier sesión.
2. **Nivel B: Memoria Operativa (`memory/operational/` y `tasks/`)**:
   - Refleja el estado del día (`current_state.md`), tareas de hoy (`today.md`), compromisos inminentes y proyectos en marcha.
   - Se actualiza en tiempo real con cada cambio de estado o adición.
3. **Nivel C: Memoria Histórica (`memory/historical/` y `reports/`)**:
   - Bitácora inmutable de decisiones clave (`decisions_log.md`) y archivo de hitos concluidos (`completed_archive.md`).
   - Se consulta bajo demanda cuando se requiere contexto retrospectivo.

---

## 3. Catálogo de Habilidades (.agents/skills/)

| Habilidad | Misión Principal | Activación en Lenguaje Natural |
| :--- | :--- | :--- |
| **`task-management`** | Alta, edición, priorización (P1 a P4) y cierre de tareas. | *"Añade una tarea...", "¿Qué tengo pendiente?", "Terminé la tarea X"* |
| **`daily-weekly-planning`** | Detección de retrasos, balance de carga y secuencia óptima. | *"Organiza mi día", "Planifica mi semana", "¿Qué hago primero?"* |
| **`project-management`** | Estructuración de proyectos, hitos y métricas de avance. | *"Crea el proyecto...", "¿Cómo va el proyecto X?", "Pausa el proyecto..."* |
| **`knowledge-management`** | Ideas, notas técnicas y registro de decisiones estratégicas. | *"Registra esta idea...", "¿Por qué decidimos X?", "Busca mis notas de..."* |
| **`commitment-tracking`** | Acuerdos y entregables con personas o entidades externas. | *"Le prometí a Juan entregar...", "Tengo reunión/entrega con..."* |
| **`reporting`** | Informes ejecutivos diarios y balances de productividad. | *"Hazme un resumen del día", "Balance semanal"* |
| **`memory-maintenance`** | Sincronización DB-Markdown, respaldos y verificación SQLite. | *"Haz un backup", "Verifica la base de datos", "Cierra sesión"* |

---

## 4. Ejemplos de Interacción Natural

Puedes hablar con NEXUS con total naturalidad; el agente mapeará tus instrucciones a las habilidades correspondientes:

- **"Organiza mi día"**:
  NEXUS analiza las tareas del día, detecta si hay alguna tarea vencida, verifica los compromisos externos y te presenta la secuencia recomendada de trabajo priorizada.
- **"Recuérdame entregar el borrador de tesis el viernes"**:
  Calcula la fecha exacta, crea la tarea con prioridad P1/P2 y la asocia al proyecto correspondiente.
- **"¿Qué decisiones tomamos anteriormente sobre la base de datos?"**:
  Consulta `memory/historical/decisions_log.md` y te expone el contexto, la decisión adoptada y su justificación.
- **"Registra esta idea: implementar un motor de búsqueda semántica local"**:
  Guarda la nota categorizada como `idea`, añade las etiquetas pertinentes y la indexa para búsquedas futuras.
- **"Hazme un resumen de hoy"**:
  Genera el balance ejecutivo en `reports/daily/YYYY-MM-DD.md` detallando lo concluido, los pendientes y las decisiones tomadas.

---

## 5. Referencia de Comandos CLI (`nexus_core.py`)

El motor `scripts/nexus_core.py` no requiere dependencias externas (utiliza únicamente la librería estándar de Python 3):

```powershell
# INICIO Y CIERRE DE SESIÓN
python scripts/nexus_core.py session-start
python scripts/nexus_core.py session-end --summary "Avance en marco teórico"

# GESTIÓN DE TAREAS
python scripts/nexus_core.py task-add --title "Revisar capítulo 2" --priority P1 --due-date 2026-11-15 --est-minutes 60
python scripts/nexus_core.py task-list --status pendiente
python scripts/nexus_core.py task-done <ID>
python scripts/nexus_core.py task-update <ID> --priority P2 --due-date 2026-11-18

# GESTIÓN DE PROYECTOS
python scripts/nexus_core.py project-add --name "Tesis de Grado" --category académico --priority P1 --target-date 2026-12-01
python scripts/nexus_core.py project-list

# COMPROMISOS CON TERCEROS
python scripts/nexus_core.py commitment-add --counterparty "Prof. Martínez" --title "Envío de avance" --due-date 2026-11-20 --importance critica
python scripts/nexus_core.py commitment-list

# NOTAS Y DECISIONES
python scripts/nexus_core.py note-add --title "RAG con SQLite" --content "Integrar FTS5 para búsquedas textuales rápidas." --category idea --tags "ia,sqlite"
python scripts/nexus_core.py note-list --search "SQLite"
python scripts/nexus_core.py decision-add --title "Migración de arquitectura" --context "..." --decision "..." --rationale "..."

# PLANIFICACIÓN Y REPORTES
python scripts/nexus_core.py plan-day
python scripts/nexus_core.py report-daily

# MANTENIMIENTO Y RESPALDOS
python scripts/nexus_core.py sync
python scripts/nexus_core.py backup
python scripts/nexus_core.py integrity
```

---

## 6. Políticas de Seguridad y Guardrails

1. **Veracidad Absoluta**: NEXUS nunca afirmará haber guardado o completado una tarea sin haber ejecutado la mutación en la base de datos real.
2. **Cero Credenciales en Texto Plano**: Está estrictamente prohibido guardar contraseñas, claves privadas o tokens en las notas o en la base de datos.
3. **Acciones Irreversibles**: Borrados masivos o eliminación física de proyectos requieren confirmación explícita del usuario.
4. **Trazabilidad Completa**: Cada operación queda registrada con marca de tiempo en `audit_log` y en `logs/operations.log`.

---

## 7. Mantenimiento y Extensión

- **Crear una nueva habilidad**: Crea una carpeta en `.agents/skills/<nombre-habilidad>/` con su respectivo `SKILL.md` (frontmatter YAML con `name` y `description`).
- **Añadir nuevas reglas**: Agrega un archivo `.md` en `.agents/rules/` con las políticas de comportamiento que desees que Antigravity aplique en cada turno.
- **Respaldos**: Los backups automáticos se guardan en `data/backups/`. Para restaurar, simplemente copia el respaldo deseado sobre `data/nexus.db`.

---

## 8. Recomendación de Espacio de Trabajo en Antigravity

Para que Antigravity cargue de manera automática las reglas de `AGENTS.md`, las directivas de `.agents/rules/` y las habilidades de `.agents/skills/`:
1. En el menú o selector de carpetas de Antigravity, abre la carpeta:
   `C:\Users\HP\Downloads\nexus`
2. Configúrala como tu **Active Workspace**.
3. De esta forma, cada conversación que inicies en ese workspace tendrá a NEXUS activo de forma nativa e inmediata.
