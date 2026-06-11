from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    created_at: datetime
    chunk_count: int


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)


class SourceChunk(BaseModel):
    document_id: int
    filename: str
    chunk_id: int
    chunk_index: int
    similarity: float
    content_preview: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    metadata: dict[str, Any] = {}


class ConversationCreateRequest(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=255)


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
    