from sentence_transformers import CrossEncoder # type: ignore


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

model = CrossEncoder(MODEL_NAME)


def rerank_chunks(
    query: str,
    results: list,
) -> list:
    """
    Rerank retrieved document chunks using a cross-encoder.

    Args:
        query: User's question.
        results: Results returned by vector search.

    Returns:
        Results sorted by reranker relevance score.
    """

    if not results:
        return []

    pairs = [
        (
            query,
            result["chunk"].content,
        )
        for result in results
    ]

    scores = model.predict(pairs)

    reranked_results = []

    for result, score in zip(results, scores):
        reranked_results.append(
            {
                **result,
                "rerank_score": float(score),
            }
        )

    reranked_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return reranked_results