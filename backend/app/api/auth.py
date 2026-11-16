from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.memory import Memory
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario registrado con este correo electrónico."
        )
    
    # Crear usuario
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name or "Usuario NEXUS",
        timezone=user_in.timezone or "America/Bogota"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Crear conversación inicial de bienvenida
    welcome_conv = Conversation(user_id=user.id, title="Bienvenida a NEXUS")
    db.add(welcome_conv)
    db.commit()
    db.refresh(welcome_conv)
    
    welcome_msg = Message(
        conversation_id=welcome_conv.id,
        sender="assistant",
        content=(
            f"¡Hola {user.full_name}! Soy **NEXUS**, tu asistente personal de vida y gestión cotidiana. "
            f"Estoy sincronizado en la nube para acompañarte desde tu móvil o tu PC. "
            f"¿Qué te gustaría organizar hoy? Puedes pedirme que registre tareas, organice proyectos, "
            f"guarde notas, anote gastos o planifique tu jornada."
        )
    )
    db.add(welcome_msg)
    
    # Crear memoria permanente base
    db.add(Memory(user_id=user.id, level="permanent", category="preferencia", key="idioma", value="español"))
    db.add(Memory(user_id=user.id, level="permanent", category="preferencia", key="zona_horaria", value=user.timezone))
    db.commit()
    
    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, token_type="bearer", user=user)

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifica tu correo y contraseña."
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Cuenta inactiva.")
        
    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, token_type="bearer", user=user)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
