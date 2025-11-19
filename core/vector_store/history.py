
from typing import List, Dict
from core.vector_store.elastic_client import ElasticClient
import datetime
from core.vector_store.mappings import HISTORY_INDEX_MAPPING, MESSAGE_INDEX_MAPPING
from core.pipeline.title import TitleAgent
from core.config import HISTORY_INDEX_NAME, MESSAGE_INDEX_NAME
from core.vector_store.logger import ActivityLogger

class History:
    def __init__(self):
        self.history_index_name = HISTORY_INDEX_NAME # -> index for conversations
        self.message_index_name = MESSAGE_INDEX_NAME # -> index for messages
        self.es_client = ElasticClient(hosts="http://localhost:9200")
        self.history_index_mapping = HISTORY_INDEX_MAPPING
        self.message_index_mapping = MESSAGE_INDEX_MAPPING
        self.title_agent = TitleAgent()
        self.activity_logger = ActivityLogger("history_manager")
       
    def list_history(self):
        try:
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
        except Exception as e:
            self.activity_logger.log_interaction(f"Error listing history: {e}", "error")
            return []
        
            
    
    def load_messages(self, conversation_id: str) -> List[dict]:
        try:
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
        except Exception as e:
            self.activity_logger.log_interaction(f"Error loading messages: {e}", "error")
            return []
        
    def create_conversation(self, conversation_id: str,message:str) -> bool:
        try:
            try : 
                title = self.title_agent.create_title(question=message).title
            except Exception as e:
                self.activity_logger.log_interaction(f"Error generating title: {e}", "error")
                title = "Nouvelle Conversation"
            conversation_doc = {
                "id": conversation_id,
                "title": title,
                "created_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat().replace('T', ' ')
            }
            self.es_client.es.index(index=self.history_index_name, document=conversation_doc)
            print("HISTORY: Conversation created successfully")
            return True
        except Exception as e:
            self.activity_logger.log_interaction(f"Error creating conversation: {e}", "error")
            return False

       
    
    def add_message(self,message: str, conversation_id: str,role: str) -> bool:
        try:
            message_doc = {
                "id":"2345",
                "conversation_id": conversation_id,
                "message":message,
                "role": role,
                "timestamp": datetime.datetime.utcnow().replace(microsecond=0).isoformat().replace('T', ' ')
            }
            return self.add_message_to_history(self.message_index_name, message=message_doc)
        except Exception as e:
            self.activity_logger.log_interaction(f"Error adding message: {e}", "error")
            return False
        
    def create_history_index(self):    
        self.es_client.create_index(self.history_index_name, mappings=self.history_index_mapping)     
              
    def create_message_index(self):
        self.es_client.create_index(self.message_index_name, mappings=self.message_index_mapping)
    
    def add_message_to_history(self, index_name: str, message: Dict, ) -> bool:
        try:
            self.es_client.es.index(index=index_name, document=message)
            print("HISTORY: Message added successfully")
            return True    
        except Exception as e:
            self.activity_logger.log_interaction(f"Error adding message to history: {e}", "error")
            return False