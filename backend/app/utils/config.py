import os
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)


class AppSettings:
    """Environment-backed settings shared across backend services."""

    milvus_host: str = os.getenv("MILVUS_HOST", "localhost")
    milvus_port: int = int(os.getenv("MILVUS_PORT", "19530"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    milvus_vector_field: str = os.getenv("MILVUS_VECTOR_FIELD", "embedding")
    milvus_text_field: str = os.getenv("MILVUS_TEXT_FIELD", "text")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))


settings = AppSettings()
