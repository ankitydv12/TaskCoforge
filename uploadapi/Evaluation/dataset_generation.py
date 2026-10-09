import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def parse_json(response: str) -> list[dict]:
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by LLM: {e}")


async def generate_eval_questions(
    chunk: str,
    num_questions: int = 3,
    llm_client = None
) -> list[dict]:
    """Generate evaluation questions from a document chunk."""
    prompt = f"""Given the following text, generate {num_questions} questions whose answers can be found in the text.
For each question, also provide the exact answer from the text.

Text:
{chunk}

Return a JSON array of objects with 'question' and 'answer' keys.
Only generate questions that have clear, unambiguous answers in the text."""

    response = await generate(prompt, response_format="json")
    response_json = parse_json(response)
    
    questions = response_json["questions"]
    print("Return from parsed json questions-->",questions)
    print("Return from parsed json questions type-->",type(questions))



    data =  [
        {
            "question": q["question"],
            "ground_truth": q["answer"],
            "source_chunk": chunk
        }
        for q in questions
    ]
    await json_to_csv(data, csv_file_path="evaluation_dataset.csv")
    return data

async def generate(prompt, response_format="json"):

    print("Prompt------------>",prompt)
    llm =ChatOpenAI(
    model="gpt-4o-mini",
    model_kwargs={
        "response_format": {"type": "json_object"}
    }
    )
    response = await llm.ainvoke(prompt)
    print("Response from LLM type--> ",type(response.content))
    print("Response from LLM content--> ",response.content)
    return response.content


async def json_to_csv(json_data:list[dict], csv_file_path:str = "evaluation_dataset.csv"):
    import pandas as pd
    if not json_data:
        raise ValueError("The provided JSON data is empty.")
    df = pd.DataFrame(json_data)
    df.to_csv(csv_file_path, index=False ,mode='a',header = False)