from fastapi import APIRouter , HTTPException , status
from Evaluation.dataset_generation import generate_eval_questions
from Services.vector_services import chroma_services
from chatbot.chatbot import model
import os
import csv
from dotenv import load_dotenv
from Evaluation.evaluation_pipeline import evaluate_rag_pipeline
from Services.llm_services import LLMService


load_dotenv()

import sys

COLLECTION_NAME = os.getenv("COLLECTION_NAME")

router = APIRouter(tags=["evaluation"])


@router.post("/eval/generate_dataset")
async def generate_dataset_endpoint(filename:str | None = None):
    print("generate_dataset_endpoint called")
    """Endpoint to generate evaluation dataset from a document."""

    document_text = chroma_services.get_all_doc(str(COLLECTION_NAME), filename)

    if document_text is None or len(document_text) == 0:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail="chunk of the length for data generation is 0")

    for i , chunk in enumerate(document_text):
        sys.stdout.write(f"Chunk {i}: {chunk}\n")

    
    selected_chunks = document_text[18:19]
    print("length of the document for question ",len(selected_chunks))
    
    generated_questions = []

    for chunk in selected_chunks:

        questions = await generate_eval_questions(
            chunk=chunk,
            num_questions=3,
        )

        generated_questions.extend(questions)

    return {
        "message": "Evaluation dataset generated successfully",
        "chunks_processed": len(selected_chunks),
        "questions_generated": len(generated_questions),
        "data": generated_questions,
    }

@router.get("/eval/test")
async def evalution_test():
    # Question from the evalution_dataset.csv
    with open('evalution_dataset.csv','r',newline='') as csv_file:

        reader = csv.DictReader(csv_file,delimiter='|')

        golden_dataset = [row for row in reader]

        print(golden_dataset)
        print("length of the golden dataset ",len(golden_dataset))
        print("type of the golden dataset ",type(golden_dataset))
        print("Calling the evaluation pipeline")

        evalution_result = await evaluate_rag_pipeline(
            golden_dataset = golden_dataset,
            rag_pipeline = LLMService("openai")
        )

        print(evalution_result)
        return evalution_result
