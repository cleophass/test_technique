from core.embeddings import Embedder
from core.types import Embeddings, Document, DocumentMetadata
from core.vector_store.elastic_client import ElasticClient
from core.preprocessing import Preprocessor
import json
import datetime
import os

class DocumentsManager:
    def __init__(self, raw_path: str, clean_path: str):
        self.embedder = Embedder()
        self.es_client = ElasticClient(hosts="http://localhost:9200")
        self.preprocessor = Preprocessor(raw_path=raw_path, clean_path=clean_path)
            
    def add_document(self, index_name: str, document_path: str) -> bool:
        # this function will be called after loading a documents from streamlit
        # first preprocess the document
        clean_file_path = self.preprocessor.process_file(document_path)
        if not clean_file_path:
            print("Failed to preprocess document.")
            return False
        # read file as json
        with open(clean_file_path, "r", encoding="utf-8") as file:
            document_content = file.read()
            document_content = json.loads(document_content)
        
        # embed file
        embedded_doc = self.embed_document(clean_file_path)
        
        # create DocumentMetadata
        metadata = DocumentMetadata(
            source=document_content.get("metadata", {}).get("source", ""),
            date=document_content.get("metadata", {}).get("date"),
            modified=document_content.get("metadata", {}).get("modified"),
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

        res = self.es_client.index_document(index_name, document)
        return res
    
    # manage also embeddings
    def embed_document(self, document_path: str) -> Embeddings:
        # load the cleaned document
        with open(document_path, "r", encoding="utf-8") as file:
            document_content = file.read()
        # embed the content
        embedded_doc = self.embedder.embed_text(document_content)
        return embedded_doc

    # delete also documents
    def delete_document(self, index_name: str, document_id: str, doc_name: str, full_path: str) -> bool:
        # we will also delete from folder raw and clean but we will need to get both file path and extension
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
            print(f"Error deleting files: {e}") 
            
        res = self.es_client.delete_document(index_name, document_id)
        # delete from both raw and clean folders if needed
        
        return res

    def process_folder(self, index_name: str, folder_path: str):
        import os
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                self.add_document(index_name, file_path)