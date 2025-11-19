from typing import Dict
import pandas as pd
import os
import re
import datetime
from core.vector_store.logger import ActivityLogger

class Preprocessor:
    """
    Pereprocess files based on their type.
    can both preprocess a file or a folder
    """

    def __init__(self, raw_path: str, clean_path: str):
        self.raw_path = raw_path # maybe not needed
        self.clean_path = clean_path
        self.activity_logger = ActivityLogger("preprocessor")

    # Process file
    def process_file(self, file_path: str) -> str:
        try : # Detect file type
            print(f"PREPROCESSING: Preprocessing file: {file_path}")
            json_result = None  
            if file_path.endswith('.csv'):
                json_result = self._process_csv(file_path)
            elif file_path.endswith('.html'):
                json_result = self._process_html(file_path)
            elif file_path.endswith('.txt'):
                json_result = self._process_txt(file_path)
        
            # save file type to clean_path
            if json_result:
                doc_title = json_result['doc_title']
                clean_file_path = os.path.join(self.clean_path, f"{doc_title}.json")
                with open(clean_file_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(json_result, f, ensure_ascii=False, indent=4)
                print(f"PREPROCESSING: Processed and saved: {clean_file_path}")
                return clean_file_path
            else:
                self.activity_logger.log_interaction(f"Skipping empty or invalid file: {file_path}", "warning")
                return ""
        except Exception as e:
            self.activity_logger.log_interaction(f"Error processing file {file_path}: {e}", "error")
            raise e

    # Process folder
    def process_folder(self, folder_path: str):
        try :
            fnames = [ os.path.join(folder_path, x) for x in os.listdir(folder_path) if x.endswith('.txt') or x.endswith('.csv') or x.endswith('.html')]
            for fname in fnames:
                self.process_file(fname)
        except Exception as e:
            self.activity_logger.log_interaction(f"Error processing folder {folder_path}: {e}", "error")
            raise e

    def _process_csv(self, file_path: str) -> Dict:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            df = df.dropna(axis=1, how='all')
            df = df.drop_duplicates()

            # here I will add a step to truncate the content if too long but in the funture we could chunk documents
            if len(df) > 20:
                df = df.head(20)
            json_data = df.to_dict(orient='records')
            date = self._extract_date(str(json_data))
            doc_title = os.path.splitext(os.path.basename(file_path))[0]
            json_result = {
                "doc_title": doc_title,
                "content": json_data,
                "metadata": {
                    "source": file_path,
                    "date": date,
                    "modified": datetime.datetime.now().strftime("%Y-%m-%d")
                }
            }
            print(f"PREPROCESSING: Processed CSV file: {file_path}")
            return json_result
        except Exception as e:
            self.activity_logger.log_interaction(f"Error processing CSV file {file_path}: {e}", "error")
            return {}
    
    def _process_html(self, file_path: str) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Verify if content is empty
            if not content.strip():
                print(f"Warning: The file {file_path} is empty.")
                return {}
            # Remove script and style tags
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
            # truncate the content if too long
            if len(content) > 800:
                content = content[:800]
            date = self._extract_date(content)
            doc_title = os.path.splitext(os.path.basename(file_path))[0]
            json_result = {
                "doc_title": doc_title,
                "content": content,
                "metadata": {
                    "source": file_path,
                    "date": date,
                    "modified": datetime.datetime.now().strftime("%Y-%m-%d")
                }
            }
            print(f"PREPROCESSING: Processed HTML file: {file_path}")
            return json_result
        except Exception as e:
            self.activity_logger.log_interaction(f"Error processing HTML file {file_path}: {e}", "error")
            return {}
        

    def _process_txt(self, file_path: str) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Verify if content is empty
            if not content.strip():
                print(f"Warning: The file {file_path} is empty.")
                return {}
        
            # remove extra new lines and spaces
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = content.strip()
            if len(content) > 800:
                content = content[:800]
            
            date = self._extract_date(content)
            doc_title = os.path.splitext(os.path.basename(file_path))[0]
            
            json_result = {
                "doc_title": doc_title,
                "content": content,
                "metadata": {
                    "source": file_path,
                    "date": date,
                    "modified": datetime.datetime.now().strftime("%Y-%m-%d")
                }
            }
            return json_result
            print(f"PREPROCESSING: Processed TXT file: {file_path}")
        except Exception as e:
            self.activity_logger.log_interaction(f"Error processing TXT file {file_path}: {e}", "error")
            return {}

    def _extract_date(self, text: str) -> str:
        try:
            # check if in the text there is a 4 digits starting by 20 and between 2000 and 2099
            match = re.search(r'20[0-9]{2}', text)
            if match:
                return match.group(0)
            return ""
        except Exception as e:
            self.activity_logger.log_interaction(f"Error extracting date from text: {e}", "error")
            return ""
        


