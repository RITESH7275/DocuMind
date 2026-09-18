from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.models.chunk import DocumentChunk

from app.services.document_processor import extract_text_from_pdf, clean_text
from app.services.chunker import chunk_text
from app.services.embedding_service import generate_embeddings

DOCUMENT_ID = 7
PDF_PATH = r"uploads\7\Resume_final6.pdf"


print("Starting chunk + embedding database test...")
print("-" * 60)


# 1. Extract PDF text
text = extract_text_from_pdf(PDF_PATH)

print(f"Extracted characters: {len(text)}")


# 2. Clean text
cleaned_text = clean_text(text)

print(f"Cleaned characters: {len(cleaned_text)}")


# 3. Create chunks
chunks = chunk_text(cleaned_text)

print(f"Total chunks: {len(chunks)}")


# 4. Generate embeddings
embeddings = generate_embeddings(chunks)

print(f"Total embeddings: {len(embeddings)}")
print(f"Embedding dimension: {len(embeddings[0])}")


# 5. Save chunks + embeddings to PostgreSQL
db = SessionLocal()

try:
    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        document_chunk = DocumentChunk(
            document_id=DOCUMENT_ID,
            chunk_index=index,
            content=chunk,
            embedding=embedding,
        )

        db.add(document_chunk)

    db.commit()

    print("-" * 60)
    print("CHUNKS + EMBEDDINGS SAVED SUCCESSFULLY!")


except Exception as e:
    db.rollback()
    print("ERROR:", e)


finally:
    db.close()