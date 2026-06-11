from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    # pgvector extension must exist before vector columns are created.
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    # Import models here so SQLAlchemy registers them.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Optional HNSW index for faster similarity search.
    # It is safe if this fails during very early development.
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
                ON chunks
                USING hnsw (embedding vector_cosine_ops)
                """
            )
        )
