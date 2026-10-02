from fastapi import FastAPI
from routers.pdfroutes.pdf_router import router as pdf_router

app = FastAPI()
app.include_router(pdf_router)