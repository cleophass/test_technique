
from typing import List, Dict
from core.vector_store.elastic_client import ElasticClient
import datetime
from core.vector_store.mappings import HISTORY_INDEX_MAPPING, MESSAGE_INDEX_MAPPING
from core.pipeline.title import TitleAgent
from core.config import HISTORY_INDEX_NAME, MESSAGE_INDEX_NAME

class History:
    def __init__(self):
        self.history_index_name = HISTORY_INDEX_NAME # -> index for conversations
        self.message_index_name = MESSAGE_INDEX_NAME # -> index for messages
        self.es_client = ElasticClient(hosts="http://localhost:9200")
        self.history_index_mapping = HISTORY_INDEX_MAPPING
        self.message_index_mapping = MESSAGE_INDEX_MAPPING
        self.title_agent = TitleAgent()
       
    def list_history(self):
        response = self.es_client.es.search(
            index=self.history_index_name,
            body={
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {"created_at": {"order": "desc"}}
                ]
            }
        )
        histories = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            histories.append({
                "id": source.get("id", ""),
                "created_at": source.get("created_at", ""),
                "title": source.get("title", "")
            })
        return histories
    
        
    
    def load_messages(self, conversation_id: str) -> List[dict]:
        response = self.es_client.es.search(
            index=self.message_index_name,
            body={
                "query": {
                    "match": {
                        "conversation_id": conversation_id
                    }
                },
                "sort": [
                    {"timestamp": {"order": "asc"}}
                ]
            }
        )
        messages = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            messages.append({
                "role": source.get("role", "user"),
                "content": source.get("message", "")
            })
        return messages
    
    def create_conversation(self, conversation_id: str,message:str) -> bool:
        try : 
            title = self.title_agent.create_title(question=message).title
        except Exception as e:
            print("Error generating title: ", e)
            title = "Nouvelle Conversation"
        conversation_doc = {
            "id": conversation_id,
            "title": title,
            "created_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat().replace('T', ' ')
        }
        self.es_client.es.index(index=self.history_index_name, document=conversation_doc)
        print("Conversation created successfully")
        return True

       
    
    def add_message(self,message: str, conversation_id: str,role: str) -> bool:
        message_doc = {
            "id":"2345",
            "conversation_id": conversation_id,
            "message":message,
            "role": role,
            "timestamp": datetime.datetime.utcnow().replace(microsecond=0).isoformat().replace('T', ' ')
        }
        return self.add_message_to_history(self.message_index_name, message=message_doc)
        
        
    def create_history_index(self):    
        self.es_client.create_index(self.history_index_name, mappings=self.history_index_mapping)     
              
    def create_message_index(self):
        self.es_client.create_index(self.message_index_name, mappings=self.message_index_mapping)
    
    def add_message_to_history(self, index_name: str, message: Dict, ) -> bool:
        self.es_client.es.index(index=index_name, document=message)
        print("Message added successfully")
        return True    