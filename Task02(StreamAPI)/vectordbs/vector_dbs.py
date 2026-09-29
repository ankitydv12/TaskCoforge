import chromadb
import os

from Task01.embedding import embedding

import hashlib
from typing import List

CHROMA_DIR = "./chroma_db"
os.makedirs(CHROMA_DIR, exist_ok=True)

class ChromaServices:
    def get_chroma_client(self):
        client = chromadb.PersistentClient(CHROMA_DIR)
        return client

    def get_chromadb(self , collection_name:str):

        #Creating a persistent client
        client = self.get_chroma_client() 

        # TODO: Add validations for collection name and embeddong function

        #creating a collection_name 
        collection = client.get_or_create_collection(
            name = collection_name ,
            embedding_function = embedding
        )

        return client

    def add_documents_to_chroma(self ,documents: List[Document], file_id: str , collection_name : str) -> List[str]:
        
        client = self.get_chroma_client()
        collection = client.get_collection(collection_name)
    
        # tag every chunk with file_id so we can filter/delete/update by source later
        for doc in documents:
            doc.metadata["file_id"] = file_id
    
        collection.upsert(
            ids = [self.create_chunk_id(file_id , _.page_content) for _ in documents] ,
            documents = [d.page_content for d in documents],
            metadatas = [d.metadata for d in documents]
        )
    
        print("No of vector in chroma ",collection.count())

    def create_chunk_id(file_id:str,content:str):
        return hashlib.sha256(
            f"{file_id} : {content}".encode("utf-8")
        ).hexdigest()



