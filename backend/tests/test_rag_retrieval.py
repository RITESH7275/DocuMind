from app.db.session import SessionLocal

from app.models.user import User
from app.models.document import Document
from app.models.chunk import DocumentChunk

from app.services.rag_service import retrieve_context


DOCUMENT_ID = 7

query = "What programming languages and technical skills does Ritesh have?"


db = SessionLocal()

try:
    context = retrieve_context(
        db=db,
        query=query,
        document_id=DOCUMENT_ID,
        top_k=3,
    )

    print("RAG RETRIEVAL SUCCESSFUL!")
    print("-" * 60)

    print("QUERY:")
    print(query)

    print("\n" + "=" * 60)
    print("RETRIEVED CONTEXT")
    print("=" * 60)

    print(context)

finally:
    db.close()