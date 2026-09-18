from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import DocumentStatus
from app.core.security import get_current_user
from app.db.session import get_db

from app.repositories.document import get_document_by_id
from app.repositories.conversation import (
    create_conversation,
    get_conversation_by_id,
)
from app.repositories.message import create_message

from app.schemas.chat import ChatRequest, ChatResponse, Source

from app.services.conversation_service import (
    get_conversation_history,
)

from app.services.query_rewriter import rewrite_query

from app.services.rag_service import (
    retrieve_chunks,
    build_context,
    extract_snippet,
)

from app.services.llm_service import generate_answer


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------
    # 1. Verify document exists
    # --------------------------------------------------

    document = get_document_by_id(
        db,
        request.document_id,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # --------------------------------------------------
    # 2. Verify document ownership
    # --------------------------------------------------

    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document",
        )

    # --------------------------------------------------
    # 3. Verify document is ready for chat
    # --------------------------------------------------

    if document.status != DocumentStatus.INDEXED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document is not ready for chat. Current status: {document.status}",
        )

    # --------------------------------------------------
    # 4. Get or create conversation
    # --------------------------------------------------

    if request.conversation_id is None:

        conversation = create_conversation(
            db=db,
            user_id=current_user.id,
            document_id=document.id,
        )

    else:

        conversation = get_conversation_by_id(
            db=db,
            conversation_id=request.conversation_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Verify conversation ownership
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation",
            )

        # Verify conversation belongs to requested document
        if conversation.document_id != document.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation does not belong to this document",
            )

    # --------------------------------------------------
    # 5. Get conversation history
    # --------------------------------------------------

    history = get_conversation_history(
        db=db,
        conversation_id=conversation.id,
    )

    # --------------------------------------------------
    # 6. Save user's message
    # --------------------------------------------------

    create_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=request.question,
    )

    # --------------------------------------------------
    # 7. Rewrite question using conversation history
    # --------------------------------------------------

    rewritten_query = rewrite_query(
        question=request.question,
        history=history,
    )
    print("REWRITTEN QUERY:", rewritten_query)
    # --------------------------------------------------
    # 8. Retrieve chunks + generate answer
    # --------------------------------------------------

    try:
        chunks = retrieve_chunks(
            db=db,
            query=rewritten_query,
            document_id=request.document_id,
            top_k=request.top_k,
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant information found in the document",
            )

        # --------------------------------------------------
        # 9. Build context
        # --------------------------------------------------

        context = build_context(chunks)

        # --------------------------------------------------
        # 10. Generate answer
        # --------------------------------------------------

        answer = generate_answer(
            question=request.question,
            context=context,
            history=history,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate an answer",
        )

    # --------------------------------------------------
    # 11. Save assistant's message
    # --------------------------------------------------

    create_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
    )

    # --------------------------------------------------
    # 12. Build sources
    # --------------------------------------------------

    sources = [
        Source(
            page_number=result["chunk"].page_number,
            similarity=round(
                result["similarity"],
                4,
            ),
            rerank_score=round(
                result["rerank_score"],
                4,
            ),
            snippet=extract_snippet(
                text=result["chunk"].content,
                query=rewritten_query,
            ),
        )
        for result in chunks
    ]

    # --------------------------------------------------
    # 13. Return response
    # --------------------------------------------------

    return ChatResponse(
        question=request.question,
        answer=answer,
        document_id=document.id,
        conversation_id=conversation.id,
        filename=document.filename,
        sources=sources,
    )