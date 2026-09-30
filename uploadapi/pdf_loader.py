from pathlib import Path

from pypdf import PdfReader

from schemas import Document


def load_pdf(path: Path, source_name: str) -> list[Document]:
    """One Document per non-empty page. Raises ValueError for unreadable PDFs."""
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted and reader.decrypt("") == 0:
            raise ValueError("PDF is password protected")

        total = len(reader.pages)
        docs: list[Document] = []
        for i, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                docs.append(Document(
                    page_content=text,
                    metadata={"source": source_name, "page": i, "total_pages": total},
                ))
        return docs
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Could not read PDF: {exc}") from exc