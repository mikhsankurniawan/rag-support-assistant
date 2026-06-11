from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Support MVP"
    database_url: str

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    chunk_size: int = 900
    chunk_overlap: int = 150
    default_top_k: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
