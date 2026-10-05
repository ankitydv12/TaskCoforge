import sys
from pathlib import Path
# uploadapi directory
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from langchain_text_splitters import CharacterTextSplitter
from Schemas.schemas import Document
from langchain_core.documents import Document as LCDocument


class ChunkingServices:
    def character_chunk(self,documents:list[Document],chunk_size,chunk_overlap):
        lc_docs = [
        LCDocument(
            page_content=doc.page_content,
            metadata=doc.metadata
            )
            for doc in documents
        ]
        splitter = CharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
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


    