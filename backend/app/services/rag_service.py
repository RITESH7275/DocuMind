import re

from sqlalchemy.orm import Session

from app.services.vector_search import search_similar_chunks
from app.services.reranker import rerank_chunks

def retrieve_chunks(
    db: Session,
    query: str,
    document_id: int,
    top_k: int = 3,
):
    """
    Retrieve candidate chunks using vector search,
    rerank them using a cross-encoder,
    and remove results that are significantly weaker
    than the best result.
    """

    # Retrieve more candidates than we finally need.
    candidate_k = max(top_k * 3, 10)

    candidates = search_similar_chunks(
        db=db,
        query=query,
        document_id=document_id,
        top_k=candidate_k,
    )

    if not candidates:
        return []

    # Rerank candidates using the cross-encoder.
    reranked = rerank_chunks(
        query=query,
        results=candidates,
    )

    if not reranked:
        return []

    # The highest reranker score is our strongest result.
    best_score = reranked[0]["rerank_score"]

    # Relative margin rather than an absolute threshold.
    score_margin = 2.0

    filtered_results = [
        result
        for result in reranked
        if best_score - result["rerank_score"] <= score_margin
    ]

    # Never return more than the requested number of sources.
    return filtered_results[:top_k]

def build_context(results) -> str:
    """
    Build context from retrieved chunks for the LLM.
    """

    if not results:
        return ""

    context_parts = []

    for result in results:
        chunk = result["chunk"]

        context_parts.append(
           f"[Page {chunk.page_number} | Chunk {chunk.chunk_index}]\n"
           f"{chunk.content}"
       )

    return "\n\n".join(context_parts)


def extract_snippet(
    text: str,
    query: str,
    max_length: int = 300,
) -> str:
    """
    Extract a relevant section of a document chunk
    based on words from the user's query.

    The function keeps nearby lines together so that
    citations contain useful supporting evidence rather
    than only a heading or isolated sentence.
    """

    if not text:
        return ""

    if len(text) <= max_length:
        return text

    query_words = {
        word.lower()
        for word in re.findall(r"\b\w+\b", query)
        if len(word) > 3
    }

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return text[:max_length].rstrip() + "..."

    best_index = 0
    best_score = 0

    for index, line in enumerate(lines):
        line_words = {
            word.lower()
            for word in re.findall(r"\b\w+\b", line)
        }

        score = len(
            query_words.intersection(line_words)
        )

        if score > best_score:
            best_score = score
            best_index = index

    if best_score == 0:
        return text[:max_length].rstrip() + "..."

    start_index = max(0, best_index - 1)
    end_index = min(len(lines), best_index + 4)

    selected_lines = lines[start_index:end_index]

    snippet = "\n".join(selected_lines)

    while len(snippet) > max_length and len(selected_lines) > 1:
        selected_lines.pop()
        snippet = "\n".join(selected_lines)

    if len(snippet) > max_length:
        snippet = snippet[:max_length].rstrip() + "..."

    return snippet


def retrieve_context(
    db: Session,
    query: str,
    document_id: int,
    top_k: int = 3,
) -> str:
    """
    Retrieve relevant chunks and combine them
    into context for the LLM.
    """

    results = retrieve_chunks(
        db=db,
        query=query,
        document_id=document_id,
        top_k=top_k,
    )

    return build_context(results)