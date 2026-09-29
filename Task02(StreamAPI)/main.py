from fastapi import FastAPI , File , UploadFile
from vectordbs.vector_dbs import (
    get_chroma_db ,
    add_documents_to_chroma
)

from schema import Document

app = FastAPI()

COLLECTION_NAME = "collection1"


@app.post("/uploadfile")
def uploadfile(file : list[UploadFile] = File(...)):

    #TODO: Extract from the pdf and chunk it 
    documents = extractpdf_and_get_chunks()

    client = get_chroma_db(COLLECTION_NAME)

    add_documents_to_chroma(documents,file_id,COLLECTION_NAME)




