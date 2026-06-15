# RAG Support Assistant

![Tests](https://github.com/mikhsankurniawan/rag-support-assistant/actions/workflows/tests.yml/badge.svg)

A full-stack internal knowledge assistant that lets users upload support documents, ask questions, and receive grounded AI-generated answers with source citations.

This project demonstrates a production-oriented Retrieval-Augmented Generation pipeline using **FastAPI**, **PostgreSQL**, **pgvector**, **Sentence Transformers**, **Ollama**, and **Streamlit**.

The goal of this project is not only to build a chatbot, but to show how a normal backend system can be extended with AI capabilities such as document ingestion, semantic search, grounded answer generation, source citation, duplicate protection, and conversation history.

---

## Features

* Upload `.txt` and `.pdf` documents
* Extract readable text from uploaded files
* Split documents into searchable chunks
* Generate embeddings using Sentence Transformers
* Store documents, chunks, and embeddings in PostgreSQL with pgvector
* Ask questions against indexed documents
* Retrieve the most relevant document chunks using vector similarity search
* Generate grounded answers using Ollama
* Return source citations for retrieved chunks
* Prevent duplicate document ingestion using content hashing
* List indexed documents
* Delete documents and their related chunks
* Create conversations
* Store user and assistant message history
* Use FastAPI Swagger docs for API testing
* Use Streamlit as a simple frontend demo
* Includes automated tests for core backend behavior
* Runs with Docker Compose for local development

---

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* pgvector
* Pydantic
* Uvicorn

### AI / RAG

* Sentence Transformers
* Ollama
* Local LLM inference
* Vector embeddings
* Semantic search
* Retrieval-Augmented Generation

### Frontend

* Streamlit
* HTTPX

### Infrastructure

* Docker Compose
* PostgreSQL container with pgvector extension
* GitHub Actions CI

---

## Architecture

```text
User uploads document
        ↓
FastAPI receives file
        ↓
Text extraction
        ↓
Text chunking
        ↓
Embedding model converts chunks into vectors
        ↓
PostgreSQL + pgvector stores chunks and vectors
        ↓
User asks question
        ↓
Question is embedded
        ↓
Vector search retrieves relevant chunks
        ↓
Retrieved context + question are sent to Ollama
        ↓
LLM generates grounded answer with sources
        ↓
Conversation history is saved
```

---

## Project Structure

```text
rag-support-mvp/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   └── services/
│       ├── chunker.py
│       ├── embeddings.py
│       ├── extraction.py
│       ├── ingestion.py
│       ├── llm.py
│       └── rag.py
│
├── docs/
│   └── screenshots/
│
├── sample_docs/
│   └── company_policy.txt
│
├── scripts/
│   └── smoke_test.py
│
├── tests/
│   ├── test_chunker.py
│   ├── test_hashing.py
│   └── test_health.py
│
├── streamlit_app.py
├── Dockerfile.api
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

---

## Running Locally

### Prerequisites

Make sure these are installed:

* Python 3.12
* Docker Desktop
* Ollama
* Git

This project was tested locally on Windows using Python 3.12.

---

## 1. Start PostgreSQL with pgvector

```bash
docker compose up -d db
```

Check that the database is running:

```bash
docker compose ps
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If PyTorch has DLL issues on Windows, reinstall the CPU-only version:

```bash
pip uninstall -y torch torchvision torchaudio
pip cache purge
pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

---

## 4. Create Environment File

```bash
copy .env.example .env
```

Example `.env` configuration:

```env
DATABASE_URL=postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_support
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b
OPENAI_API_KEY=
```

Do not commit `.env` to Git.

---

## 5. Prepare Ollama Model

Pull the local LLM model:

```bash
ollama pull llama3.1:8b
```

Check available models:

```bash
ollama list
```

Test Ollama:

```bash
ollama run llama3.1:8b "say ok"
```

---

## 6. Run the Backend

```bash
uvicorn app.main:app --reload
```

Backend API:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## 7. Run the Frontend

Open a second terminal, activate the virtual environment, then run:

```bash
streamlit run streamlit_app.py
```

Frontend URL:

```text
http://localhost:8501
```

---

## Running with Docker Compose

The project can also run with Docker Compose. This starts the PostgreSQL database, FastAPI backend, and Streamlit frontend.

Ollama should still run locally outside Docker.

Make sure the Ollama model is available:

```bash
ollama pull llama3.1:8b
```

Test Ollama locally:

```bash
ollama run llama3.1:8b "say ok"
```

Then start the Dockerized services:

```bash
docker compose up --build
```

Backend health check:

```text
http://localhost:8000/health
```

FastAPI Swagger docs:

```text
http://localhost:8000/docs
```

Streamlit frontend:

```text
http://localhost:8501
```

The Dockerized backend connects to the local Ollama server through:

```text
http://host.docker.internal:11434
```

---

## Smoke Test

Run this after the backend is running:

```bash
python scripts\smoke_test.py
```

The smoke test checks:

* Health endpoint
* Document upload
* Question answering
* Source retrieval

Example successful output:

```text
Health: {'status': 'ok'}
Upload: 200 {...}
Ask: 200 {...}
```

---

## Running Tests

Run the automated test suite:

```bash
pytest
```

The current test suite covers:

* Text chunking behavior
* Content hashing for duplicate document protection
* Health check API behavior

---

## API Overview

### Health Check

```http
GET /health
```

Checks whether the backend is running.

---

### Upload Document

```http
POST /documents
```

Uploads a `.txt` or `.pdf` document, extracts text, chunks it, generates embeddings, and stores it in PostgreSQL.

---

### List Documents

```http
GET /documents
```

Returns all indexed documents.

---

### Delete Document

```http
DELETE /documents/{document_id}
```

Deletes a document and its related chunks.

---

### Ask Question

```http
POST /ask
```

Asks a question against all indexed documents.

Example request:

```json
{
  "question": "When should support escalate a ticket to engineering?",
  "top_k": 3
}
```

Example response:

```json
{
  "answer": "Support agents should escalate tickets to engineering if the issue involves repeated payment failure, missing transaction records, data inconsistency, security risk, or service downtime.",
  "sources": [
    {
      "document_id": 1,
      "filename": "company_policy.txt",
      "chunk_id": 1,
      "chunk_index": 0,
      "similarity": 0.3162,
      "content_preview": "..."
    }
  ],
  "metadata": {
    "top_k": 3
  }
}
```

---

### Create Conversation

```http
POST /conversations
```

Creates a new conversation.

Example request:

```json
{
  "title": "Support policy test"
}
```

---

### List Conversations

```http
GET /conversations
```

Returns all conversations.

---

### Ask Inside Conversation

```http
POST /conversations/{conversation_id}/ask
```

Asks a question inside a conversation and saves both the user question and assistant answer.

Example request:

```json
{
  "question": "When should support escalate a ticket to engineering?",
  "top_k": 3
}
```

---

### Get Conversation Messages

```http
GET /conversations/{conversation_id}/messages
```

Returns saved user and assistant messages for a conversation.

Example response:

```json
[
  {
    "id": 1,
    "conversation_id": 1,
    "role": "user",
    "content": "When should support escalate a ticket to engineering?",
    "created_at": "2026-06-11T06:35:27.005579Z"
  },
  {
    "id": 2,
    "conversation_id": 1,
    "role": "assistant",
    "content": "Support agents should escalate tickets to engineering if...",
    "created_at": "2026-06-11T06:35:29.112345Z"
  }
]
```

---

## Frontend Usage

The Streamlit frontend supports:

1. Checking backend health
2. Uploading documents
3. Viewing indexed documents
4. Deleting documents
5. Creating conversations
6. Selecting conversations
7. Asking questions
8. Viewing generated answers
9. Expanding retrieved source citations
10. Reading conversation history

---

## Example Document

The sample document contains support policy information such as refund rules, escalation rules, account access rules, and service-level expectations.

Example question:

```text
When should support escalate a ticket to engineering?
```

Example answer:

```text
Support agents should escalate tickets to engineering if the issue involves repeated payment failure, missing transaction records, data inconsistency, security risk, or service downtime.
```

---

## Duplicate Document Protection

This project prevents duplicate ingestion by hashing normalized document text.

If the same document is uploaded multiple times, the system returns the existing document instead of creating duplicate chunks and embeddings.

This avoids:

* Duplicate search results
* Unnecessary embedding generation
* Wasted database storage
* Repeated source citations from identical documents

---

## Current Status

The project currently supports the core document lifecycle:

```text
Upload document
Prevent duplicate upload
List documents
Delete document
Ask questions from indexed documents
Save conversation history
Use the system through a Streamlit UI
Run the backend and frontend with Docker Compose
Run automated tests locally and in GitHub Actions
```

This version focuses on the core RAG workflow and local development experience.

---

## Screenshots

### Streamlit Frontend

![Streamlit Frontend](docs/screenshots/streamlit-home.png)

### Answer With Sources

![Answer With Sources](docs/screenshots/answer-sources.png)

### FastAPI Swagger Docs

![Swagger Docs](docs/screenshots/swagger-docs.png)

---

## Future Improvements

Potential next features:

* Workspace separation
* User authentication
* Role-based access control
* Per-workspace document search
* Better PDF parsing
* File metadata extraction
* RAG evaluation scripts
* Hybrid search with keyword and vector search
* Reranking retrieved chunks
* Streaming LLM responses
* Cloud deployment
* Monitoring and observability
* More comprehensive API tests