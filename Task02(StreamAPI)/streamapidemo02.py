from fastapi import FastAPI 
from fastapi.responses import StreamingResponse

app = FastAPI()


def file_reader():
    file_path = "D:/Task01ChunkStra/Task01/uploads/Chunking_Strategy_Task_Project.pdf"

    with open(file_path, "wb") as file:
        while chunk := file.read(1024):
            yield str(chunk)

@app.get("/download")
def download():
    return StreamingResponse(file_reader(),media_type="application/octet-stream")

