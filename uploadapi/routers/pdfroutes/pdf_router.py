import asyncio
import json
import os
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    UploadFile,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from Configs.config import settings
from Schemas.schemas import upload_progress
from Services.pdf_loader import load_pdf
from Services.upload_service import save_pdf
from Services.vector_services import chroma_services
import time


router = APIRouter(tags=["pdf"])
# chunker = ChunkingService(settings.chunk_size, settings.chunk_overlap)



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
        process_upload,
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
                break
            await asyncio.sleep(1)
 
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


async def process_upload(upload_id: str, files: list[UploadFile]):

    upload_progress[upload_id]["status"] = "uploading"

    start = time.perf_counter()

    await  save_pdf(upload_id, files)

    upload_progress[upload_id]["status"] = "parsing"

    pdfs_path_list = [
        os.path.join(settings.upload_dir, pdf)
        for pdf in os.listdir(settings.upload_dir)
        if pdf.lower().endswith(".pdf")
    ]

    docs = await run_in_threadpool(load_pdf,pdfs_path_list)

    upload_progress[upload_id]["status"] = "adding to vector"

    await run_in_threadpool(
        chroma_services.add_documents_to_chroma,
        docs,
        "collection1"
    )

    end = time.perf_counter() - start
    print(f"Total Time Taken {end}")

    # --------------------------------
    # 4. Completed
    # --------------------------------

    upload_progress[upload_id]["status"] = "completed"


