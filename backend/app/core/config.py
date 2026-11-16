import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(BACKEND_ROOT / ".env")

class Settings:
    PROJECT_NAME: str = "NEXUS: Personal Life Agent"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Seguridad y JWT
    SECRET_KEY: str = os.getenv("JWT_SECRET", "nexus_super_secret_production_key_change_in_env_2026_xyz")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 días para persistencia móvil
    
    # Base de Datos (PostgreSQL en la nube o SQLite local/desarrollo)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nexus_app.db")
    
    # Adaptador de IA
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "gemini-2.5-flash")
    
    # Configuración de Ollama Local
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    
    # Zona horaria por defecto
    DEFAULT_TIMEZONE: str = os.getenv("DEFAULT_TIMEZONE", "America/Bogota")
    
    # Orígenes permitidos para CORS (Frontend web, PWA y local)
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:4173",
        "*"  # Permisivo para desarrollo y URLs temporales de despliegue
    ]

settings = Settings()
