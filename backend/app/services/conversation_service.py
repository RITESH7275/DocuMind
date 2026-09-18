from sqlalchemy.orm import Session

from app.repositories.message import (
    get_messages_by_conversation,
)


def get_conversation_history(
    db: Session,
    conversation_id: int,
) -> list[dict]:
    """
    Retrieve messages from a conversation
    and convert them into a simple format
    for the LLM.
    """

    messages = get_messages_by_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]