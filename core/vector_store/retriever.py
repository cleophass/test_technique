# simple class just to avoid using es class directly in the pipeline

from core.vector_store.elastic_client import ElasticClient
from core.embeddings import Embedder
from typing import List, Dict
from core.types import ElasticsearchAnswer, ElasticsearchAnswerItem
from core.config import DOCUMENTS_INDEX_NAME
class Retriever:
    def __init__(self):
        self.es_client = ElasticClient(hosts="http://localhost:9200")
        self.embedder = Embedder()
        self.documents_index_name = DOCUMENTS_INDEX_NAME
        
    def retrieve_documents(self, query: str, top_k: int = 5) -> ElasticsearchAnswer:
        # embed the query
        query_embedding = self.embedder.embed_text(query).embeddings
        # perform the search
        results = self.es_client.cosine_similarity_search(index_name=self.documents_index_name, query_embedding=query_embedding, top_k=top_k)
        # limit to top_k results

        results = results[:top_k]
        # create a ElasticsearchAnswer object 
        es_answer_items = []
        for item in results:
            es_answer_item = ElasticsearchAnswerItem(
                index=item.get("_index", ""),
                id=item.get("_id", ""),
                score=item.get("_score", 0.0),
                source=item.get("_source", {})
            )
            es_answer_items.append(es_answer_item)
        es_answer = ElasticsearchAnswer(hits=es_answer_items)
        return es_answer
    
