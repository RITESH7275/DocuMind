from app.db.session import SessionLocal
from app.models.chunk import DocumentChunk


db = SessionLocal()

try:
    print("Starting transaction...")

    test_chunk = DocumentChunk(
        document_id=23,
        chunk_index=999999,
        page_number=999999,
        content="ROLLBACK TEST - THIS SHOULD NOT BE SAVED",
        embedding=[0.0] * 384,
    )

    db.add(test_chunk)

    # Force the INSERT to PostgreSQL
    db.flush()

    print("Test chunk inserted inside transaction.")

    # Intentionally create an error
    raise RuntimeError("Intentional rollback test")

except Exception as error:
    print(f"Error occurred: {error}")
    print("Rolling back transaction...")

    db.rollback()

finally:
    db.close()
    print("Database session closed.")