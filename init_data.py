# Script to manually init template data already in "raw file"
from core.vector_store.documents_manager import DocumentsManager

print("Initializing DocumentsManager...")
doc_manager = DocumentsManager(
    raw_path="data/raw",
    clean_path="data/clean"
)
print("DocumentsManager initialized successfully")

print("Starting to process folder...")
doc_manager.process_folder("documents_index","data/raw")
print("Folder processing completed")