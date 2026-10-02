from pathlib import Path

from pypdf import PdfReader

from Schemas.schemas import Document

#TODO : for now source_name is optional later remove it 
def load_pdf(paths: list[str]) -> list[Document]:
    """One Document per non-empty page. Raises ValueError for unreadable PDFs."""

    print("load_pdf Executed ",len(paths))
    print(paths)
    # if(len(paths)) == 0:
    #     raise ValueError("No pdf in DIRECTORY")
    docs: list[Document] = []
    try:
        for path in paths:
            print(path)
            file_name = path.split("/")[-1]
            print(f"file name ---> {file_name}")
            
            print("Reading the PDF......")
            reader = PdfReader(str(path))
            print("PDF Readed...........")
            if reader.is_encrypted and reader.decrypt("") == 0:
                raise ValueError("PDF is password protected")

            total = len(reader.pages)
            print(f"Total Pages in pdfs : {total}")
                
            for i, page in enumerate(reader.pages, start=1):
                print(f"{i}th is going to be extracted.......")
                text = (page.extract_text() or "").strip()
                print(f"{i}th is Extracted")
                if text:
                    docs.append(Document(
                        page_content=text,
                        metadata={"file_name": file_name, "page": i, "total_pages": total},
                    ))
            
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Could not read PDF: {exc}") from exc
    return docs