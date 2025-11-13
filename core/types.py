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
    doc_title: str = Field(..., description="Titre du document")
    content: str = Field(..., description="Contenu du document")
    embeddings: List[float] = Field(..., description="Vecteur d'embeddings")
    metadata: DocumentMetadata = Field(..., description="Métadonnées du document")
    indexed_at: Optional[datetime] = Field(default=None, description="Date d'indexation")
    
class EmbeddingsMetadata(BaseModel):
    embedding_model: str
    embedding_date: str
    embedding_dimension: int
    
class Embeddings(BaseModel):
    text: str = Field(..., description="Texte à encoder")
    embeddings: List[float] = Field(..., description="Vecteur d'embeddings")
    metadata: EmbeddingsMetadata = Field(..., description="Métadonnées des embeddings")
    
    
class GuardAgentResponse(BaseModel):
    isSafe: bool
    reasons: str|None = None
    
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
    
