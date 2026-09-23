# Zepto Support Assistant

## Overview

The Zepto Support Assistant is a retrieval-based customer support service that answers questions using a fixed set of Zepto policy documents.

The system uses local document embeddings, ChromaDB for vector retrieval, LangGraph for query routing, Pydantic for structured responses, and FastAPI for exposing the assistant as an API.

The graded baseline runs in deterministic mock mode and does not require an LLM API key.

## Architecture

The overall flow is:

```text
Policy Documents
      |
      v
ingest.py
      |
      v
all-MiniLM-L6-v2
      |
      v
ChromaDB: zepto_policies
      |
      |
User Query
      |
      v
classify_intent
      |
      +-----------------------+
      |                       |
      v                       v
policy_question         general_question
      |                       |
      v                       v
retrieve_and_answer     direct_answer
      |
      v
Top-3 Retrieved Documents
      |
      v
Structured Response
      |
      v
Pydantic Validation
      |
      v
FastAPI /ask

## API Testing

The FastAPI service exposes a POST `/ask` endpoint.

### Policy question

Request:

```json
{
  "query": "How long does Zepto take to deliver an order?"
}
```

Response:

```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
  "sources": [
    "doc_01",
    "doc_04",
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

## Running the API

Start the FastAPI service with:

```bash
uvicorn support_assistant.app:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The default graded mode is deterministic mock mode. It does not require an LLM API key or external LLM service.

Set `MOCK_LLM=0` only when using the optional real-LLM path.

## Docker

A Dockerfile is included for running the FastAPI service locally. The container exposes port `7860` and starts the application using Uvicorn.

Docker execution was not performed in the current development environment because Docker Desktop requires WSL on this system. The Dockerfile is included for reproducible local container execution on a system with Docker configured.