from app.db.session import SessionLocal
from app.services.vector_search import search_similar_chunks
from app.services.reranker import rerank_chunks


DOCUMENT_ID = 8

QUESTION = "What programming languages and technical skills does Ritesh have?"


def main():
    db = SessionLocal()

    try:
        print("\n" + "=" * 80)
        print("VECTOR SEARCH RESULTS")
        print("=" * 80)

        results = search_similar_chunks(
            db=db,
            query=QUESTION,
            document_id=DOCUMENT_ID,
            top_k=5,
        )

        for rank, result in enumerate(results, start=1):
            chunk = result["chunk"]

            print(
                f"\nRank: {rank}"
                f"\nChunk Index: {chunk.chunk_index}"
                f"\nSimilarity: {result['similarity']:.4f}"
                f"\nContent: {chunk.content[:250]}..."
            )

        print("\n" + "=" * 80)
        print("RERANKED RESULTS")
        print("=" * 80)

        reranked_results = rerank_chunks(
            query=QUESTION,
            results=results,
        )

        for rank, result in enumerate(
            reranked_results,
            start=1,
        ):
            chunk = result["chunk"]

            print(
                f"\nRank: {rank}"
                f"\nChunk Index: {chunk.chunk_index}"
                f"\nVector Similarity: {result['similarity']:.4f}"
                f"\nRerank Score: {result['rerank_score']:.4f}"
                f"\nContent: {chunk.content[:250]}..."
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()