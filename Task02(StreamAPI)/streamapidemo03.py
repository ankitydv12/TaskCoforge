"""
FastAPI’s asynchronous nature makes it well-suited for streaming responses. 
By using async and await, you can ensure that your streaming doesn’t block other parts of your application, 
allowing you to handle multiple clients simultaneously without sacrificing performance.
"""

from fastapi import FastAPI 
from fastapi.responses import StreamingResponse
import aiofiles

app = FastAPI()

async def async_file_reader():
    file_path = "D:/Task01ChunkStra/Task01/uploads/Chunking_Strategy_Task_Project.pdf"

    with aiofiles.open(file_path,"wb") as file:
        while chunk := await file.read(1024):
            yield chunk

@app.get("/download")
async def download_file():
    return StreamingResponse(
        async_file_reader() , media_type="application/octet-stream"
    )