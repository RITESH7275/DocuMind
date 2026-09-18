from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the document",
    )

    document_id: int = Field(
        ...,
        gt=0,
        description="ID of the document to search",
    )

    conversation_id: int | None = Field(
        default=None,
        gt=0,
        description="Existing conversation ID, if continuing a conversation",
        examples=[None],
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve",
    )

class Source(BaseModel):
    page_number: int | None
    similarity: float
    rerank_score: float
    snippet: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    document_id: int
    conversation_id: int
    filename: str
    sources: list[Source]