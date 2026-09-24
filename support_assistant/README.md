# Zepto Support Assistant

## Overview

The Zepto Support Assistant is a retrieval-based customer support service that answers questions using a fixed corpus of Zepto policy documents.

The system uses local document embeddings with `all-MiniLM-L6-v2`, ChromaDB for vector retrieval, LangGraph for query routing, Pydantic for structured responses, and FastAPI for the API layer.

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

## Architecture

The overall RAG pipeline is:

```text
Policy Documents
      |
      v
Ingestion and Chunking
      |
      v
all-MiniLM-L6-v2 Embeddings
      |
      v
ChromaDB: zepto_policies
      |
      v
User Query
      |
      v
classify_intent
      |
      +-------------------------+
      |                         |
      v                         v
policy_question          general_question
      |                         |
      v                         v
retrieve_and_answer       direct_answer
      |
      v
Top-3 Retrieved Chunks
      |
      v
Answer Generation
      |
      v
Pydantic Validation
      |
      v
FastAPI /ask

### Ingestion

`ingest.py` loads all 8 policy documents from the `docs/` directory, generates local embeddings using `all-MiniLM-L6-v2`, and stores them in the ChromaDB collection `zepto_policies`.

### Retrieval

For policy questions, the system queries ChromaDB using cosine similarity and retrieves the top 3 relevant documents.

### Intent Routing

`classify_intent` routes policy-related questions to `retrieve_and_answer` and other questions to `direct_answer`.

### Generation

In mock mode, the answer is generated deterministically from the retrieved context. The response is then validated using the Pydantic `AssistantResponse` schema.

### MOCK_LLM

The graded baseline uses deterministic mock mode and does not call an external LLM service. An optional real-LLM path is included separately.

## Structured Prompt

The application uses a structured prompt following the role-context-task-format-length skeleton.

The prompt includes:

- Role definition
- Retrieved context
- Task instructions
- Required response format
- Length constraint
- An explicit negative constraint instructing the model not to use information outside the provided context
- A few-shot example

This prompt is used by the optional real-LLM path. The graded mock path does not make an external LLM call.
## API Testing

The FastAPI service exposes a POST `/ask` endpoint.

### Policy question

Request:

```json
{
  "query": "What are Zepto customer support hours?"
}
```

Response:

```json
{
  "answer": "Based on the retrieved context: Zepto customer support is available via in-app chat 24 hours a day, 7 days a week, given the time-sensitive nature of quick commerce deliveries. Average in-app chat response time is under 2 minutes.",
  "sources": [
    "doc_08",
    "doc_03",
    "doc_06"
  ],
  "confidence": 1.0
}
```

### General question

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

## Ingestion

Run the ingestion pipeline with:

```bash
python support_assistant/ingest.py
```

## Running the API

Start the FastAPI service with:

```bash
uvicorn support_assistant.app:app --port 7860
```

The API is available at:

`http://127.0.0.1:7860`

Interactive API documentation:

`http://127.0.0.1:7860/docs`

## Docker

A Dockerfile is included for running the FastAPI service in a container. The container exposes port `7860`.

Build the Docker image from the project root:

```bash
docker build -f support_assistant/Dockerfile -t zepto-support-assistant .
```

Run the container:

```bash
docker run -p 7860:7860 zepto-support-assistant
```

The API is then available at:

`http://127.0.0.1:7860`

Interactive API documentation:

`http://127.0.0.1:7860/docs`

Docker execution was not performed locally because Docker Desktop requires the Linux/WSL environment on this machine.