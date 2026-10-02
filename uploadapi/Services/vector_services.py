import hashlib
import os
from typing import List, Tuple

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from fastapi import HTTPException, status

from Schemas.schemas import Document
from Services.embedding_service import embedding


CHROMA_DIR = "./chroma_db"
os.makedirs(CHROMA_DIR, exist_ok=True)


class ChromaServices:

    def get_chroma_client(self) -> ClientAPI:
        client: ClientAPI = chromadb.PersistentClient(CHROMA_DIR)
        return client

    def get_chromadb(
        self,
        collection_name: str
    ) -> Tuple[ClientAPI, Collection]:

        client = self.get_chroma_client()

        if embedding is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Embedding does not exist"
            )

        collection: Collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding
        )

        return client, collection

    def add_documents_to_chroma(
        self,
        documents: List[Document],
        collection_name: str
    ) -> List[str]:

        client = self.get_chroma_client()

        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding
        )

        # Create one unique ID for every document/chunk
        ids = [
            self.create_chunk_id(doc)
            for doc in documents
        ]

        collection.upsert(
            ids=ids,
            documents=[
                doc.page_content
                for doc in documents
            ],
            metadatas=[
                doc.metadata
                for doc in documents
            ]
        )

        print(
            "No of vectors in Chroma:",
            collection.count()
        )

        return ids

    @staticmethod
    def create_chunk_id(doc: Document) -> str:

        file_name = doc.metadata["file_name"]
        page = doc.metadata["page"]
        content = doc.page_content

        raw_id = f"{file_name}:{page}:{content}"

        return hashlib.sha256(
            raw_id.encode("utf-8")
        ).hexdigest()


chroma_services = ChromaServices()