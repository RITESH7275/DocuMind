from app.db.session import SessionLocal
from app.models.document import Document
from app.services.document_processor import extract_clean_pages_from_pdf
from app.services.ingestion_service import process_document


def test_document_ingestion():
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.text_content.isnot(None))
            .filter(Document.text_content != "")
            .first()
        )

        assert document is not None, "No processed document found"

        pages = extract_clean_pages_from_pdf(
            document.file_path
        )

        assert pages, "No pages extracted from PDF"

        chunk_count = process_document(
            db=db,
            document_id=document.id,
            pages=pages,
        )

        db.commit()

        assert chunk_count > 0, "No chunks were created"

    finally:
        db.close()