import sys
import types

if "langchain_community.chat_models.vertexai" not in sys.modules:
    _stub = types.ModuleType("langchain_community.chat_models.vertexai")

    class ChatVertexAI:
        pass

    _stub.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = _stub
import asyncio
from statistics import fmean
 
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory
 
from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecisionWithReference,
    ContextRecall,
    AnswerCorrectness,
)
 
from dotenv import load_dotenv
 
load_dotenv()
 
 
# Configure RAGAS evaluator models
client = AsyncOpenAI()
 
evaluation_llm = llm_factory(
    "gpt-4o-mini",
    client=client,
)
 
evaluation_embeddings = embedding_factory(
    "openai",
    model="text-embedding-3-small",
    client=client,
    interface="modern",
)
 
 
# Initialize metrics once, rather than for every question
faithfulness_metric = Faithfulness(llm=evaluation_llm)
 
answer_relevancy_metric = AnswerRelevancy(
    llm=evaluation_llm,
    embeddings=evaluation_embeddings,
)
 
context_precision_metric = ContextPrecisionWithReference(
    llm=evaluation_llm,
)
 
context_recall_metric = ContextRecall(
    llm=evaluation_llm,
)
 
answer_correctness_metric = AnswerCorrectness(
    llm=evaluation_llm,
    embeddings=evaluation_embeddings,
)
 
 
async def evaluate_rag_pipeline(
    golden_dataset: list[dict],
    rag_pipeline,
) -> dict:
 
    metric_scores = {
        "faithfulness": [],
        "answer_relevancy": [],
        "context_precision": [],
        "context_recall": [],
        "answer_correctness": [],
    }
 
    for record in golden_dataset:
        question = record["question"]
        reference = record["ground_truths"]
 
        # Execute your actual RAG application.
        result = await rag_pipeline.query(question)
        
        # Must be a list[str] containing the actual retrieved contexts.
        contexts = result["reranked_chunk"]
        answer = result["answer"]
 
        # Evaluate all metrics for this question.
        results = await asyncio.gather(
            faithfulness_metric.ascore(
                response=answer,
                retrieved_contexts=contexts,
                user_input = question,
            ),
            answer_relevancy_metric.ascore(
                user_input=question,
                response=answer,
            ),
            context_precision_metric.ascore(
                user_input=question,
                retrieved_contexts=contexts,
                reference=reference,
            ),
            context_recall_metric.ascore(
                user_input=question,
                retrieved_contexts=contexts,
                reference=reference,
            ),
            answer_correctness_metric.ascore(
                response=answer,
                reference=reference,
                user_input=question,
            ),
        )
 
        for metric_name, metric_result in zip(
            metric_scores.keys(),
            results,
        ):
            metric_scores[metric_name].append(
                metric_result.value
            )
 
    # Return the average score for each metric.
    return {
        name: fmean(scores)
        for name, scores in metric_scores.items()
        if scores
    }
 