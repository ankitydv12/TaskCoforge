from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from pathlib import Path
import uuid
import asyncio
import json
 
app = FastAPI()
 
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
 
# Learning purpose only.
# Production: use Redis/database instead of an in-memory dictionary.
upload_progress = {}
 
 
async def save_files(upload_id: str, files: list[UploadFile]):
    total_files = len(files)
 
    upload_progress[upload_id] = {
        "total": total_files,
        "uploaded": 0,
        "status": "processing"
    }
 
    for index, file in enumerate(files, start=1):
 
        # Create unique filename
        filename = f"{uuid.uuid4()}_{file.filename}"
 
        file_path = UPLOAD_DIR / filename
 
        # Save file in chunks
        with open(file_path, "wb") as buffer:
 
            while True:
                chunk = await file.read(1024 * 1024)  # 1 MB
 
                if not chunk:
                    break
 
                buffer.write(chunk)
 
        await file.close()
 
        # Update progress
        upload_progress[upload_id]["uploaded"] = index
 
        # Small delay just to demonstrate streaming
        # Remove this in real application
        await asyncio.sleep(0.1)
 
    upload_progress[upload_id]["status"] = "completed"
 
 
@app.post("/upload")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...)
):
    upload_id = str(uuid.uuid4())
 
    # Initialize immediately
    upload_progress[upload_id] = {
        "total": len(files),
        "uploaded": 0,
        "status": "queued"
    }
 
    # Start file processing in background
    background_tasks.add_task(
        save_files,
        upload_id,
        files
    )
 
    return {
        "upload_id": upload_id,
        "total_files": len(files),
        "message": "Upload started"
    }
 
 
@app.get("/upload/{upload_id}/progress")
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
 
            await asyncio.sleep(0.5)
 
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
 