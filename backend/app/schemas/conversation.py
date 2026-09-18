from datetime import datetime

from pydantic import BaseModel, Field


class ConversationResponse(BaseModel):
    id: int
    document_id: int
    title: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    id: int
    document_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]


class ConversationUpdate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )
    