from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    user_id: int,
    filename: str,
    file_path: str,
    file_type: str,
    file_size: int,
    text_content: str | None = None,
):
    document = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        status="uploaded",
        text_content=text_content,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document_by_id(
    db: Session,
    document_id: int,
):
    statement = select(Document).where(
        Document.id == document_id
    )

    return db.execute(statement).scalar_one_or_none()


def get_documents_by_user(
    db: Session,
    user_id: int,
):
    statement = select(Document).where(
        Document.user_id == user_id
    )

    return db.execute(statement).scalars().all()