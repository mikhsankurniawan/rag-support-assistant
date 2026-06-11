from sqlalchemy.orm import Session

from app.models import Chunk, Document
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts


def ingest_document(
    session: Session,
    filename: str,
    content_type: str,
    raw_text: str,
) -> Document:
    chunks = chunk_text(raw_text)
    if not chunks:
        raise ValueError("No readable text found in document.")

    embeddings = embed_texts(chunks)

    document = Document(filename=filename, content_type=content_type)
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
