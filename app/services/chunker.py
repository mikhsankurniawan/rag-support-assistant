from app.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split text into overlapping chunks.

    This simple implementation is intentionally easy to explain in interviews.
    Later, you can replace it with sentence-aware or markdown-aware chunking.
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(cleaned):
        end = start + chunk_size
        chunk = cleaned[start:end]
        chunks.append(chunk)

        if end >= len(cleaned):
            break

        start = max(end - overlap, start + 1)

    return chunks
