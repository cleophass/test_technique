# this will be called when launchin app to verify that everithing is setup

# Script to manually init template data already in "raw file"
import os
from core.vector_store.documents_manager import DocumentsManager
from core.vector_store.history import History
from core.config import DOCUMENTS_INDEX_NAME, HISTORY_INDEX_NAME, MESSAGE_INDEX_NAME


class Setup:
    
    
    def __init__(self,):
        self.raw_folder = "data/raw"
        self.clean_folder = "data/clean"
        self.documents_index_name = DOCUMENTS_INDEX_NAME
        self.history_index_name = HISTORY_INDEX_NAME
        self.message_index_name = MESSAGE_INDEX_NAME

    def verify_setup(self) -> bool:
        try : 
            print("Verifying document setup")
            
            raw_fnames = [ os.path.join(self.raw_folder, x) for x in os.listdir(self.raw_folder) if x.endswith('.txt') or x.endswith('.csv') or x.endswith('.html')]
            clean_fnames = [ os.path.join(self.clean_folder, x) for x in os.listdir(self.clean_folder) if x.endswith('.txt') or x.endswith('.csv') or x.endswith('.html')]
            
            if len(raw_fnames) != len(clean_fnames) :    
                print("Initializing DocumentsManager...")
                doc_manager = DocumentsManager(
                raw_path="data/raw",
                clean_path="data/clean"
            )
                print("DocumentsManager initialized successfully")
                
                print("Verify that index as been created...")
                if doc_manager.es_client.verify_index(self.documents_index_name):
                    print("Index exist")
                else :
                    print("Index does not exist")
                    doc_manager.create_document_index()
            

                print("Starting to process folder...")
                doc_manager.process_folder("documents_index","data/raw")
                print("Folder processing completed")
            else:
                print("Documents already processed.")
        except Exception as e:
            print("documents processing error : ",e)
            return False
        


        try :
            print("Verifying history setup")
            history_manager = History()
            if history_manager.es_client.verify_index(self.history_index_name):
                print("exist")
            else : 
                print("do not exist")
                history_manager.create_history_index()
            print("History setup verified")
            if history_manager.es_client.verify_index(self.message_index_name):
                print("exist")
            else :
                print("do not exist")
                history_manager.create_message_index()
        except Exception as e:
            print("error : ",e)
            return False
        return True