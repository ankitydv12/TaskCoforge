import asyncio
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness,
)

from datasets import Dataset
from langchain_openai import ChatOpenAI , OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

async def evaluate_rag_pipeline(
    golden_dataset : list[dict],
    rag_pipeline,
    llm,
    embeddings
)->dict:
    questions = []
    ground_truths = []
    all_contexts = []
    all_answers = []

    for record in golden_dataset:

        results = await rag_pipeline.query(record["question"])

        questions.append(record["question"])
        ground_truths.append(record["ground_truths"])

        all_contexts.append(results.retrieve_chunk) #TODO : check it
        all_answers.append(results.answer)

    dataset = Dataset.from_dict(
    {       "question" : questions,
            "contexts" : all_contexts,
            "answer" : all_answers,
            "ground_truth" : ground_truths
    }
    )

    scores = evaluate(
            dataset = dataset,
            metrics = [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
                answer_correctness,
            ],
            llm = llm,
            embeddings = embeddings
        )

    return scores.to_pandas().mean().to_dict()    


