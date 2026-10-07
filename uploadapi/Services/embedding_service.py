from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)


embedding = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# from langchain_huggingface import HuggingFaceEmbeddings

# embedding = HuggingFaceEmbeddings(
#     model_name='sentence-transformers/all-MiniLM-L6-v2'
# )