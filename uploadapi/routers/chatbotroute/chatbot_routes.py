from fastapi import APIRouter , Request
from Services.llm_services import LLMService
from Schemas.schemas import LLMResponse

import os 
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")

router = APIRouter(tags=["chatbot"])


@router.post("/chatbot",response_model=LLMResponse)
async def askchatbot(request : Request , query:str):
    print("*"*20 + "askchatbot" + "*"*20)

    llm_services = request.app.state.llm_service

    result = await llm_services.query(query)

    return LLMResponse(
        query=query,
        answer=result["answer"],
        chunks=result["reranked_chunk"],
        scores=result["rerank_score"]
    )