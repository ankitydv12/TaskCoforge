import json
import os
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from chunkingservice import ChunkingService
from config import settings
from pdf_loader import load_pdf
from schemas import Document
from upload_service import UploadResult, save_pdf

router = APIRouter(tags=["pdf"])
chunker = ChunkingService(settings.chunk_size, settings.chunk_overlap)


def _line(payload: dict) -> str:
    return json.dumps(payload) + "\n"


def _process_file(path: Path, name: str) -> tuple[int, list[Document]]:
    """Blocking work: pypdf extraction + chunking. Runs in a worker thread."""
    pages = load_pdf(path, name)
    return len(pages), chunker.chunk_documents(pages)


@router.post("/process-pdfs")
async def process_pdfs(files: list[UploadFile] = File(...)):
    print("hello")
    # Step 1: save every file first. Chunking never starts before all are uploaded.
    results: list[UploadResult] = [await save_pdf(f) for f in files]
    uploaded = [r for r in results if r.ok]
    failed = [r for r in results if not r.ok]

    async def stream():
        all_documents: list[Document] = []
        processed = 0
        try:
            # Step 2: report how many files reached the server.
            yield _line({
                "event": "upload_summary",
                "files_received": len(results),
                "files_uploaded": len(uploaded),
                "files_failed": len(failed),
            })
            for r in failed:
                yield _line({"event": "upload_failed", "file": r.original_name, "error": r.error})

            # Step 3: extract text and chunk, one file at a time.
            for r in uploaded:
                try:
                    page_count, docs = await run_in_threadpool(
                        _process_file, r.saved_path, r.original_name
                    )
                    all_documents.extend(docs)
                    processed += 1
                    yield _line({
                        "event": "processed",
                        "file": r.original_name,
                        "pages_with_text": page_count,
                        "chunks": len(docs),
                    })
                except ValueError as exc:
                    yield _line({"event": "processing_failed", "file": r.original_name, "error": str(exc)})
                finally:
                    Path(r.saved_path).unlink(missing_ok=True)  # delete after processing

            # TODO: send `all_documents` (list[Document]) to the vector store here.
            yield _line({
                "event": "completed",
                "files_uploaded": len(uploaded),
                "files_processed": processed,
                "total_chunks": len(all_documents),
            })
        finally:
            # Also clean up if the client disconnects mid-stream.
            for r in uploaded:
                if os.path.exists(r.saved_path):
                    os.remove(r.saved_path)

    return StreamingResponse(stream(), media_type="application/x-ndjson")