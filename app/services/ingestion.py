import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, Document
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts


def _hash_text(raw_text: str) -> str:
    normalized_text = "\n".join(
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    )
    return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()


def ingest_document(
    session: Session,
    filename: str,
    content_type: str,
    raw_text: str,
) -> Document:
    chunks = chunk_text(raw_text)
    if not chunks:
        raise ValueError("No readable text found in document.")

    content_hash = _hash_text(raw_text)

    existing_document = session.scalar(
        select(Document).where(Document.content_hash == content_hash)
    )
    if existing_document is not None:
        return existing_document

    embeddings = embed_texts(chunks)

    document = Document(
        filename=filename,
        content_type=content_type,
        content_hash=content_hash,
    )
    session.add(document)
    session.flush()

    for index, (content, embedding) in enumerate(zip(chunks, embeddings)):
        session.add(
            Chunk(
                document_id=document.id,
                chunk_index=index,
                content=content,
                embedding=embedding,
            )
        )

    session.commit()
    session.refresh(document)
    return document