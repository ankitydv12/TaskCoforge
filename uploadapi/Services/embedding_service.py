from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)


embedding = SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)