from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.message import Message


def create_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages_by_conversation(
    db: Session,
    conversation_id: int,
):
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
    )

    return db.execute(statement).scalars().all()