from app.db.session import SessionLocal
from app.models.document import Document
from app.services.vector_search import search_similar_chunks


def test_vector_search():
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.text_content.isnot(None))
            .filter(Document.text_content != "")
            .first()
        )

        assert document is not None, "No processed document found"

        query = "What programming languages and technical skills does Ritesh have?"

        results = search_similar_chunks(
            db=db,
            query=query,
            document_id=document.id,
            top_k=3,
        )

        assert results, "Vector search returned no results"
        assert len(results) <= 3

        for result in results:
            assert "chunk" in result
            assert "similarity" in result

            chunk = result["chunk"]

            assert chunk.id is not None
            assert chunk.document_id == document.id
            assert chunk.content
            assert result["similarity"] is not None

    finally:
        db.close()