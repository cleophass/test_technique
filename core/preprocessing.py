from typing import Dict
import pandas as pd
import os
import re
import datetime

class Preprocessor:
    """
    Pereprocess files based on their type.
    can both preprocess a file or a folder
    """

    def __init__(self, raw_path: str, clean_path: str):
        self.raw_path = raw_path # maybe not needed
        self.clean_path = clean_path

    # Main function

    # Process file
    def process_file(self, file_path: str) -> str:
        print("file_path:", file_path)
        # Detect file type
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
            print(f"Processed and saved: {clean_file_path}")
            return clean_file_path
        else:
            print(f"Skipping empty or invalid file: {file_path}")
            return ""

    # Process folder
    def process_folder(self, folder_path: str):
        fnames = [ os.path.join(folder_path, x) for x in os.listdir(folder_path) if x.endswith('.txt') or x.endswith('.csv') or x.endswith('.html')]
        for fname in fnames:
            self.process_file(fname)

    def _process_csv(self, file_path: str) -> Dict:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except Exception as e:
            print("Error reading CSV file:", e)
        df = df.dropna(axis=1, how='all')
        df = df.drop_duplicates()
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
        return json_result
    
    def _process_html(self, file_path: str) -> Dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Verify if content is empty
        if not content.strip():
            print(f"Warning: The file {file_path} is empty.")
            return {}
        # Remove script and style tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
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
            
        

    def _process_txt(self, file_path: str) -> Dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Verify if content is empty
        if not content.strip():
            print(f"Warning: The file {file_path} is empty.")
            return {}
    
        # remove extra new lines and spaces
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
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

    def _extract_date(self, text: str) -> str:
        # check if in the text there is a 4 digits starting by 20 and between 2000 and 2099
        match = re.search(r'20[0-9]{2}', text)
        if match:
            return match.group(0)
        return ""
    


