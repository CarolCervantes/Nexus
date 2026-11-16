import json
import re
import httpx
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.memory import Memory
from app.models.task import Task
from app.services.tools_service import execute_tool

SYSTEM_INSTRUCTIONS = """Eres NEXUS: Personal Life Agent, el asistente personal inteligente y persistente de organización y gestión cotidiana.
Tu rol es ayudar al usuario a organizar su vida diaria, proyectos, finanzas, ideas y tareas.
Idioma: Español.
Personalidad: Profesional, organizado, práctico, claro, proactivo y adaptable.
Comunicación: Concisa, directa a la solución, orientada a la acción.

Tienes herramientas internas para interactuar con la base de datos real:
1. create_task(title, priority, due_date, estimated_minutes, description)
2. list_pending_tasks()
3. mark_task_completed(task_id)
4. create_note(title, content, category, tags)
5. save_memory(key, value, level, category)
6. add_financial_record(type, category, amount, description)

REGLAS FUNDAMENTALES:
- Cuando el usuario te pida crear o gestionar algo, utiliza la herramienta correspondiente para ejecutar la acción REAL.
- No afirmes haber realizado una acción si no fue ejecutada mediante las herramientas.
- Consulta los recuerdos y contexto provisto antes de solicitar información que ya conoces.
"""

def build_context_prompt(db: Session, user_id: int) -> str:
    """Construye el contexto vivo con memorias permanentes y estado del día."""
    today = date.today().isoformat()
    memories = db.query(Memory).filter(Memory.user_id == user_id, Memory.is_active == True).all()
    tasks = db.query(Task).filter(Task.user_id == user_id, Task.status.in_(["pendiente", "en_progreso"])).limit(10).all()
    
    mem_text = "\n".join([f"- [{m.category}] {m.key}: {m.value}" for m in memories]) or "Sin memorias registradas aún."
    task_text = "\n".join([f"- [ID {t.id} - {t.priority}] {t.title} (Vence: {t.due_date or 'Sin fecha'})" for t in tasks]) or "Sin tareas pendientes."
    
    return f"""
FECHA ACTUAL: {today}

MEMORIA PERSISTENTE DEL USUARIO:
{mem_text}

TAREAS PENDIENTES EN BASE DE DATOS:
{task_text}
"""

