from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk


def delete_chunks_by_document(
    db: Session,
    document_id: int,
) -> None:
    """
    Delete all chunks belonging to a document.

    The transaction is NOT committed here.
    The caller decides when to commit.
    """

    statement = delete(DocumentChunk).where(
        DocumentChunk.document_id == document_id,
    )

    db.execute(statement)


def create_chunks(
    db: Session,
    document_id: int,
    chunks: list[str],
    embeddings: list[list[float]],
    page_numbers: list[int],
) -> list[DocumentChunk]:

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match number of embeddings"
        )

    if len(chunks) != len(page_numbers):
        raise ValueError(
            "Number of chunks must match number of page numbers"
        )

    db_chunks = []

    for index, (content, embedding, page_number) in enumerate(
        zip(chunks, embeddings, page_numbers)
    ):
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            page_number=page_number,
            content=content,
            embedding=embedding,
        )

        db.add(chunk)
        db_chunks.append(chunk)

    # Sends INSERT statements to PostgreSQL,
    # but does NOT permanently commit them.
    db.flush()

    return db_chunks