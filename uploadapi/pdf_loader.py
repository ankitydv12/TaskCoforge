from pathlib import Path

from pypdf import PdfReader

from schemas import Document

#TODO : for now source_name is optional later remove it 
def load_pdf(paths: list[str]) -> list[Document]:
    """One Document per non-empty page. Raises ValueError for unreadable PDFs."""

    print("load_pdf Executed ",len(paths))
    # if(len(paths)) == 0:
    #     raise ValueError("No pdf in DIRECTORY")
    docs: list[Document] = []
    for path in paths:
        print(path)
        source_name = path.split("/")[-1]
        print(f"file name ---> {source_name}")
        try:
            reader = PdfReader(str(path))
            if reader.is_encrypted and reader.decrypt("") == 0:
                raise ValueError("PDF is password protected")

            total = len(reader.pages)
            
            for i, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if text:
                    docs.append(Document(
                        page_content=text,
                        metadata={"source": source_name, "page": i, "total_pages": total},
                    ))
            
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"Could not read PDF: {exc}") from exc
        return docs