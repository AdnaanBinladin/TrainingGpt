import os
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)


class AppSettings:
    """Environment-backed settings shared across backend services."""

    milvus_host: str = os.getenv("MILVUS_HOST", "127.0.0.1")
    milvus_port: int = int(os.getenv("MILVUS_PORT", "19530"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    milvus_vector_field: str = os.getenv("MILVUS_VECTOR_FIELD", "embedding")
    milvus_text_field: str = os.getenv("MILVUS_TEXT_FIELD", "text")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
    embedding_batch_size: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "16"))
    embedding_retries: int = int(os.getenv("EMBEDDING_RETRIES", "2"))
    upload_max_files: int = int(os.getenv("UPLOAD_MAX_FILES", "20"))
    upload_max_file_size_mb: int = int(os.getenv("UPLOAD_MAX_FILE_SIZE_MB", "10"))
    upload_max_total_size_mb: int = int(os.getenv("UPLOAD_MAX_TOTAL_SIZE_MB", "50"))


settings = AppSettings()
