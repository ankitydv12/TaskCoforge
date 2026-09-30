import json
import os
from pathlib import Path

from fastapi import APIRouter, File, UploadFile , BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from chunkingservice import ChunkingService
from config import settings
from pdf_loader import load_pdf
from schemas import Document
from upload_service import UploadResult, save_pdf

from schemas import upload_progress

import uuid

router = APIRouter(tags=["pdf"])
chunker = ChunkingService(settings.chunk_size, settings.chunk_overlap)



def _line(payload: dict) -> str:
    return json.dumps(payload) + "\n"


def _process_file(path: Path, name: str) -> tuple[int, list[Document]]:
    """Blocking work: pypdf extraction + chunking. Runs in a worker thread."""
    pages = load_pdf(path, name)
    return len(pages), chunker.chunk_documents(pages)



@router.post("/process-pdfs")
async def process_pdfs(background_tasks: BackgroundTasks , files: list[UploadFile] = File(...)):
    print("hello")
    # Step 1: save every file first. Chunking never starts before all are uploaded.
    upload_id = str(uuid.uuid4())

    # Initialize immediately
    upload_progress[upload_id] = {
        "total": len(files),
        "uploaded": 0,
        "status": "queued"
    }

    background_tasks.add_task(save_pdf,
    upload_id,files
    )

    yield {
    "upload_id": upload_id,
    "total_files": len(files),
    "message": "Upload started"
    }
    pdf_files = [
        file
        for file in os.listdir(settings.upload_dir)
        if file.lower().endswith(".pdf")
    ]

    print(f"PDF files in upload dir: {pdf_files}")

    for pdf_file in pdf_files:
        print(f"Processing file: {pdf_file}")

        file_path = os.path.join(settings.upload_dir, pdf_file)

        try:
            page_count, docs = await run_in_threadpool(
                    _process_file,
                    Path(file_path),
                    pdf_file,
                )

            yield {
                    "event": "processed",
                    "file": pdf_file,
                    "pages_with_text": page_count,
                    "chunks": len(docs),
                }

        except ValueError as exc:
            yield {
                    "event": "processing_failed",
                    "file": pdf_file,
                    "error": str(exc),
                }

        finally:
            Path(file_path).unlink(missing_ok=True)  # Delete after processing


    
    
"""
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
"""

@router.get("/upload/{upload_id}/progress")
async def upload_progress_stream(upload_id: str):
 
    async def event_generator():
 
        while True:
 
            progress = upload_progress.get(upload_id)
 
            if progress is None:
                yield f"data: {json.dumps({'error': 'Upload ID not found'})}\n\n"
                break
 
            # Send progress to client
            yield f"data: {json.dumps(progress)}\n\n"
 
            # Stop when completed
            if progress["status"] == "completed":
                break
          
 
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )