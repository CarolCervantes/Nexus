from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatMessageSend, MessageResponse, ConversationResponse, ConversationDetail
from app.services.ai_service import AIService
from app.api.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["Asistente Inteligente / Chat"])

@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    convs = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc()).all()
    
    result = []
    for c in convs:
        last_m = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.desc()).first()
        result.append(ConversationResponse(
            id=c.id,
            title=c.title,
            is_pinned=c.is_pinned,
            created_at=c.created_at,
            updated_at=c.updated_at,
            last_message=last_m.content[:80] + "..." if last_m and len(last_m.content) > 80 else (last_m.content if last_m else None)
        ))
    return result

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    title: str = "Nueva conversación",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = Conversation(user_id=current_user.id, title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        is_pinned=conv.is_pinned,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        last_message=None
    )

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conv

@router.post("/send", response_model=MessageResponse)
async def send_message(
    chat_in: ChatMessageSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Obtener o crear conversación
    conv_id = chat_in.conversation_id
    if not conv_id:
        # Usar la más reciente o crear una
        last_conv = db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.updated_at.desc()).first()
        if last_conv:
            conv = last_conv
        else:
            conv = Conversation(user_id=current_user.id, title=chat_in.message[:30])
            db.add(conv)
            db.commit()
            db.refresh(conv)
    else:
        conv = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.user_id == current_user.id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # 2. Guardar mensaje del usuario
    user_msg = Message(
        conversation_id=conv.id,
        sender="user",
        content=chat_in.message
    )
    db.add(user_msg)
    conv.updated_at = datetime.now(timezone.utc)
    db.commit()

    # 3. Obtener historial reciente para contexto
    history_msgs = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).limit(10).all()
    history = [{"sender": m.sender, "content": m.content} for m in history_msgs]

    # 4. Generar respuesta de la IA (con evaluación de herramientas)
    ai_result = await AIService.generate_response(
        db=db,
        user_id=current_user.id,
        user_message=chat_in.message,
        conversation_history=history
    )

    # 5. Guardar respuesta del asistente
    assistant_msg = Message(
        conversation_id=conv.id,
        sender="assistant",
        content=ai_result["content"],
        tool_calls=ai_result.get("tool_calls"),
        tool_results=ai_result.get("tool_results")
    )
    db.add(assistant_msg)
    conv.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg
