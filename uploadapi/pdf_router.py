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
import asyncio


router = APIRouter(tags=["pdf"])
chunker = ChunkingService(settings.chunk_size, settings.chunk_overlap)



def _line(payload: dict) -> str:
    return json.dumps(payload) + "\n"


def _process_file(path: Path, name: str) -> tuple[int, list[Document]]:
    """Blocking work: pypdf extraction + chunking. Runs in a worker thread."""
    pages = load_pdf(path, name)
    return len(pages), chunker.chunk_documents(pages)



@router.post("/process-pdfs")
async def process_pdfs(background_task:BackgroundTasks,files: list[UploadFile] = File(...)):
    print("hello")
    # Step 1: save every file first. Chunking never starts before all are uploaded.
    #TODO: Remove hard code 
    upload_id = "abc"
    # upload_id = str(uuid.uuid4())

    # Initialize immediately
    upload_progress[upload_id] = {
        "total": len(files),
        "uploaded": 0,
        "status": "queued"
    }

    background_task.add_task(
        save_pdf,
        upload_id,
        files
    )
    
    return{
    "upload_id": upload_id,
    "total_files": len(files),
    "message": "Upload started"
    }
    
@router.get("/upload/{upload_id}/progress")
async def upload_progress_stream(upload_id: str):
 
    async def event_generator():
 
        while True:
 
            progress = upload_progress.get(upload_id)
 
            if progress is None:
                yield f"data: {json.dumps({'error': 'Upload ID not found'})}\n\n"
                return
 
            # Send progress to client
            yield f"data: {json.dumps(progress)}\n\n"
 
            # Stop when completed
            if progress["status"] == "uploaded":
                return
            await asyncio.sleep(1)   
 
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )