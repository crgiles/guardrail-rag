"""Public API request and response schemas."""

from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["employee", "network_engineer", "security_admin"]


class QueryRequest(BaseModel):
    """Incoming query and caller role."""
    question: str = Field(min_length=1, max_length=2000)
    role: Role


class Citation(BaseModel):
    """Reference to evidence used in an answer."""
    document_id: str
    chunk_id: str
    title: str


class QueryResponse(BaseModel):
    """Grounded answer response with citations and refusal metadata."""
    request_id: str
    answer: str
    citations: list[Citation]
    retrieved_count: int
    refusal_reason: str | None = None
