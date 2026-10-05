from fastapi import FastAPI 
from fastapi.responses import StreamingResponse
import time

app = FastAPI()

def fake_video_streamer():
    for i in range(10):
        yield f"frame {i} \n"
        time.sleep(2)


@app.get("/stream")
async def stream_frame():
    return StreamingResponse(fake_video_streamer(),media_type="text/plain")
