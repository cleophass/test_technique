from core.embeddings import Embedder
from core.types import Embeddings, Document, DocumentMetadata
from core.vector_store.elastic_client import ElasticClient
from core.preprocessing import Preprocessor
import json
import datetime
import os
from core.vector_store.mappings import DOCUMENT_INDEX_MAPPING
from core.config import DOCUMENTS_INDEX_NAME
from core.vector_store.logger import ActivityLogger

class DocumentsManager:
    def __init__(self, raw_path: str, clean_path: str):
        self.embedder = Embedder()
        self.es_client = ElasticClient(hosts="http://localhost:9200")
        self.preprocessor = Preprocessor(raw_path=raw_path, clean_path=clean_path)
        self.document_index_mapping = DOCUMENT_INDEX_MAPPING
        self.documents_index_name = DOCUMENTS_INDEX_NAME
        self.activity_logger = ActivityLogger("documents_manager")
        
    def create_document_index(self):
        self.es_client.create_index(self.documents_index_name, mappings=self.document_index_mapping)
            
    def add_document(self, index_name: str, document_path: str) -> bool:
        # this function will be called after loading a documents from streamlit
        # first preprocess the document
        try:
            clean_file_path = self.preprocessor.process_file(document_path)
            if not clean_file_path:
                self.activity_logger.log_interaction(f"Failed to preprocess document: {document_path}", "error")
                return False
        except Exception as e:
            self.activity_logger.log_interaction(f"Error preprocessing document: {e}", "error")
            return False
            
        # read file as json
        try:
            with open(clean_file_path, "r", encoding="utf-8") as file:
                document_content = file.read()
                document_content = json.loads(document_content)
        except Exception as e:
            self.activity_logger.log_interaction(f"Error reading or parsing JSON file: {e}", "error")
            return False
        
        # embed file
        try:
            embedded_doc = self.embed_document(clean_file_path)
        except Exception as e:
            self.activity_logger.log_interaction(f"Error embedding document: {e}", "error")
            return False
        
        # create DocumentMetadata
        try:
            doc_metadata = document_content.get("metadata", {})
            date_value = doc_metadata.get("date")
            modified_value = doc_metadata.get("modified")
            
            date_value = date_value if date_value else None
            modified_value = modified_value if modified_value else None

            metadata = DocumentMetadata(
                source=document_content.get("metadata", {}).get("source", ""),
                date=date_value,
                modified=modified_value,
                embedding_model=embedded_doc.metadata.embedding_model,
                embedding_date=embedded_doc.metadata.embedding_date,
                embedding_dimension=embedded_doc.metadata.embedding_dimension
            )

            document = Document(
                doc_title=document_content.get("doc_title", "untitled"),
                content=str(document_content.get("content", "")), 
                embeddings=embedded_doc.embeddings,
                metadata=metadata,
                indexed_at=datetime.datetime.now())
        except Exception as e:
            self.activity_logger.log_interaction(f"Error creating document metadata or document: {e}", "error")
            return False

        try:
            res = self.es_client.index_document(index_name, document)
            self.activity_logger.log_interaction(f"Indexed document to Elasticsearch: {document.doc_title}", "info")
            return res
        except Exception as e:
            self.activity_logger.log_interaction(f"Error indexing document to Elasticsearch: {e}", "error")
            return False
    
    # manage also embeddings
    def embed_document(self, document_path: str) -> Embeddings:
        # load the cleaned document
        try:
            with open(document_path, "r", encoding="utf-8") as file:
                document_content = file.read()
            # embed the content
            embedded_doc = self.embedder.embed_text(document_content)
            return embedded_doc
        except Exception as e:
            self.activity_logger.log_interaction(f"Error embedding document content: {e}", "error")
            raise e

    # delete also documents
    def delete_document(self, index_name: str, document_id: str, doc_name: str, full_path: str) -> bool:
        # we will also delete from folder raw and clean but we will need to get both file path and extension
        try:
            _, file_extension = os.path.splitext(full_path)
            raw_file_path = os.path.join(self.preprocessor.raw_path, doc_name + file_extension)
            clean_file_path = os.path.join(self.preprocessor.clean_path, doc_name + ".json")
            # delete files
            try:
                if os.path.exists(raw_file_path):
                    os.remove(raw_file_path)
                if os.path.exists(clean_file_path):
                    os.remove(clean_file_path)
            except Exception as e:
                self.activity_logger.log_interaction(f"Error deleting files: {e}", "error") 
                
            res = self.es_client.delete_document(index_name, document_id)
            # delete from both raw and clean folders if needed
            
            return res
        except Exception as e:
            self.activity_logger.log_interaction(f"Error deleting document: {e}", "error")
            return False

    def process_folder(self, index_name: str, folder_path: str):
        try:
            import os
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    self.add_document(index_name, file_path)
        except Exception as e:
            self.activity_logger.log_interaction(f"Error processing folder {folder_path}: {e}", "error")
            raise e