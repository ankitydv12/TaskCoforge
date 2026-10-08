from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()
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


llm = HuggingFaceEndpoint(
    repo_id='meta-llama/Llama-3.1-8B-Instruct',
    task='text-generation',
    max_new_tokens=350
)

# model = ChatHuggingFace(llm=llm)
model = ChatOpenAI()

def query(context,query):
    parser = StrOutputParser()
    _answer_chain = _answer_prompt | model | parser
    ans = _answer_chain.invoke({"context":context,"query":query})
    print(ans)
    print("Answer from LLM type--> ",type(ans))
    return ans




