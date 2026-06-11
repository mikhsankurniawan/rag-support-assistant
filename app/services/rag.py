from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, Document
from app.schemas import SourceChunk
from app.services.embeddings import embed_query
from app.services.llm import generate_answer


def ask_question(session: Session, question: str, top_k: int) -> tuple[str, list[SourceChunk]]:
    query_embedding = embed_query(question)

    distance = Chunk.embedding.cosine_distance(query_embedding).label("distance")

    statement = (
        select(Chunk, Document, distance)
        .join(Document, Chunk.document_id == Document.id)
        .order_by(distance)
        .limit(top_k)
    )

    results = session.execute(statement).all()

    if not results:
        return "I do not know from the available documents because no documents have been indexed yet.", []

    context_blocks: list[str] = []
    sources: list[SourceChunk] = []

    for chunk, document, dist in results:
        # cosine_distance ranges lower-is-better. Because embeddings are normalized,
        # this rough conversion is useful for display only.
        similarity = max(0.0, min(1.0, 1.0 - float(dist)))
        context_blocks.append(chunk.content)
        sources.append(
            SourceChunk(
                document_id=document.id,
                filename=document.filename,
                chunk_id=chunk.id,
                chunk_index=chunk.chunk_index,
                similarity=similarity,
                content_preview=chunk.content[:280],
            )
        )

    answer = generate_answer(question, context_blocks)
    return answer, sources
