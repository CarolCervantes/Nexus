---
name: knowledge-management
description: >-
  Registra, indexa y recupera notas, ideas, referencias, recursos y decisiones estratégicas en NEXUS.
  Usa esta habilidad cuando el usuario diga "Registra esta idea", "Guarda esta nota", "¿Qué decisiones tomamos anteriormente?",
  o pida buscar apuntes, enlaces o conocimiento previo.
---

# Habilidad: Gestión de Notas y Conocimiento (knowledge-management)

Esta habilidad asegura que ninguna idea, recurso o decisión clave se pierda, guardándolos tanto en la base de datos para búsqueda indexada como en Markdown para lectura humana directa.

## 1. Clasificación del Conocimiento
- `idea`: Conceptos preliminares, hipótesis o innovaciones por explorar.
- `nota`: Resúmenes de lecturas, apuntes de clase o síntesis operativas.
- `recurso`: Enlaces, referencias bibliográficas, herramientas recomendadas.
- `referencia`: Documentación fija, normas o guías permanentes.

## 2. Procedimiento de Ejecución

### A. Guardar una nota o idea
```powershell
python scripts/nexus_core.py note-add --title "Algoritmo de optimización de rutas" --content "Detalles de la idea..." --category idea --tags "ia,grafos,investigacion"
```
*Si se relaciona con un proyecto específico, incluye `--project-id <ID>`.*

### B. Buscar en notas existentes
```powershell
# Búsqueda por término o palabra clave
python scripts/nexus_core.py note-list --search "optimización"

# Filtrar por categoría
python scripts/nexus_core.py note-list --category idea
```

### C. Registrar una decisión importante (Memoria Histórica)
Cuando se tome una decisión relevante sobre la arquitectura de un proyecto, metodología o compromiso:
```powershell
python scripts/nexus_core.py decision-add --title "Elección de SQLite frente a JSON puro" --context "Se necesitaba almacenamiento con consultas complejas y atomicidad" --decision "Implementar SQLite local con sync a Markdown" --rationale "Garantiza integridad referencial y cero dependencias externas" --impact "Persistencia robusta y velocidad inmediata"
```

### D. Consultar decisiones previas
```powershell
python scripts/nexus_core.py decision-list
```
O consultar directamente el archivo sincronizado `memory/historical/decisions_log.md`.

## 3. Criterios de Finalización
- La nota o decisión queda insertada en `data/nexus.db`.
- Se sincroniza la bitácora histórica en `memory/historical/decisions_log.md`.
- El agente resume la información registrada confirmando tags y categoría asignada.
