from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session, init_db
from app.models import Chunk, Document
from app.schemas import AskRequest, AskResponse, DocumentResponse
from app.services.extraction import extract_text_from_upload
from app.services.ingestion import ingest_document
from app.services.rag import ask_question


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> DocumentResponse:
    try:
        raw_text = await extract_text_from_upload(file)
        document = ingest_document(
            session=session,
            filename=file.filename or "uploaded_file",
            content_type=file.content_type or "application/octet-stream",
            raw_text=raw_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {exc}") from exc

    chunk_count = session.scalar(select(func.count()).select_from(Chunk).where(Chunk.document_id == document.id)) or 0
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        created_at=document.created_at,
        chunk_count=chunk_count,
    )


@app.get("/documents", response_model=list[DocumentResponse])
def list_documents(session: Session = Depends(get_session)) -> list[DocumentResponse]:
    statement = (
        select(Document, func.count(Chunk.id).label("chunk_count"))
        .outerjoin(Chunk, Chunk.document_id == Document.id)
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
    )
    rows = session.execute(statement).all()
    return [
        DocumentResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            created_at=document.created_at,
            chunk_count=chunk_count,
        )
        for document, chunk_count in rows
    ]


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, session: Session = Depends(get_session)) -> AskResponse:
    try:
        answer, sources = ask_question(
            session=session,
            question=request.question,
            top_k=request.top_k,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {exc}") from exc

    return AskResponse(
        answer=answer,
        sources=sources,
        metadata={"top_k": request.top_k},
    )
