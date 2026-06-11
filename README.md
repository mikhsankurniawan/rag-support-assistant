# RAG Support MVP

A portfolio-ready AI customer support / internal knowledge assistant.

This project lets users upload documents, stores document chunks in PostgreSQL with pgvector, retrieves relevant chunks using vector similarity search, and answers questions with citations.

## What this demonstrates

- Backend API design with FastAPI
- PostgreSQL + pgvector for vector search
- Document ingestion and chunking
- Embedding generation
- Retrieval-Augmented Generation (RAG)
- Docker-based local development
- Clean architecture without LangChain magic

## Architecture

```text
User uploads document
        ↓
Text extraction
        ↓
Chunking
        ↓
Embedding generation
        ↓
Store chunks + vectors in PostgreSQL/pgvector
        ↓
User asks question
        ↓
Question embedding
        ↓
Top-k vector search
        ↓
Prompt LLM with retrieved context
        ↓
Answer + source citations
```

## Tech stack

- Python 3.11
- FastAPI
- PostgreSQL 16
- pgvector
- SQLAlchemy
- Sentence Transformers for local embeddings
- Ollama or OpenAI-compatible response generation

## Quick start

### 1. Start PostgreSQL with pgvector

```bash
docker compose up -d db
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Default mode uses local embeddings with Sentence Transformers and Ollama for answer generation.

To use Ollama:

```bash
ollama pull llama3.1:8b
ollama serve
```

To use OpenAI instead, set:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

### 5. Run API

```bash
uvicorn app.main:app --reload
```

Open API docs:

```text
http://localhost:8000/docs
```

## Example usage

### Upload a file

```bash
curl -X POST "http://localhost:8000/documents" \
  -F "file=@sample_docs/company_policy.txt"
```

### Ask a question

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the refund policy?","top_k":5}'
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/documents` | Upload and ingest document |
| GET | `/documents` | List documents |
| POST | `/ask` | Ask question using RAG |

## Portfolio improvements to add later

1. User authentication
2. Multi-tenant workspaces
3. Document deletion and re-indexing
4. Evaluation dataset and RAG quality metrics
5. Streaming responses
6. Admin dashboard
7. Deployment to AWS ECS or Railway
8. CI/CD with GitHub Actions
9. Observability with Prometheus + Grafana
10. Role-based access control

## Interview explanation

This project uses RAG instead of relying only on the LLM's memory. Documents are split into chunks, each chunk is embedded into a vector, and vectors are stored in PostgreSQL using pgvector. When a user asks a question, the system embeds the question, searches for the most semantically similar chunks, and passes only those chunks into the LLM as context. The final answer includes citations so the user can trace the answer back to source documents.
