from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_huggingface import (
    HuggingFaceEndpoint , 
    ChatHuggingFace , 
    HuggingFaceEmbeddings
    )
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from Services.retrival_service import retrival
from Services.reranking_service import reranking_service
from dotenv import load_dotenv
import os

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")

class LLMService:

    NOT_FOUND_RESPONSE = (
    "I couldn't find this in the available policy documents. "
    "Please check with HR for confirmation."
    )
    _answer_prompt = ChatPromptTemplate.from_messages([
        ("system",
        "You are an HR policy assistant for Coforge employees. Answer using "
        "ONLY the policy content below. Do not guess, estimate, or use outside "
        "knowledge — every number or fact in your answer must come directly "
        "from the context. Give a concise, direct answer when a source passage "
        "contains the answer, including any stated number, duration, "
        "eligibility, or condition. Do not use the fallback response merely "
        "because the question does not name a policy ; the retrieved context "
        "may come from multiple policies, if only policy name is in query five the summary from context \n\n"
        "Use the fallback response only if none of the source passages "
        "provides an answer to the question. The fallback response must be "
        f'exactly: "{NOT_FOUND_RESPONSE}"\n\n'
        "Context:\n{context}"),
        ("human", "{query}"),
    ])

    def __init__(self, provider: str):
        self.llm = LLMFactory.create(provider)

    def query(self,query):
        parser = StrOutputParser()
        _answer_chain = LLMService._answer_prompt | self.llm | parser

        print(f"Retriving the chunk before reranking")
        retrive_chunk = retrival.chroma_query(query,str(COLLECTION_NAME))

        documents =  [y for x in retrive_chunk["documents"] for y in x]
        reranked_chunk , rerank_score = reranking_service.cross_encoder_reranking(query,documents)
        
        ans = _answer_chain.invoke({"context":reranked_chunk[:5],"query":query})
        print("Answer from LLM --> ",ans)
        return {
            "answer": ans,
            "reranked_chunk": reranked_chunk[:5],
            "rerank_score" : rerank_score[:5]
        }
        
    

class LLMFactory:
    @staticmethod
    def create(provider:str=None):
        if provider == None or provider == 'huggingface':
            print("Default provider huggingface")
            llm = HuggingFaceEndpoint(
                repo_id='meta-llama/Llama-3.1-8B-Instruct',
                task='text-generation',
                max_new_tokens=350
                )
            
            return ChatHuggingFace(llm=llm)
        
        elif provider == "openai":
            return ChatOpenAI(model = "gpt-5.4-mini")

        elif provider == "openaiembeddings":
            return OpenAIEmbeddings()

        elif provider == "huggingfaceembeddings":
            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        raise ValueError("Unsupported provider")

