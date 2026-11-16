#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite de Verificación de Backend de NEXUS
Prueba todos los endpoints, autenticación, base de datos e IA.
"""

import sys
import os
from pathlib import Path

# Configurar UTF-8 en salida estándar de Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Agregar raíz de backend al path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

# Asegurar SQLite local temporal para pruebas
os.environ["DATABASE_URL"] = f"sqlite:///{BACKEND_DIR / 'test_nexus.db'}"

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine

def run_tests():
    print("=== INICIANDO PRUEBAS DE BACKEND NEXUS ===")
    
    # 1. Recrear tablas de prueba
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    
    # 2. Health check
    print("\n1. Verificando Health Check...")
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Error en health check: {resp.text}"
    print("   -> OK:", resp.json())

    # 3. Registro de usuario
    print("\n2. Probando Registro de Usuario...")
    user_payload = {
        "email": "usuario@nexus.com",
        "password": "PasswordSeguro2026!",
        "full_name": "Santiago Arquitecto",
        "timezone": "America/Bogota"
    }
    reg_resp = client.post("/api/auth/register", json=user_payload)
    assert reg_resp.status_code == 201, f"Fallo registro: {reg_resp.text}"
    auth_data = reg_resp.json()
    token = auth_data["access_token"]
    assert token, "No se generó el token JWT"
    print("   -> Usuario registrado exitosamente. Token JWT recibido.")

    headers = {"Authorization": f"Bearer {token}"}

    # 4. Login
    print("\n3. Probando Login con Credenciales...")
    login_resp = client.post("/api/auth/login", json={
        "email": "usuario@nexus.com",
        "password": "PasswordSeguro2026!"
    })
    assert login_resp.status_code == 200, f"Fallo login: {login_resp.text}"
    print("   -> Login OK:", login_resp.json()["user"]["email"])

    # 5. Perfil de usuario (/api/auth/me)
    print("\n4. Verificando Perfil del Usuario...")
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    print("   -> Perfil verificado:", me_resp.json()["full_name"])

    # 6. Proyectos
    print("\n5. Creando Proyecto de Prueba...")
    proj_resp = client.post("/api/projects/", json={
        "name": "Lanzamiento PWA NEXUS",
        "category": "profesional",
        "priority": "P1",
        "description": "Despliegue y configuración en la nube"
    }, headers=headers)
    assert proj_resp.status_code == 201
    project_id = proj_resp.json()["id"]
    print(f"   -> Proyecto creado [ID {project_id}]:", proj_resp.json()["name"])

    # 7. Tareas
    print("\n6. Creando y Completando Tareas...")
    task_resp = client.post("/api/tasks/", json={
        "title": "Configurar Frontend Vite PWA",
        "project_id": project_id,
        "priority": "P1",
        "estimated_minutes": 60,
        "due_date": "2026-11-15"
    }, headers=headers)
    assert task_resp.status_code == 201
    task_id = task_resp.json()["id"]
    print(f"   -> Tarea creada [ID {task_id}]:", task_resp.json()["title"])

    # Marcar tarea como completada
    done_resp = client.post(f"/api/tasks/{task_id}/complete", headers=headers)
    assert done_resp.status_code == 200
    assert done_resp.json()["status"] == "completada"
    print("   -> Tarea marcada como completada exitosamente.")

    # 8. Notas
    print("\n7. Guardando Nota de Conocimiento...")
    note_resp = client.post("/api/notes/", json={
        "title": "Arquitectura Serverless PWA",
        "content": "Vite PWA con Service Worker para soporte offline y PostgreSQL remoto.",
        "category": "recurso",
        "tags": "pwa,cloud,arquitectura"
    }, headers=headers)
    assert note_resp.status_code == 201
    print("   -> Nota guardada:", note_resp.json()["title"])

    # 9. Finanzas
    print("\n8. Registrando Movimiento Financiero...")
    fin_resp = client.post("/api/finances/", json={
        "type": "gasto",
        "category": "servicios",
        "amount": 25000.0,
        "currency": "COP",
        "description": "Dominio web para NEXUS"
    }, headers=headers)
    assert fin_resp.status_code == 201
    print("   -> Gasto registrado:", fin_resp.json()["amount"], fin_resp.json()["currency"])

    # 10. Dashboard Summary
    print("\n9. Consultando Dashboard Summary...")
    dash_resp = client.get("/api/dashboard/summary", headers=headers)
    assert dash_resp.status_code == 200
    metrics = dash_resp.json()["metrics"]
    print("   -> Métricas obtenidas:", metrics)

    # 11. Chat con IA y Ejecución de Herramientas
    print("\n10. Probando Chat con IA y Ejecución de Herramientas...")
    chat_resp = client.post("/api/chat/send", json={
        "message": "Añade una tarea urgente para entregar informe final"
    }, headers=headers)
    assert chat_resp.status_code == 200
    ai_msg = chat_resp.json()
    print("   -> Respuesta de NEXUS:", ai_msg["content"])
    print("   -> Herramientas ejecutadas:", ai_msg.get("tool_calls"))

    # Verificar que la tarea realmente fue creada en la BD
    tasks_check = client.get("/api/tasks/", headers=headers).json()
    created_titles = [t["title"] for t in tasks_check]
    print(f"   -> Tareas registradas en BD ({len(tasks_check)}):", created_titles)
    assert any("informe final" in t.lower() for t in created_titles), "La herramienta no persistió la tarea en BD"
    print("   -> Verificación de acción real superada con éxito.")

    # Limpiar BD de test
    test_db = BACKEND_DIR / "test_nexus.db"
    if test_db.exists():
        try:
            test_db.unlink()
        except Exception:
            pass

    print("\n>>> TODAS LAS PRUEBAS DE BACKEND PASARON EXITOSAMENTE (11/11). <<<")

if __name__ == "__main__":
    run_tests()
