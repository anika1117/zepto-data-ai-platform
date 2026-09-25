# Zepto Support Assistant

## Overview

The Zepto Support Assistant is a retrieval-based customer support application that answers questions using a fixed corpus of 8 Zepto policy documents.

The system uses `all-MiniLM-L6-v2` for embeddings, ChromaDB for vector retrieval, LangGraph for query routing, Pydantic for structured responses, and FastAPI for the API layer.

The graded baseline runs in deterministic mock mode and does not require an LLM API key or external LLM service.

## Project Structure

```text
support_assistant/
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
├── chroma_db/
├── app.py
├── graph.py
├── ingest.py
├── Dockerfile
└── README.md
```

## RAG Architecture

The application follows the required Retrieval-Augmented Generation pipeline:

```text
8 Zepto Policy Documents
          |
          v
Document Ingestion
    ingest.py
          |
          v
Embedding Generation
all-MiniLM-L6-v2
          |
          v
ChromaDB
zepto_policies
          |
          v
User Query
          |
          v
classify_intent
          |
     +----+----+
     |         |
     v         v
policy_question  general_question
     |         |
     v         v
retrieve_and_answer  direct_answer
     |
     v
Top-3 Retrieved Documents
     |
     v
Answer Generation
     |
     v
Pydantic Validation
     |
     v
FastAPI /ask
```

### Pipeline Components

| Stage | File / Component |
|---|---|
| Document ingestion | `ingest.py` |
| Embedding generation | `all-MiniLM-L6-v2` |
| Vector storage and retrieval | ChromaDB |
| Vector collection | `zepto_policies` |
| Intent classification | `classify_intent` node in `graph.py` |
| Policy retrieval and answer | `retrieve_and_answer` node in `graph.py` |
| General question answer | `direct_answer` node in `graph.py` |
| Response validation | Pydantic response model |
| API | `app.py` |
| Containerization | `Dockerfile` |

## Data Flow
1. `ingest.py` loads all 8 policy documents from the `docs/` directory.
2. The documents are embedded using `all-MiniLM-L6-v2`.
3. The embeddings and document text are stored in the ChromaDB collection `zepto_policies`.
4. A user sends a query to the FastAPI `/ask` endpoint.
5. The query enters the LangGraph workflow.
6. `classify_intent` determines whether the query is a `policy_question` or `general_question`.
7. Policy questions are routed to `retrieve_and_answer`.
8. `retrieve_and_answer` performs embedding-based retrieval and gets the top 3 relevant documents from ChromaDB using cosine similarity.
9. The retrieved context is used to generate the policy answer.
10. General questions are routed to `direct_answer`.
11. The final response is validated using the Pydantic response schema.
12. FastAPI returns the validated JSON response.

## Ingestion

All 8 policy documents are loaded and embedded into ChromaDB.

The collection name is:

```text
zepto_policies
```

The verified ingestion output was:

```text
Documents loaded: 8
Generating embeddings...

ChromaDB ingestion complete.
Collection: zepto_policies
Total documents: 8
```

A retrieval test using:

```text
How long does Zepto take to deliver an order?
```

returned:

```text
Retrieved documents:
1. doc_01
2. doc_04
3. doc_06
```

Run the ingestion pipeline with:

```bash
python support_assistant/ingest.py
```

## Intent Routing

The LangGraph workflow uses three nodes:

```text
classify_intent
retrieve_and_answer
direct_answer
```

The `classify_intent` node uses the required deterministic keyword-based approach in mock mode.

The policy keywords are:

```text
delivery
return
refund
membership
tracking
cancel
gift card
support hours
```

If a query contains one of these keywords, it is classified as:

```text
policy_question
```

Otherwise it is classified as:

```text
general_question
```

The conditional routing is:

```text
classify_intent
      |
      +---- policy_question ----> retrieve_and_answer
      |
      +---- general_question --> direct_answer
```

No LLM call is required for mock intent classification.

## Retrieval and Generation

For a policy question, `retrieve_and_answer` performs real vector retrieval from ChromaDB.

The query is embedded using `all-MiniLM-L6-v2`, and the top 3 relevant policy documents are retrieved using cosine similarity.

