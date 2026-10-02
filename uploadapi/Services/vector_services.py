import chromadb
import os

from Services.embedding_service import embedding

import hashlib
from typing import List

from fastapi  import  HTTPException , status

from Schemas.schemas import Document

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
        if collection_name not in client.list_collections():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Collection does not exits"
            )
        if embedding  is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="embedding does not exits"
            )

        #creating a collection_name 
        collection = client.get_or_create_collection(
            name = collection_name ,
            embedding_function = embedding
        )

        return client

    def add_documents_to_chroma(self ,documents: List[Document], file_name: str , collection_name : str) -> List[str]:
        
        client = self.get_chroma_client()
        collection = client.get_collection(collection_name)
    
        # tag every chunk with file_name so we can filter/delete/update by source later
        for doc in documents:
            doc.metadata["file_name"] = file_name
    
        collection.upsert(
            ids = [self.create_chunk_id(file_name , _.page_content) for _ in documents] ,
            documents = [d.page_content for d in documents],
            metadatas = [d.metadata for d in documents]
        )
    
        print("No of vector in chroma ",collection.count())

    def create_chunk_id(file_name:str,content:str):
        return hashlib.sha256(
            f"{file_name} : {content}".encode("utf-8")
        ).hexdigest()


