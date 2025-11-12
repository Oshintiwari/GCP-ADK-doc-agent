from pydantic import BaseModel, Field
from typing import List

class Citation(BaseModel):
    doc_id: str
    filename: str
    page: int
    excerpt: str

class Meta(BaseModel):
    used_model: str
    num_docs: int
    retrieval_k: int
    latency_ms: int
    tokens_input: int
    tokens_output: int
    confidence: float = Field(ge=0.0, le=1.0)

class QAResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    meta: Meta
    logs: List[str]
