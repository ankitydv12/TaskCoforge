from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)


embedding = SentenceTransformerEmbeddingFunction(
    model_name=r"D:\all-MiniLM-L6-v2"
)