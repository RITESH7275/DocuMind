from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db

from app.repositories.conversation import (
    get_conversation_by_id,
    get_conversations_by_user,
    delete_conversation,
    update_conversation_title,
)

from app.repositories.message import get_messages_by_conversation

from app.schemas.conversation import (
    ConversationResponse,
    ConversationDetailResponse,
    ConversationUpdate,
    MessageResponse,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get(
    "",
    response_model=list[ConversationResponse],
)
def get_my_conversations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_conversations_by_user(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation",
        )

    messages = get_messages_by_conversation(
        db=db,
        conversation_id=conversation.id,
    )

    return ConversationDetailResponse(
        id=conversation.id,
        document_id=conversation.document_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message in messages
        ],
    )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def update_conversation(
    conversation_id: int,
    request: ConversationUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation",
        )

    updated_conversation = update_conversation_title(
        db=db,
        conversation_id=conversation_id,
        title=request.title,
    )

    return updated_conversation


@router.delete(
    "/{conversation_id}",
)
def delete_my_conversation(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation",
        )

    delete_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    return {
        "message": "Conversation deleted successfully"
    }