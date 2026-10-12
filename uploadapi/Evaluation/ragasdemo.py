from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Your RAG pipeline results — one row per evaluated query
eval_data = {
    "question": [
        "What is the cancellation policy for annual subscriptions?",
        "How do I reset my API key?",
        "What are the rate limits for the free tier?",
    ],
    "contexts": [
        [
            "Annual subscriptions can be cancelled at any time. Cancellation takes effect at the end of the current billing period. No refunds are issued for the remaining period.",
            "To cancel, navigate to Account Settings > Billing > Cancel Subscription.",
        ],
        [
            "To reset your API key, go to the Developer Settings panel. Click 'Regenerate Key'. Your old key is immediately invalidated.",
        ],
        [
            "Free tier accounts are limited to 100 API calls per day and 10 calls per minute. Limits reset at midnight UTC.",
        ],
    ],
    "answer": [
        "Annual subscriptions can be cancelled at any time through Account Settings. The cancellation takes effect at the end of your billing period with no refund for remaining time.",
        "You can reset your API key in Developer Settings by clicking 'Regenerate Key'. Note that this immediately invalidates your current key.",
        "The free tier allows 100 API calls per day and 10 per minute, resetting at midnight UTC.",
    ],
    "ground_truth": [
        "Annual subscriptions can be cancelled at any time. Cancellation takes effect at end of billing period. No refunds issued.",
        "Reset API key via Developer Settings > Regenerate Key. Old key is immediately invalidated.",
        "Free tier: 100 calls/day, 10 calls/minute. Resets at midnight UTC.",
    ],
}

dataset = Dataset.from_dict(eval_data)

# Configure the LLM used for evaluation (separate from your production LLM)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Run evaluation
results = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=llm,
    embeddings=embeddings,
)

print(results)
# {'faithfulness': 0.97, 'answer_relevancy': 0.94, 'context_precision': 0.89, 'context_recall': 0.91}