import time

from celery.utils.log import get_task_logger

from app.core.constants import DocumentStatus
from app.celery_app import celery_app
from app.db.session import SessionLocal

from app.repositories.document import get_document_by_id
from app.repositories.chunk_repositories import delete_chunks_by_document

from app.services.document_processor import (
    extract_clean_pages_from_pdf,
)

from app.services.ingestion_service import (
    process_document,
)


logger = get_task_logger(__name__)


@celery_app.task
def process_document_task(document_id: int) -> str:
    """
    Background task for processing a document.

    Pipeline:
    PDF → extraction → chunking → embedding → database
    """

    db = SessionLocal()
    start_time = time.perf_counter()

    try:
        # 1. Get document
        document = get_document_by_id(
            db=db,
            document_id=document_id,
        )

        if not document:
            raise ValueError(
                f"Document {document_id} not found"
            )

        # 2. Mark document as processing
        document.status = DocumentStatus.PROCESSING.value

        # Clear old extracted text
        document.text_content = None

        # Remove old chunks before reprocessing
        delete_chunks_by_document(
            db=db,
            document_id=document_id,
        )

        db.commit()

        logger.info(
            f"Document {document_id} status: processing"
        )

        logger.info(
            f"Processing document: {document.filename}"
        )

        # 3. Mark document as extracting
        document.status = DocumentStatus.EXTRACTING.value
        db.commit()

        logger.info(
            f"Document {document_id} status: extracting"
        )

        # Extract and clean pages
        pages = extract_clean_pages_from_pdf(
            document.file_path
        )

        logger.info(
            f"Extracted {len(pages)} pages"
        )

        # Store extracted document text
        document.text_content = "\n\n".join(
            page["text"]
            for page in pages
        )

        db.commit()

        # 4. Mark document as chunking
        document.status = DocumentStatus.CHUNKING.value
        db.commit()

        logger.info(
            f"Document {document_id} status: chunking"
        )

        # 5. Mark document as embedding
        document.status = DocumentStatus.EMBEDDING.value
        db.commit()

        logger.info(
            f"Document {document_id} status: embedding"
        )

        # Run ingestion pipeline
        chunk_count = process_document(
            db=db,
            document_id=document_id,
            pages=pages,
        )

        logger.info(
            f"Stored {chunk_count} chunks in database"
        )

        # 6. Mark document as indexed
        document.status = DocumentStatus.INDEXED.value
        db.commit()

        logger.info(
            f"Document {document_id} status: indexed"
        )

        # Calculate processing time
        processing_time = (
            time.perf_counter() - start_time
        )

        logger.info(
            f"Document {document_id} processing completed "
            f"in {processing_time:.2f} seconds"
        )

        # 7. Return task result
        return (
            f"Document {document_id}: "
            f"{len(pages)} pages, "
            f"{chunk_count} chunks stored"
        )

    except Exception:
        # Roll back the failed transaction
        db.rollback()

        # Get the document again
        document = get_document_by_id(
            db=db,
            document_id=document_id,
        )

        if document:
            # Mark document as failed
            document.status = DocumentStatus.FAILED.value

            # Remove potentially stale data
            document.text_content = None

            delete_chunks_by_document(
                db=db,
                document_id=document_id,
            )

            db.commit()

        logger.error(
            f"Document {document_id} processing failed",
            exc_info=True,
        )

        raise

    finally:
        db.close()