from dotenv import load_dotenv
import os
load_dotenv()
EMBEDDINGS_MODEL_NAME="paraphrase-multilingual-mpnet-base-v2"
REWRITER_MODEL_NAME="gpt-4.1"
GUARDRAILS_MODEL_NAME="gpt-4.1"
HYDE_MODEL_NAME="gpt-4.1"
GENERATOR_MODEL_NAME="gpt-4.1"
TITLE_MODEL_NAME="gpt-4.1"
RERANKER_MODEL_NAME="antoinelouis/crossencoder-camembert-base-mmarcoFR"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


DOCUMENTS_INDEX_NAME="documents_index"
HISTORY_INDEX_NAME="history_index"
MESSAGE_INDEX_NAME="message_index"
LOGGER_INDEX_NAME="logger_index"