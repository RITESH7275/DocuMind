from app.db.session import SessionLocal
from app.services.vector_search import search_similar_chunks


DOCUMENT_ID = 8


QUESTIONS = [
    "What programming languages and technical skills does Ritesh have?",
    "What projects has Ritesh worked on?",
    "What hackathons did Ritesh participate in?",
    "What is Ritesh's CGPA?",
    "What is Ritesh's educational background?",
]


def main():
    db = SessionLocal()

    try:
        for question in QUESTIONS:
            print("\n" + "=" * 80)
            print(f"QUESTION: {question}")
            print("=" * 80)

            results = search_similar_chunks(
                db=db,
                query=question,
                document_id=DOCUMENT_ID,
                top_k=5,
            )

            for rank, result in enumerate(results, start=1):
                chunk = result["chunk"]
                similarity = result["similarity"]

                print(
                    f"\nRank: {rank}"
                    f"\nChunk Index: {chunk.chunk_index}"
                    f"\nSimilarity: {similarity:.4f}"
                    f"\nContent: {chunk.content[:250]}..."
                )

    finally:
        db.close()


if __name__ == "__main__":
    main()