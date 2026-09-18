from app.db.session import SessionLocal

from app.models.user import User
from app.models.document import Document
from app.models.chunk import DocumentChunk

from app.services.rag_service import retrieve_context
from app.services.llm_service import generate_answer


DOCUMENT_ID = 7

question = "What programming languages and technical skills does Ritesh have?"


db = SessionLocal()

try:
    print("Starting complete RAG test...")
    print("-" * 60)

    # Step 1: Retrieve relevant document context
    context = retrieve_context(
        db=db,
        query=question,
        document_id=DOCUMENT_ID,
        top_k=3,
    )

    print("Context retrieved successfully!")
    print("-" * 60)

    # Step 2: Generate answer using the LLM
    answer = generate_answer(
        question=question,
        context=context,
    )

    print("LLM ANSWER")
    print("=" * 60)
    print(answer)

finally:
    db.close()