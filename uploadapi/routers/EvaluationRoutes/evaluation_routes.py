from fastapi import APIRouter
from Evaluation.dataset_generation import generate_eval_questions
from Services.vector_services import chroma_services
from chatbot.chatbot import model
import os
from dotenv import load_dotenv
load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "collection1")

router = APIRouter(tags=["evaluation"])


@router.post("/eval/generate_dataset")
async def generate_dataset_endpoint(filename:str | None = None):
    print("generate_dataset_endpoint called")
    """Endpoint to generate evaluation dataset from a document."""

    document_text = chroma_services.get_all_doc("collection1", filename)
    document_text = document_text[20:23]

    for chunk in document_text:
        await generate_eval_questions(
                        chunk, 
                        num_questions=3, 
            )


