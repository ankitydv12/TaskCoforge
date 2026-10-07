from fastapi import APIRouter
from chatbot import chatbot
from Services.retrival_service import retrival
from Services.reranking_service import reranking_service

router = APIRouter(tags=["chatbot"])


@router.post("/chatbot")
def askchatbot(query:str,top:int):
    print("*"*20 + "askchatbot" + "*"*20)
    #TODO: get collection from the .env file
    retrive_chunk = retrival.chroma_query(query,"collection1",top)

    documents =  [y for x in retrive_chunk["documents"] for y in x]

    
    reranked_chunk , rerank_score = reranking_service.cross_encoder_reranking(query,documents)

    ans = chatbot.query(reranked_chunk[:5],query)
    return ans