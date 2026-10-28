"""
Pydantic models for API request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ─── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str = Field(..., example="alice")
    password: str = Field(..., example="alice123")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class UserInfo(BaseModel):
    username: str
    role: str


# ─── RAG ───────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: Optional[int] = Field(default=None, ge=1, le=10)
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class SourceChunk(BaseModel):
    """A single retrieved document chunk shown to the user for transparency."""
    text: str               # snippet of the chunk text
    access_level: str       # the security label on this chunk
    source_file: str        # originating filename
    chunk_id: str           # unique ID in ChromaDB
    relevance_score: Optional[float] = None


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    query: str
    user_role: str
    chunks_retrieved: int
    access_denied: bool = False
    model_used: Optional[str] = None
    latency_ms: Optional[float] = None
    filter_applied: Optional[str] = None

