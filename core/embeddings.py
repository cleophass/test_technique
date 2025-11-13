from core.config import EMBEDDINGS_MODEL_NAME
from sentence_transformers import SentenceTransformer
from typing import Dict, List
import datetime
from core.types import Embeddings

class Embedder:
    
    def __init__(self, model_name:str = EMBEDDINGS_MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        
    
    def embed_text(self, text:str) -> Embeddings:
        # This will be use for the retrieval part to embed the query
        embeddings = self.model.encode(text, show_progress_bar=False)
        embeddings_doc = {
            "text": text,
            "embeddings": embeddings.tolist(),
            "metadata": {
                "embedding_model": EMBEDDINGS_MODEL_NAME,
                "embedding_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "embedding_dimension": len(embeddings)
            }
        }
        return Embeddings(**embeddings_doc)
    
    def embed_multiple_texts(self, texts:List[str]) -> List[Dict]:
        embeddings = self.model.encode(texts, show_progress_bar=True)
        results = []
        for i, text in enumerate(texts):
            results.append({
                "text": text,
                "embeddings": embeddings[i].tolist(),
                "metadata": {
                    "embedding_model": EMBEDDINGS_MODEL_NAME,
                    "embedding_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "embedding_dimension": len(embeddings[i])
                }
            })
        return results
