from app.services.chunker import chunk_text


def test_chunk_text_returns_chunks_for_valid_text():
    text = "This is a test sentence. " * 200

    chunks = chunk_text(text)

    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk.strip()) > 0 for chunk in chunks)


def test_chunk_text_returns_empty_for_blank_text():
    chunks = chunk_text("   \n\n   ")

    assert chunks == []