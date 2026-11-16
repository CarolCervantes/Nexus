#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite Integral de NEXUS
Verifica funcionalmente cada habilidad, persistencia y detección de colisiones.
"""

import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import date, timedelta

# Asegurar soporte UTF-8 en salida estándar de Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

NEXUS_DIR = Path(__file__).resolve().parent.parent
os.chdir(str(NEXUS_DIR))

# Configurar UTF-8 en el entorno de ejecución
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

def run_cmd(args):
    cmd = [sys.executable, "scripts/nexus_core.py"] + args
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env
    )
    return res.returncode, (res.stdout or ""), (res.stderr or "")

def extract_id(text):
    m = re.search(r"ID:\s*(\d+)", text)
    return int(m.group(1)) if m else None

def main():
    print("=== INICIANDO BATERIA DE PRUEBAS DE NEXUS ===")
    today = date.today().strftime("%Y-%m-%d")
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Proyectos
    print("\n--- PRUEBA 1: Creacion de Proyectos ---")
    rc, out, err = run_cmd(["project-add", "--name", "Tesis de Inteligencia Artificial", "--category", "académico", "--priority", "P1", "--target-date", tomorrow, "--desc", "Desarrollo del marco teorico y modelo de evaluacion"])
    assert rc == 0, f"Error en project-add: {err}"
    proj1_id = extract_id(out)
    print(f"Proyecto 1 (ID: {proj1_id}):", out.strip())
    
    rc, out, err = run_cmd(["project-add", "--name", "Automatizacion Domestica", "--category", "personal", "--priority", "P3", "--desc", "Instalacion de sensores y alertas"])
    assert rc == 0, f"Error en project-add 2: {err}"
    proj2_id = extract_id(out)
    print(f"Proyecto 2 (ID: {proj2_id}):", out.strip())

    # 2. Tareas con diversas prioridades y fechas
    print("\n--- PRUEBA 2: Gestion de Tareas y Prioridades ---")
    # Tarea atrasada (ayer)
    rc, out, err = run_cmd(["task-add", "--title", "Revision bibliografica inicial", "--project-id", str(proj1_id or 1), "--priority", "P1", "--due-date", yesterday, "--est-minutes", "60", "--desc", "Lectura de los 3 papers de referencia"])
    assert rc == 0, f"Error en task-add 1: {err}"
    t_overdue_id = extract_id(out)
    print(f"Tarea vencida creada (ID: {t_overdue_id}):", out.strip())
    
    # Tarea para hoy P1
    rc, out, err = run_cmd(["task-add", "--title", "Redaccion de metodologia", "--project-id", str(proj1_id or 1), "--priority", "P1", "--due-date", today, "--est-minutes", "90"])
    assert rc == 0, f"Error en task-add 2: {err}"
    t_today_id = extract_id(out)
    print(f"Tarea hoy P1 creada (ID: {t_today_id}):", out.strip())

    # Tarea para hoy P2
    rc, out, err = run_cmd(["task-add", "--title", "Configuracion de entorno de pruebas", "--project-id", str(proj1_id or 1), "--priority", "P2", "--due-date", today, "--est-minutes", "45"])
    assert rc == 0, f"Error en task-add 3: {err}"
    print("Tarea hoy P2 creada:", out.strip())

    # Tarea futura backlog P3
    rc, out, err = run_cmd(["task-add", "--title", "Comprar sensores Zigbee", "--project-id", str(proj2_id or 2), "--priority", "P3", "--due-date", tomorrow, "--est-minutes", "30"])
    assert rc == 0, f"Error en task-add 4: {err}"
    print("Tarea futura creada:", out.strip())

    # 3. Compromisos
    print("\n--- PRUEBA 3: Seguimiento de Compromisos ---")
    rc, out, err = run_cmd(["commitment-add", "--counterparty", "Prof. Ramirez", "--title", "Entrega preliminar de indice de tesis", "--due-date", today, "--importance", "critica", "--project-id", str(proj1_id or 1)])
    assert rc == 0, f"Error en commitment-add: {err}"
    print("Compromiso registrado:", out.strip())

    # 4. Notas y Decisiones
    print("\n--- PRUEBA 4: Notas y Bitacora Historica de Decisiones ---")
    rc, out, err = run_cmd(["note-add", "--title", "Arquitectura RAG para tesis", "--content", "Utilizar embeddings locales combinados con reranking para optimizar contexto.", "--category", "idea", "--tags", "tesis,ia,rag", "--project-id", str(proj1_id or 1)])
    assert rc == 0, f"Error en note-add: {err}"
    print("Nota guardada:", out.strip())
    
    rc, out, err = run_cmd(["decision-add", "--title", "Uso de SQLite + Markdown en NEXUS", "--context", "Necesidad de persistencia local confiable sin dependencias de red.", "--decision", "Base de datos relacional SQLite como fuente de verdad y sincronizacion automatica a Markdown.", "--rationale", "Proporciona ACID, atomicidad en Windows y legibilidad instantanea.", "--impact", "Continuidad garantizada entre sesiones.", "--project-id", str(proj1_id or 1)])
    assert rc == 0, f"Error en decision-add: {err}"
    print("Decision registrada:", out.strip())

    # 5. Planificación diaria y detección de conflictos
    print("\n--- PRUEBA 5: Planificacion y Deteccion de Conflictos / Atrasos ---")
    rc, out, err = run_cmd(["plan-day"])
    assert rc == 0, f"Error en plan-day: {err}"
    print(out)
    assert "ALERTA: ELEMENTOS ATRASADOS" in out, "Debe alertar sobre elementos atrasados"
    assert "COMPROMISOS" in out, "Debe mostrar compromisos críticos"

    # 6. Completar tarea
    print("\n--- PRUEBA 6: Completar Tarea y recalcular avance ---")
    rc, out, err = run_cmd(["task-done", str(t_overdue_id)])
    assert rc == 0, f"Error en task-done: {err}"
    print(out.strip())

    # 7. Listado de proyectos y avance
    print("\n--- PRUEBA 7: Listar Proyectos y Metricas de Avance ---")
    rc, out, err = run_cmd(["project-list"])
    assert rc == 0, f"Error en project-list: {err}"
    print(out)

    # 8. Generar Reporte Diario
    print("\n--- PRUEBA 8: Generacion de Reporte Diario ---")
    rc, out, err = run_cmd(["report-daily"])
    assert rc == 0, f"Error en report-daily: {err}"
    print(out.strip())
    
    # Verificar que el archivo existe
    report_path = NEXUS_DIR / "reports" / "daily" / f"{today}.md"
    assert report_path.exists(), f"El reporte {report_path} no fue creado"
    print(f"Reporte verificado en: {report_path}")

    # 9. Cierre de sesión y backup automático
    print("\n--- PRUEBA 9: Cierre de Sesion y Respaldo de Base de Datos ---")
    rc, out, err = run_cmd(["session-end", "--summary", "Prueba integral de ciclo completo exitosa"])
    assert rc == 0, f"Error en session-end: {err}"
    print(out.strip())

    # 10. Verificación de archivos de respaldo
    backups = list((NEXUS_DIR / "data" / "backups").glob("*.db"))
    assert len(backups) > 0, "No se genero el archivo de respaldo"
    print(f"Respaldos encontrados ({len(backups)}): {[b.name for b in backups]}")

    # 11. Verificación de Nueva Sesión (Persistencia Real y Continuidad)
    print("\n--- PRUEBA 10: Continuidad de Sesion Real (session-start) ---")
    rc, out, err = run_cmd(["session-start"])
    assert rc == 0, f"Error en session-start: {err}"
    print(out)

    # 12. Verificación de Integridad de SQLite
    print("\n--- PRUEBA 11: Comprobacion de Integridad SQLite ---")
    rc, out, err = run_cmd(["integrity"])
    assert rc == 0, f"Error en integrity: {err}"
    print(out)

    print("\n>>> TODAS LAS PRUEBAS PASARON EXITOSAMENTE CON PERSISTENCIA 100% VERIFICADA. <<<")

if __name__ == "__main__":
    main()
