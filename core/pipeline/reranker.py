from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from core.types import ElasticsearchAnswer
from core.vector_store.logger import ActivityLogger
class Reranker:    
    def __init__(self, model_name: str = "antoinelouis/crossencoder-camembert-base-mmarcoFR"):
        self.model_name = model_name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        except Exception as e:
            print(f"Error loading reranker model '{model_name}': {e}")
            raise e
        self.activity_logger = ActivityLogger("reranker")
    
    def rerank(self, query: str, docs: ElasticsearchAnswer, top_n: int = 3):
        try:
            if not docs or not docs.hits:
                print("No documents to rerank.")
                self.activity_logger.log_interaction("No documents to rerank.", "warning")
                return ElasticsearchAnswer(hits=[])
            # display title of documents in order before reranking
            
            try:
                print("RERANKER: Documents before reranking:")
                for doc in docs.hits:
                    title = doc.source.get('doc_title', 'No Title')
                    print(f"RERANKER: Document ID: {doc.id}, Title: {title}")
            except Exception as e:
                self.activity_logger.log_interaction(f"Error logging document titles before reranking: {e}", "error")

                
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
            
            # display title of documents in order after reranking
            try:
                print("RERANKER: Documents after reranking:")
                for doc in reranked_hits:
                    title = doc.source.get('doc_title', 'No Title')
                    print(f"RERANKER: Document ID: {doc.id}, Title: {title}")
            except Exception as e:
                self.activity_logger.log_interaction(f"Error logging document titles after reranking: {e}", "error")
            
            return ElasticsearchAnswer(hits=reranked_hits)
        except Exception as e:
            self.activity_logger.log_interaction(f"Error during reranking: {e}", "error")
            raise e

