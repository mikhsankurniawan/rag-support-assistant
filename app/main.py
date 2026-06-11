from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session, init_db
from app.models import Chunk, Conversation, Document, Message
from app.schemas import (
    AskRequest,
    AskResponse,
    ConversationCreateRequest,
    ConversationResponse,
    DocumentResponse,
    MessageResponse,
)
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


@app.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreateRequest,
    session: Session = Depends(get_session),
) -> ConversationResponse:
    conversation = Conversation(title=request.title)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
    )


@app.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(session: Session = Depends(get_session)) -> list[ConversationResponse]:
    conversations = session.scalars(
        select(Conversation).order_by(Conversation.created_at.desc())
    ).all()

    return [
        ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
        )
        for conversation in conversations
    ]


@app.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def list_conversation_messages(
    conversation_id: int,
    session: Session = Depends(get_session),
) -> list[MessageResponse]:
    conversation = session.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    messages = session.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    return [
        MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        for message in messages
    ]


@app.post("/conversations/{conversation_id}/ask", response_model=AskResponse)
def ask_in_conversation(
    conversation_id: int,
    request: AskRequest,
    session: Session = Depends(get_session),
) -> AskResponse:
    conversation = session.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    try:
        answer, sources = ask_question(
            session=session,
            question=request.question,
            top_k=request.top_k,
        )

        session.add(
            Message(
                conversation_id=conversation_id,
                role="user",
                content=request.question,
            )
        )
        session.add(
            Message(
                conversation_id=conversation_id,
                role="assistant",
                content=answer,
            )
        )
        session.commit()

    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {exc}") from exc

    return AskResponse(
        answer=answer,
        sources=sources,
        metadata={
            "top_k": request.top_k,
            "conversation_id": conversation_id,
        },
    )
    

@app.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    session: Session = Depends(get_session),
) -> Response:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    session.delete(document)
    session.commit()

    return Response(status_code=204)
