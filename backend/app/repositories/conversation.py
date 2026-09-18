from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


def create_conversation(
    db: Session,
    user_id: int,
    document_id: int,
    title: str = "New Conversation",
):
    conversation = Conversation(
        user_id=user_id,
        document_id=document_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation_by_id(
    db: Session,
    conversation_id: int,
):
    statement = select(Conversation).where(
        Conversation.id == conversation_id
    )

    return db.execute(
        statement
    ).scalar_one_or_none()


def get_conversations_by_user(
    db: Session,
    user_id: int,
):
    statement = (
        select(Conversation)
        .where(
            Conversation.user_id == user_id
        )
        .order_by(
            Conversation.updated_at.desc()
        )
    )

    return db.execute(
        statement
    ).scalars().all()


def delete_conversation(
    db: Session,
    conversation_id: int,
):
    statement = select(Conversation).where(
        Conversation.id == conversation_id
    )

    conversation = db.execute(
        statement
    ).scalar_one_or_none()

    if not conversation:
        return None

    db.delete(conversation)
    db.commit()

    return conversation


def update_conversation_title(
    db: Session,
    conversation_id: int,
    title: str,
):
    statement = select(Conversation).where(
        Conversation.id == conversation_id
    )

    conversation = db.execute(
        statement
    ).scalar_one_or_none()

    if not conversation:
        return None

    conversation.title = title

    db.commit()
    db.refresh(conversation)

    return conversation