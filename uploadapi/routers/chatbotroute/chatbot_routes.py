from fastapi import APIRouter
from chatbot import chatbot
from Services.retrival_service import retrival

router = APIRouter(tags=["chatbot"])


@router.post("/chatbot")
def askchatbot(query:str,top:int):
    retrive_chunk = retrival.chroma_query(query,"collection1",top)

    ans = chatbot.query(retrive_chunk,query)
    print(ans)