from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db

from app.repositories.document import (
    create_document,
    get_document_by_id,
    get_documents_by_user,
)

from app.schemas.document import (
    DocumentResponse,
    DocumentStatusResponse,
)

from app.tasks.document_tasks import process_document_task
from app.models.document import Document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    # Create a directory for the current user
    user_upload_dir = UPLOAD_DIR / str(current_user.id)

    user_upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Prevent unsafe filenames
    filename = Path(
        file.filename or "document.pdf"
    ).name

    # Read uploaded file
    file_content = file.file.read()

    # Validate file is not empty
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must not exceed 10 MB",
        )

    # Generate a unique filename for storage
    stored_filename = f"{uuid4().hex}_{filename}"

    file_path = user_upload_dir / stored_filename

    # Save the uploaded PDF
    with file_path.open("wb") as buffer:
        buffer.write(file_content)

    try:
        # Create database record
        document = create_document(
            db=db,
            user_id=current_user.id,
            filename=filename,
            file_path=str(file_path),
            file_type=file.content_type,
            file_size=file_path.stat().st_size,
            text_content=None,
        )

        try:
            # Queue background processing
            process_document_task.delay(document.id)

        except Exception:
            # Remove database record if task cannot be queued
            db.delete(document)
            db.commit()

            # Remove uploaded file
            if file_path.exists():
                file_path.unlink()

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document processing service is unavailable",
            )

        return document

    except HTTPException:
        raise

    except Exception:
        # Roll back any pending database changes
        db.rollback()

        # Remove uploaded file
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document",
        )


@router.get(
    "/",
    response_model=list[DocumentResponse],
)
def get_my_documents(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_documents_by_user(
        db,
        current_user.id,
    )


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
)
def get_document_status(
    document_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = get_document_by_id(
        db,
        document_id,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Make sure the document belongs to the current user
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document",
        )

    return DocumentStatusResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = get_document_by_id(
        db,
        document_id,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Make sure the document belongs to the current user
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document",
        )

    return document


@router.delete(
    "/{document_id}",
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    file_path = Path(doc.file_path)

    db.delete(doc)
    db.commit()

    if file_path.exists():
        file_path.unlink()

    return {
        "message": "Document deleted successfully"
    }