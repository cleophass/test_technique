# this will be called when launchin app to verify that everithing is setup

# Script to manually init template data already in "raw file"
import os
from core.vector_store.documents_manager import DocumentsManager
from core.vector_store.history import History
from core.config import DOCUMENTS_INDEX_NAME, HISTORY_INDEX_NAME, MESSAGE_INDEX_NAME
from core.vector_store.logger import ActivityLogger

class Setup:
    
    
    def __init__(self,):
        self.raw_folder = "data/raw"
        self.clean_folder = "data/clean"
        self.documents_index_name = DOCUMENTS_INDEX_NAME
        self.history_index_name = HISTORY_INDEX_NAME
        self.message_index_name = MESSAGE_INDEX_NAME
        self.activity_logger = ActivityLogger(source="setup")

    def verify_setup(self) -> bool:
        try: 
            print("SETUP: Verifying logger setup")
            if self.activity_logger.es_client.verify_index(self.activity_logger.logger_index_name):
                print("SETUP: Logger index exist")
            else :
                print("SETUP: Logger index do not exist")
                self.activity_logger.create_index()
        except Exception as e:
            self.activity_logger.log_interaction(f"logger setup error : {e}", "error")
            return False
            
        
        try : 
            print("SETUP: Verifying document setup")
            os.makedirs(self.raw_folder, exist_ok=True)
            os.makedirs(self.clean_folder, exist_ok=True)
            
            
            raw_fnames = [ os.path.join(self.raw_folder, x) for x in os.listdir(self.raw_folder) if x.endswith('.txt') or x.endswith('.csv') or x.endswith('.html')]
            clean_fnames = [ os.path.join(self.clean_folder, x) for x in os.listdir(self.clean_folder) if x.endswith('.json')]
            
            
            if len(raw_fnames) != len(clean_fnames) :    
                print("SETUP: Initializing DocumentsManager...")
                doc_manager = DocumentsManager(
                raw_path="data/raw",
                clean_path="data/clean"
            )
                print("SETUP: DocumentsManager initialized successfully")
                
                print("SETUP: Verify that index as been created...")
                if doc_manager.es_client.verify_index(self.documents_index_name):
                    print("SETUP: Index exist")
                else :
                    print("SETUP: Index does not exist")
                    doc_manager.create_document_index()
            

                print("SETUP: Starting to process folder...")
                doc_manager.process_folder("documents_index","data/raw")
            else:
                print("SETUP: Documents already processed.")
        except Exception as e:
            self.activity_logger.log_interaction(f"documents processing error : {e}", "error")
            return False
        


        try :
            print("SETUP: Verifying history setup")
            history_manager = History()
            if history_manager.es_client.verify_index(self.history_index_name):
                print("SETUP: history index exist")
            else : 
                print("SETUP: history index do not exist")
                history_manager.create_history_index()
            print("SETUP: History setup verified")
            if history_manager.es_client.verify_index(self.message_index_name):
                print("SETUP: message index exist")
            else :
                print("SETUP: message index do not exist")
                history_manager.create_message_index()
        except Exception as e:
            self.activity_logger.log_interaction(f"error : {e}", "error")
            return False
        return True