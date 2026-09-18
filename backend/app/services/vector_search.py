from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


def search_similar_chunks(
    db: Session,
    query: str,
    document_id: int,
    top_k: int = 3,
):
    """
    Find the most similar document chunks for a query
    and return each chunk with its similarity score.
    """

    query_embedding = generate_embedding(query)

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    statement = (
        select(
            DocumentChunk,
            distance.label("distance"),
        )
        .where(
            DocumentChunk.document_id == document_id
        )
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(statement).all()

    return [
        {
            "chunk": chunk,
            "similarity": 1 - float(distance_value),
        }
        for chunk, distance_value in results
    ]