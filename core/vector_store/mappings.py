embeddings_dimension = 768

HISTORY_INDEX_MAPPING = {
    "properties": {
        "id": {
            "type": "keyword"
        },
        "created_at": {
            "type": "date",
            "format": "yyyy-MM-dd HH:mm:ss"
        },
        "name": {
            "type": "text"
        }
    }
}

MESSAGE_INDEX_MAPPING = {
            "properties": {
            "id": {"type": "text",},
            "conversation_id": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "message": { "type": "text"  },
            "timestamp": { "type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis" },
            "role": { "type": "keyword"  }
        } }

DOCUMENT_INDEX_MAPPING ={
                        "properties": {
                            "doc_title": { "type": "text"  },
                            "content": { "type": "text"  },
                            "embeddings": { "type": "dense_vector", "dims": embeddings_dimension},
                            "metadata": {
                                "properties": {
                                    "source": { "type": "keyword" },
                                    "date": { "type": "date", "format": "yyyy-MM-dd||yyyy" },
                                    "modified": { "type": "date", "format": "yyyy-MM-dd" },
                                    "embedding_model": { "type": "keyword" },
                                    "embedding_date": { "type": "date", "format": "yyyy-MM-dd" },
                                    "embedding_dimension": { "type": "integer" }
                                }
                            },
                            "indexed_at": {"type": "date"}
                        } }

LOGGER_INDEX_MAPPING = {
    "properties": {
        "timestamp": { "type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis" },
        "level": {
            "type": "keyword"
        },
        "message": {
            "type": "text"
        },

        "source": {
            "type": "keyword"
        }
    }
}