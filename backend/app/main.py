from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Asegurar registro de todos los modelos SQLAlchemy

# Crear tablas automáticamente al inicio si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API de NEXUS: Personal Life Agent con persistencia en PostgreSQL / SQLite, IA y PWA."
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers modulares
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.tasks import router as tasks_router
from app.api.projects import router as projects_router
from app.api.events import router as events_router
from app.api.notes import router as notes_router
from app.api.memories import router as memories_router
from app.api.finances import router as finances_router
from app.api.dashboard import router as dashboard_router

app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(notes_router, prefix="/api")
app.include_router(memories_router, prefix="/api")
app.include_router(finances_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

@app.get("/api/health", tags=["Salud"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_provider": settings.AI_PROVIDER
    }

# Soporte unificado de Frontend PWA (Single-Port Desktop & Cloud)
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    icons_dir = os.path.join(frontend_dist, "icons")
    if os.path.exists(icons_dir):
        app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")

    @app.get("/manifest.webmanifest", include_in_schema=False)
    async def serve_manifest():
        return FileResponse(os.path.join(frontend_dist, "manifest.webmanifest"), media_type="application/manifest+json")

    @app.get("/sw.js", include_in_schema=False)
    async def serve_sw():
        return FileResponse(os.path.join(frontend_dist, "sw.js"), media_type="application/javascript")

    @app.get("/registerSW.js", include_in_schema=False)
    async def serve_register_sw():
        return FileResponse(os.path.join(frontend_dist, "registerSW.js"), media_type="application/javascript")

    @app.get("/favicon.svg", include_in_schema=False)
    async def serve_favicon():
        return FileResponse(os.path.join(frontend_dist, "favicon.svg"), media_type="image/svg+xml")

    # SPA Fallback para cualquier ruta de la aplicación
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "API endpoint no encontrado"})
        target_file = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
