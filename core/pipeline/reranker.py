from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict, Union
from core.types import ElasticsearchAnswer

class Reranker:    
    def __init__(self, model_name: str = "antoinelouis/crossencoder-camembert-base-mmarcoFR"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    def rerank(self, query: str, docs: ElasticsearchAnswer, top_n: int = 3):
        if not docs or not docs.hits:
            return ElasticsearchAnswer(hits=[])
        
        # Extract content from each document
        doc_contents = [doc.source.get('content', '') for doc in docs.hits]
        
        pairs = [(query, content) for content in doc_contents]
        
        inputs = self.tokenizer(
            pairs, 
            padding=True, 
            truncation=True, 
            return_tensors="pt", 
            max_length=512
        )
        
        with torch.no_grad():
            scores = self.model(**inputs).logits.squeeze(-1)
        
        if scores.dim() == 0:
            scores = scores.unsqueeze(0)
        
        k = min(top_n, len(docs.hits))
        top_indices = torch.topk(scores, k).indices
        
        # Return only the top n documents
        reranked_hits = [docs.hits[i] for i in top_indices]
        
        return ElasticsearchAnswer(hits=reranked_hits)

