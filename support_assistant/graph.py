import os
from typing import TypedDict
from pydantic import BaseModel, Field, ValidationError
from sentence_transformers import SentenceTransformer
import chromadb
from langgraph.graph import StateGraph, START, END
MOCK_LLM = os.getenv("MOCK_LLM", "1")

CHROMA_PATH = "support_assistant/chroma_db"
COLLECTION_NAME = "zepto_policies"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_collection(
    name=COLLECTION_NAME
)
class AssistantResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
class GraphState(TypedDict, total=False):
    query: str
    intent: str
    answer: str
    sources: list[str]
    confidence: float

def validate_response(generate_response):
    corrective_instruction = (
        "Return a valid response with answer, sources, and confidence."
    )

    last_error = None

    for attempt in range(3):
        try:
            raw_response = generate_response(
                "" if attempt == 0 else corrective_instruction
            )

            return AssistantResponse.model_validate(raw_response)

        except ValidationError as error:
            last_error = error

    raise ValueError(
        f"Response validation failed after 3 attempts: {last_error}"
    )

PROMPT_TEMPLATE = """
ROLE:
You are a Zepto customer-support assistant.

CONTEXT:
Answer only using the policy context provided below.

TASK:
Answer the customer's question clearly and briefly.

FORMAT:
Return a helpful answer followed by the relevant source document IDs.

LENGTH:
Keep the answer concise and easy to understand.

NEGATIVE CONSTRAINT:
Do not answer using information that is not present in the provided context.
Do not invent or assume Zepto policies.

FEW-SHOT EXAMPLE:

Question:
How long does delivery take?

Context:
Standard delivery typically takes 15–30 minutes.

Answer:
Standard delivery typically takes 15–30 minutes.
Source: doc_01

CUSTOMER QUESTION:
{query}

POLICY CONTEXT:
{context}
"""
def validate_response(raw_response: str):
    last_error = None

    for attempt in range(3):
        try:
            return AssistantResponse.model_validate(raw_response)
        except Exception as error:
            last_error = error

            if attempt < 2:
                corrective_instruction = (
                    "Return only valid JSON with the fields "
                    "answer, sources, and confidence."
                )
            else:
                raise last_error

def classify_intent(state: GraphState):
    query = state["query"].lower()
    policy_keywords = [
    "delivery",
    "deliver",
    "return",
    "refund",
    "membership",
    "tracking",
    "cancel",
    "gift card",
    "support hours"
]

    is_policy_question = any(
        keyword in query
        for keyword in policy_keywords
    )

    if is_policy_question:
        intent = "policy_question"
    else:
        intent = "general_question"

    print("\n[Node: classify_intent]")
    print("Query:", state["query"])
    print("Intent:", intent)

    return {
        "intent": intent
    }

def retrieve_and_answer(state: GraphState):
    query = state["query"]

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documents = results["documents"][0]
    ids = results["ids"][0]
    top_document = documents[0]
    top_id = ids[0]
    snippet = top_document[:200].strip()

    if MOCK_LLM == "1":
        answer = (
            f"Based on the retrieved context: {snippet}"
        )

        confidence = 1.0

    else:
        prompt = PROMPT_TEMPLATE.format(
            query=query,
            context="\n\n".join(
                f"{doc_id}: {doc}"
                for doc_id, doc in zip(ids, documents)
            )
        )
        answer = (
            "Real LLM mode is optional. "
            "The retrieved context was prepared successfully."
        )

        confidence = 0.8

    print("\n[Node: retrieve_and_answer]")
    print("Retrieved sources:", ids)

    return {
        "answer": answer,
        "sources": ids,
        "confidence": confidence
    }
def direct_answer(state: GraphState):

    if MOCK_LLM == "1":
        answer = (
            "I can only answer questions about Zepto policies right now."
        )

        confidence = 1.0

    else:       
        answer = (
            "I can only answer questions about Zepto policies right now."
        )

        confidence = 0.8

    print("\n[Node: direct_answer]")

    return {
        "answer": answer,
        "sources": [],
        "confidence": confidence
    }
def route_after_classification(state: GraphState):

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"

graph_builder = StateGraph(GraphState)

graph_builder.add_node(
    "classify_intent",
    classify_intent
)

graph_builder.add_node(
    "retrieve_and_answer",
    retrieve_and_answer
)

graph_builder.add_node(
    "direct_answer",
    direct_answer
)

graph_builder.add_edge(
    START,
    "classify_intent"
)

graph_builder.add_conditional_edges(
    "classify_intent",
    route_after_classification,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)

graph_builder.add_edge(
    "retrieve_and_answer",
    END
)

graph_builder.add_edge(
    "direct_answer",
    END
)

graph = graph_builder.compile()
def ask(query: str):

    result = graph.invoke(
        {
            "query": query
        }
    )

    raw_response = {
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "confidence": result.get("confidence", 0.0)
    }

    response = validate_response(raw_response)

    return response
if __name__ == "__main__":

    print("=" * 60)
    print("TEST 1 — POLICY QUESTION")
    print("=" * 60)

    response1 = ask(
        "How long does Zepto take to deliver an order?"
    )

    print(response1.model_dump_json(indent=2))


    print("\n" + "=" * 60)
    print("TEST 2 — GENERAL QUESTION")
    print("=" * 60)

    response2 = ask(
        "What is the capital of India?"
    )

    print(response2.model_dump_json(indent=2))