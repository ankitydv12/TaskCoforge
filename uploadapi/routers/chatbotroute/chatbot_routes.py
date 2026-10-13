from fastapi import APIRouter
from Services.llm_services import LLMService
from Schemas.schemas import LLMResponse

import os 
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv(COLLECTION_NAME)

router = APIRouter(tags=["chatbot"])


@router.post("/chatbot",response_model=LLMResponse)
def askchatbot(query:str):
    print("*"*20 + "askchatbot" + "*"*20)

    llm_services = LLMService("openai")

    ans , reranked_chunk , rerank_score = llm_services.query(query)

    return LLMResponse(
        query=query,
        answer=ans,
        chunks=reranked_chunk[:5],
        scores=rerank_score[:5]
    )