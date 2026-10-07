import sys
from pathlib import Path
# uploadapi directory
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from langchain_text_splitters import CharacterTextSplitter
from Schemas.schemas import Document
from langchain_core.documents import Document as LCDocument
from langchain_experimental.text_splitter import SemanticChunker
from Services.chunking_embedding_model import embedding


class ChunkingServices:
    def cnvt_to_lngdoc(self,documents:list[Document]) -> list[LCDocument]:
        #TODO: add empty Validation
        lc_docs = [
                LCDocument(
                    page_content=doc.page_content,
                    metadata=doc.metadata
                    )
                    for doc in documents
                ]
        return lc_docs

    def character_chunk(self,documents:list[Document],chunk_size,chunk_overlap):

        lc_docs = self.cnvt_to_lngdoc(documents)

        splitter = CharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )

        result = splitter.split_documents(lc_docs)
        return result
    
    def semantic_chunking(self,documents:list[Document]):
        lc_docs = self.cnvt_to_lngdoc(documents)

        splitter = SemanticChunker(
            embeddings=embedding,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=85,  # Higher = fewer, larger chunks
        )

        result = splitter.split_documents(lc_docs)
        return result
            
chunk_services = ChunkingServices()

# if __name__ == "__main__":
#     chunk_services = ChunkingServices()
#     doc = Document(
#     page_content="This is a sample document chunk.",
#     metadata={
#         "source": "sample.pdf",
#         "page": 1
#     }
#     )

#     chunk_services.character_chunk([doc],5,2)


    