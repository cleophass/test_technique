from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentMetadata(BaseModel):
    source: str
    date: Optional[str] = None
    modified: Optional[str] = None
    embedding_model: str
    embedding_date: str
    embedding_dimension: int


class Document(BaseModel):
    doc_title: str
    content: str
    embeddings: List[float]
    metadata: DocumentMetadata
    indexed_at: Optional[datetime]


class EmbeddingsMetadata(BaseModel):
    embedding_model: str
    embedding_date: str
    embedding_dimension: int


class Embeddings(BaseModel):
    text: str
    embeddings: List[float]
    metadata: EmbeddingsMetadata


class GuardAgentResponse(BaseModel):
    isSafe: bool
    reasons: str | None = None


class RewriterAgentResponse(BaseModel):
    neededRewrite: bool
    rewritten_question: str


class HyDEAgentResponse(BaseModel):
    hypothetical_answer: str


class ElasticsearchAnswerItem(BaseModel):
    index: str
    id: str
    score: float
    source: Dict[str, Any]


class ElasticsearchAnswer(BaseModel):
    hits: List[ElasticsearchAnswerItem]


class RAGResponse(BaseModel):
    answer: str
    source_documents: Optional[List[ElasticsearchAnswer]] = None
    error: Optional[str] = None
    details: Optional[str] = None


class TitleAgentResponse(BaseModel):
    title: str
