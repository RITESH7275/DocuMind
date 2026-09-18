from sqlalchemy.orm import Session

from app.repositories.chunk_repositories import create_chunks
from app.services.chunker import chunk_text
from app.services.embedding_service import generate_embeddings


def process_document(
    db: Session,
    document_id: int,
    pages: list[dict],
) -> int:
    """
    Chunk document pages, generate embeddings,
    and store chunks with their page numbers.

    Returns:
        Number of chunks created.
    """

    all_chunks = []
    all_page_numbers = []

    # Step 1: Chunk each page separately
    for page in pages:
        page_number = page["page_number"]
        text = page["text"]

        chunks = chunk_text(
            text=text,
            chunk_size=1000,
            chunk_overlap=200,
        )

        for chunk in chunks:
            all_chunks.append(chunk)
            all_page_numbers.append(page_number)

    # Step 2: Generate embeddings
    if all_chunks:
        embeddings = generate_embeddings(all_chunks)
    else:
        embeddings = []

    # If there are no chunks, return 0
    if not all_chunks:
        return 0

    # Step 3: Store new chunks + embeddings + page numbers
    db_chunks = create_chunks(
        db=db,
        document_id=document_id,
        chunks=all_chunks,
        embeddings=embeddings,
        page_numbers=all_page_numbers,
    )

    return len(db_chunks)





    