class AIService:
    @staticmethod
    async def generate_response(
        db: Session,
        user_id: int,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Procesa el mensaje del usuario, evalúa herramientas y devuelve la respuesta del asistente."""
        context = build_context_prompt(db, user_id)
        
        # 1. Si el proveedor configurado es Ollama:
        if settings.AI_PROVIDER == "ollama":
            try:
                return await AIService._call_ollama_api(db, user_id, user_message, context, conversation_history)
            except Exception:
                return AIService._call_heuristic_engine(db, user_id, user_message, context)

        # 2. Si el proveedor configurado es Groq (Llama 3 en la nube gratuito):
        if settings.GROQ_API_KEY and settings.AI_PROVIDER == "groq":
            try:
                return await AIService._call_groq_api(db, user_id, user_message, context, conversation_history)
            except Exception:
                return AIService._call_heuristic_engine(db, user_id, user_message, context)

        # 3. Si hay clave de Gemini y proveedor configurado, intentar llamada a Gemini API
        if settings.GEMINI_API_KEY and settings.AI_PROVIDER == "gemini":
            try:
                return await AIService._call_gemini_api(db, user_id, user_message, context, conversation_history)
            except Exception:
                return AIService._call_heuristic_engine(db, user_id, user_message, context)
                
        # 3. Motor heurístico de herramientas para respuesta inmediata y confiable
        return AIService._call_heuristic_engine(db, user_id, user_message, context)

    @staticmethod
    def _call_heuristic_engine(db: Session, user_id: int, message: str, context: str) -> Dict[str, Any]:
        """Motor heurístico de herramientas para respuesta inmediata y confiable."""
        msg_lower = message.lower().strip()
        executed_tools = []
        response_text = ""
        
        # A. Detección de creación de tareas
        task_match = re.search(r"(?:añade|agrega|crea|recuérdame|anota)(?: una)? tarea(?:\s+(?:urgente|importante))?(?:\s+(?:llamada|que se llame|de|para))?[:\s]*(.+)", message, re.IGNORECASE)
        if task_match or "recuérdame " in msg_lower or "tarea " in msg_lower:
            title = task_match.group(1).strip() if task_match else message
            # Limpiar prefijos residuales
            title = re.sub(r"^(?:que debo|hacer|de|para|que|llamada|que se llame)\s+", "", title, flags=re.IGNORECASE).strip()
            title = re.sub(r"^(?:urgente\s+|importante\s+)", "", title, flags=re.IGNORECASE).strip()
            
            prio = "P2" if any(w in msg_lower for w in ["urgente", "importante", "hoy", "ya"]) else "P3"
            t_res = execute_tool(db, user_id, "create_task", {
                "title": title[:100],
                "priority": prio,
                "due_date": date.today().isoformat(),
                "estimated_minutes": 45
            })
            executed_tools.append({"tool": "create_task", "result": t_res})
            response_text = f"✅ He creado la tarea: **{title}** (Prioridad: {prio}, Fecha: Hoy). Quedó registrada en tu base de datos y en tu panel de tareas."

        # B. Detección de consulta de pendientes
        elif any(w in msg_lower for w in ["qué tengo pendiente", "que tengo pendiente", "mis tareas", "pendientes", "organiza mi día", "organízame el día", "plan de hoy"]):
            list_res = execute_tool(db, user_id, "list_pending_tasks", {})
            executed_tools.append({"tool": "list_pending_tasks", "result": list_res})
            tasks = list_res.get("tasks", [])
            if not tasks:
                response_text = "Estás completamente al día. No tienes tareas pendientes registradas en este momento. ¿Deseas planificar un nuevo proyecto o registrar alguna actividad?"
            else:
                task_lines = "\n".join([f"- **[{t['priority']}] ID {t['id']}**: {t['title']} (Vence: {t['due_date'] or 'Sin fecha'})" for t in tasks])
                response_text = f"Aquí tienes tus tareas pendientes activas:\n\n{task_lines}\n\n¿Quieres que marquemos alguna como completada o necesitas reorganizar prioridades?"

        # C. Completar tarea
        elif any(w in msg_lower for w in ["completé", "termine", "completada", "marcar como hecha", "ya hice"]):
            id_match = re.search(r"\b(?:id|tarea)?\s*(\d+)\b", msg_lower)
            if id_match:
                tid = int(id_match.group(1))
                c_res = execute_tool(db, user_id, "mark_task_completed", {"task_id": tid})
                executed_tools.append({"tool": "mark_task_completed", "result": c_res})
                if c_res.get("success"):
                    response_text = f"✅ ¡Excelente! He marcado la tarea #{tid} como completada y actualizado tus métricas de progreso."
                else:
                    response_text = f"⚠️ {c_res.get('error')}"
            else:
                response_text = "Por favor indícame el número de ID de la tarea que completaste para actualizar el registro."

        # D. Registrar finanzas (gasto / ingreso)
        elif any(w in msg_lower for w in ["gasté", "gaste", "pagué", "pague", "compré", "ingreso de", "gané"]):
            amount_match = re.search(r"(\d+(?:[.,]\d+)?)", message)
            amount = float(amount_match.group(1).replace(",", ".")) if amount_match else 0.0
            is_income = "ingreso" in msg_lower or "gané" in msg_lower
            f_type = "ingreso" if is_income else "gasto"
            
            f_res = execute_tool(db, user_id, "add_financial_record", {
                "type": f_type,
                "category": "general",
                "amount": amount,
                "description": message[:100]
            })
            executed_tools.append({"tool": "add_financial_record", "result": f_res})
            response_text = f"💰 He registrado el {f_type} por valor de **${amount:,.2f}**. Puedes revisarlo en el módulo de Finanzas."

        # E. Guardar idea o nota
        elif any(w in msg_lower for w in ["guarda esta idea", "registra esta nota", "anota esta idea", "guarda la nota"]):
            content = re.sub(r"^(guarda|registra|anota)\s+(esta|la)\s+(idea|nota)[:\s]*", "", message, flags=re.IGNORECASE)
            n_res = execute_tool(db, user_id, "create_note", {
                "title": content[:40] + ("..." if len(content) > 40 else ""),
                "content": content,
                "category": "idea"
            })
            executed_tools.append({"tool": "create_note", "result": n_res})
            response_text = f"💡 He guardado tu idea en el módulo de Notas y Conocimiento: *\"{content}\"*."

        # F. Respuesta conversacional general
        else:
            response_text = (
                f"Entendido. Como tu asistente personal **NEXUS**, estoy listo para ejecutar lo que necesites: "
                f"puedo registrar una tarea, planificar tu día, crear un proyecto, anotar gastos o consultar tu memoria persistente. "
                f"¿Cómo prefieres que procedamos con esto?"
            )
            
        return {
            "content": response_text,
            "tool_calls": json.dumps([t["tool"] for t in executed_tools]) if executed_tools else None,
            "tool_results": json.dumps(executed_tools) if executed_tools else None
        }

    @staticmethod
    async def _call_gemini_api(
        db: Session,
        user_id: int,
        user_message: str,
        context: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Llamada a la API de Google Gemini con backend proxy seguro."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL_NAME}:generateContent?key={settings.GEMINI_API_KEY}"
        
        contents = [
            {"role": "user", "parts": [{"text": f"{SYSTEM_INSTRUCTIONS}\n\nCONTEXTO:\n{context}"}]},
            {"role": "model", "parts": [{"text": "Entendido. Operaré como NEXUS aplicando estas instrucciones y el contexto persistente."}]}
        ]
        
        # Historial reciente
        for msg in conversation_history[-6:]:
            role = "user" if msg["sender"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            
        contents.append({"role": "user", "parts": [{"text": user_message}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024
            }
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"content": text, "tool_calls": None, "tool_results": None}
            else:
                # Fallback al motor heurístico
                return AIService._call_heuristic_engine(db, user_id, user_message, context)

    @staticmethod
    async def _call_groq_api(
        db: Session,
        user_id: int,
        user_message: str,
        context: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Llamada a la API de Groq Cloud (Llama 3 en la nube gratuito)."""
        heur = AIService._call_heuristic_engine(db, user_id, user_message, context)
        if heur.get("tool_calls"):
            return heur

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": f"{SYSTEM_INSTRUCTIONS}\n\nCONTEXTO PERSISTENTE DEL USUARIO:\n{context}"}
        ]
        for msg in conversation_history[-6:]:
            role = "user" if msg["sender"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": settings.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 1024
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return {"content": text, "tool_calls": None, "tool_results": None}
            else:
                return AIService._call_heuristic_engine(db, user_id, user_message, context)

    @staticmethod
    async def _call_ollama_api(
        db: Session,
        user_id: int,
        user_message: str,
        context: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Llamada a Ollama local (ej. http://localhost:11434)."""
        messages = [
            {"role": "system", "content": f"{SYSTEM_INSTRUCTIONS}\n\nCONTEXTO PERSISTENTE DEL USUARIO:\n{context}"}
        ]
        for msg in conversation_history[-6:]:
            role = "user" if msg["sender"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        # Primero evaluar si hay una acción/herramienta explícita para persistir en BD
        heur = AIService._call_heuristic_engine(db, user_id, user_message, context)
        if heur.get("tool_calls"):
            return heur

        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                url,
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("message", {}).get("content", "")
                return {"content": text, "tool_calls": None, "tool_results": None}
            else:
                return AIService._call_heuristic_engine(db, user_id, user_message, context)