In mock mode, the answer follows the required format:

```text
Based on the retrieved context: <top retrieved context snippet>
```

The snippet is taken from the retrieved context and is approximately 200 characters.

For a general question, `direct_answer` returns the fixed mock response:

```text
I can only answer questions about Zepto policies right now.
```

## Structured Prompt

The optional real-LLM path uses a structured prompt containing the required ROLE, CONTEXT, TASK, FORMAT, and LENGTH sections.

The prompt also contains a negative constraint and a few-shot example.

The structure is:

```text
ROLE:
You are a Zepto customer support assistant.

CONTEXT:
Use the retrieved Zepto policy documents provided as context.

TASK:
Answer the user's question using the provided policy context.

FORMAT:
Return the response in the required structured format.

LENGTH:
Keep the response concise and relevant.

NEGATIVE CONSTRAINT:
Do not use information outside the provided context and do not invent policy details.

FEW-SHOT EXAMPLE:
User: How long is Zepto delivery?
Assistant: Answer the question using only the retrieved Zepto policy context.
```

The graded mock path does not make an external LLM call.

## MOCK_LLM

The default mode is deterministic mock mode.

In mock mode:

- No external LLM API key is required.
- `classify_intent` uses the required keyword-based classifier.
- Policy questions perform real top-3 ChromaDB retrieval.
- Policy answers use the required retrieved-context format.
- General questions use the required fixed direct-answer response.

When the optional real-LLM path is enabled, the retrieved context is passed to the structured prompt for LLM-based generation.

Therefore, the main difference is:

```text
MOCK_LLM enabled/default
    |
    +--> deterministic classification
    +--> real ChromaDB retrieval
    +--> deterministic answer generation
    +--> no external LLM call

MOCK_LLM disabled
    |
    +--> retrieval still provides policy context
    +--> structured prompt is used
    +--> optional real LLM generates the answer
```

## API

The FastAPI application exposes:

```text
POST /ask
```

Request format:

```json
{
  "query": "How long is Zepto delivery?"
}
```

The response contains:

```json
{
  "answer": "string",
  "sources": [],
  "confidence": 1.0
}
```

The response is validated using the Pydantic response model with:

```text
answer: string
sources: list
confidence: float
```

The confidence value is restricted to the range `0` to `1`.

## API Example 1: Policy Question

Request:

```json
{
  "query": "How long is Zepto delivery?"
}
```

Response:

```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
  "sources": [
    "doc_01",
    "doc_08",
    "doc_04"
  ],
  "confidence": 1.0
}
```

This demonstrates the policy path:

```text
/ask
  |
  v
classify_intent
  |
  v
policy_question
  |
  v
retrieve_and_answer
  |
  v
Top-3 ChromaDB Retrieval
  |
  v
Mock Answer
```

## API Example 2: General Question

Request:

```json
{
  "query": "What is the capital of India?"
}
```

Response:

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

This demonstrates the general path:

```text
/ask
  |
  v
classify_intent
  |
  v
general_question
  |
  v
direct_answer
```

## Running Locally

Run the ingestion pipeline first:

```bash
python support_assistant/ingest.py
```

Start the FastAPI application with:

```bash
uvicorn support_assistant.app:app --reload
```

The application was verified locally with Uvicorn.

The local API runs at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Docker

A Dockerfile is included for building and running the FastAPI application in a container.

Build the Docker image from the project root:

```bash
docker build -f support_assistant/Dockerfile -t zepto-support-assistant .
```

Run the container:

```bash
docker run --rm -p 7860:7860 zepto-support-assistant
```

The container runs the API on port `7860`.

Docker build was successfully verified:

```text
[+] Building 2.4s (11/11) FINISHED
```

Docker startup was successfully verified:

```text
Application startup complete.
Uvicorn running on http://0.0.0.0:7860
```

The `/ask` endpoint was also tested successfully from the running Docker container with both a policy question and a general question.

The Docker API is available at:

```text
http://127.0.0.1:7860
```

Interactive API documentation is available at:

```text
http://127.0.0.1:7860/docs
```