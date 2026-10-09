from fastapi import FastAPI
from routers.pdfroutes.pdf_router import router as pdf_router
from routers.chatbotroute.chatbot_routes import router as chatbot_router
from routers.EvaluationRoutes.evaluation_routes import router as eval_router

import os
import shutil
from Configs.config import settings
app = FastAPI()

app.include_router(pdf_router)
app.include_router(chatbot_router)
app.include_router(eval_router)

UPLOAD_DIR = settings.upload_dir

@app.on_event("shutdown")
def clear_upload_dir():
    """Clear the upload directory when FastAPI shuts down."""
    if os.path.exists(UPLOAD_DIR):
        # Remove all files inside the directory
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
        print("Upload directory cleared.")
