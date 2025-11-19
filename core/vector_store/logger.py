from core.vector_store.elastic_client import ElasticClient
from core.vector_store.mappings import LOGGER_INDEX_MAPPING
from core.config import LOGGER_INDEX_NAME
import datetime


class ActivityLogger:
    def __init__ (self, source: str = "system"):
        self.source = source
        self.logger_index_name = LOGGER_INDEX_NAME
        self.es_client = ElasticClient(hosts="http://localhost:9200")
        self.mapping = LOGGER_INDEX_MAPPING
        
    
    def create_index(self) -> bool:
        try :
            if not self.es_client.es.indices.exists(index=self.logger_index_name):
                self.es_client.es.indices.create(
                    index=self.logger_index_name,
                    body={
                        "mappings": self.mapping
                    }
                )
            print(f"Index {self.logger_index_name} created successfully.")
            return True
        except Exception as e:
            print(f"Error creating index {self.logger_index_name}: {e}")
            return False
        
    
    def log_interaction(self, interaction: str, level: str) -> bool:
        try:
            # log action to terminal
            print(f"{self.source.upper()}: {interaction}")
            self.es_client.es.index(
                index=self.logger_index_name,
                body={
                    "interaction": interaction,
                    "level": level,
                    "source": self.source,
                    "timestamp": datetime.datetime.utcnow().replace(microsecond=0).isoformat().replace('T', ' ')
                    
                }
            )
            return True
        except Exception as e:
            print(f"Error logging interaction to {self.logger_index_name}: {e}")
            return False