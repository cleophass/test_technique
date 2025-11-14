from elasticsearch import Elasticsearch
from typing import Dict, List, Any
from elasticsearch import helpers
import datetime
from pydantic import ValidationError
from core.types import Document

class ElasticClient:

    def __init__(self, hosts: str):        
        self.es = Elasticsearch(hosts=hosts, verify_certs=False)
        
    def verify_index(self, index_name: str) -> bool:
        # this will be usefull when lauching the app to verify that the index exists and create it if not
        response = self.es.indices.exists(index=index_name)
        if response == True: # Doing this because of python typing error
            return True
        else:
            return False
    
    def create_document_index(self, index_name: str, embeddings_dimension: int):
        try : 
            if not self.verify_index(index_name):
                self.es.indices.create(
                    index=index_name,
                    mappings={
                        "properties": {
                            "doc_title": { "type": "text"  },
                            "content": { "type": "text"  },
                            "embeddings": { "type": "dense_vector", "dims": embeddings_dimension},
                            "metadata": {
                                "properties": {
                                    "source": { "type": "keyword" },
                                    "date": { "type": "date", "format": "yyyy-MM-dd||yyyy" },
                                    "modified": { "type": "date", "format": "yyyy-MM-dd" },
                                    "embedding_model": { "type": "keyword" },
                                    "embedding_date": { "type": "date", "format": "yyyy-MM-dd" },
                                    "embedding_dimension": { "type": "integer" }
                                }
                            },
                            "indexed_at": {"type": "date"}
                        } }
                    )
                print("Index created successfully.")
            else:
                print("Index already exists.")
        except Exception as e:
            print("Error creating index:", e)
            
    def create_logs_index(self, index_name: str):
        try : 
            if not self.verify_index(index_name):
                self.es.indices.create(
                    index=index_name,
                    mappings={
                        "properties": {
                        "log_message": { "type": "text"  },
                        "log_level": { "type": "keyword"  },
                        "timestamp": { "type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis" }
                    } }
                )
                print("Logs Index created successfully.")
            else:
                print("Logs Index already exists.")
        except Exception as e:
            print("Error creating logs index:", e)

    def index_document(self, index_name: str, document: Document) -> bool:
        # first we validate the document using Pydantic
        try:
            Document(**document.model_dump()) # this will raise an error if the types are not correct
        except ValidationError as e:
            print("invalid types:", e)
            return False
        
        self.es.index(index=index_name, document=document.model_dump())
        print("Document indexed successfully, name:", document.doc_title)
        return True    
    
    def bulk_index_documents(self, index_name: str, documents: List[Document]) -> bool:
        try:
            for document in documents:
                Document(**document.model_dump())  # this will raise an error if the types are not correct
        except ValidationError as e:
            print("invalid types:", e)
            return False
        
        actions = [
            {
                "_index": index_name,
                "_source": document.model_dump()
            }
            for document in documents
        ]
        helpers.bulk(self.es, actions)
        print(f"Bulk indexed {len(documents)} documents successfully.")
        return True
            
    def delete_document(self, index_name: str, document_id: str) -> bool:
        try:
            self.es.delete(index=index_name, id=document_id)
            print(f"Document with ID {document_id} deleted successfully.")
            return True
        except Exception as e:
            print("Error deleting document:", e)
            return False
    
    def log_handler(self, index_name: str, log_message: str, log_level: str = "INFO") -> bool:
        # this function will be used to log different events in the system
        try :
            log_entry = {
                "log_message": log_message,
                "log_level": log_level,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.es.index(index=index_name, document=log_entry)
            return True
    
        except Exception as e:
            print("Error logging entry:", e)
            return False
        
    # We will need a function to see available documents 
    def list_documents(self, index_name: str) -> List[Dict]:
        try:
            response = self.es.search(
                index=index_name,
                body={
                    "query": {
                        "match_all": {}
                    },
                }
            )
            documents = response["hits"]["hits"]
            return documents
        except Exception as e:
            print("Error list ing documents:", e)
            return []
    
    def cosine_similarity_search(self, index_name: str, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embeddings') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }
        try : 
            response = self.es.search(index=index_name, query=query)
            if not response["hits"]["hits"]:
                return [{}]
            return response["hits"]["hits"]
        except Exception as e:
            print("Error during cosine similarity search:", e)
            return [{}]
        

