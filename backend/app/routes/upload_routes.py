from io import BytesIO

from flask import Blueprint, jsonify, request

from app.services.embedding_service import EmbeddingServiceError, embed_texts
from app.services.milvus_service import insert_vectors
from app.services.team_router_service import TeamNotFoundError, get_team_config
from app.utils.config import settings


upload_blueprint = Blueprint("upload", __name__, url_prefix="/upload")

SUPPORTED_FILE_TYPES = {
    "text/plain",
    "application/pdf",
    "application/json",
    "text/markdown",
    "text/csv",
}


@upload_blueprint.post("")
def upload_files():
    """
    Accept files, extract text, create embeddings, and store chunks in team-scoped Milvus.
    """
    team_name = request.form.get("team", "cloud")

    try:
        team_config = get_team_config(team_name)
    except TeamNotFoundError as exc:
        return jsonify({"detail": str(exc)}), 404

    files = request.files.getlist("files")
    if not files:
        return jsonify({"detail": "No files uploaded"}), 400
    if len(files) > settings.upload_max_files:
        return jsonify(
            {
                "detail": (
                    f"Too many files uploaded. Max allowed: {settings.upload_max_files}, "
                    f"received: {len(files)}."
                )
            }
        ), 400

    max_file_size_bytes = settings.upload_max_file_size_mb * 1024 * 1024
    max_total_size_bytes = settings.upload_max_total_size_mb * 1024 * 1024

    extracted_chunks: list[dict[str, object]] = []
    total_upload_size = 0
    skipped_files: list[str] = []
    processed_files: list[str] = []

    for uploaded_file in files:
        filename = (uploaded_file.filename or "uploaded-file").strip()
        content_type = (uploaded_file.content_type or "application/octet-stream").strip().lower()

        raw_bytes = uploaded_file.read()
        file_size = len(raw_bytes)
        total_upload_size += file_size

        if total_upload_size > max_total_size_bytes:
            return jsonify(
                {
                    "detail": (
                        f"Combined upload exceeded {settings.upload_max_total_size_mb} MB limit."
                    )
                }
            ), 400
        if file_size > max_file_size_bytes:
            skipped_files.append(filename)
            continue
        if content_type not in SUPPORTED_FILE_TYPES and not filename.lower().endswith(".pdf"):
            skipped_files.append(filename)
            continue

        text = _extract_text(raw_bytes=raw_bytes, content_type=content_type, filename=filename)
        chunks = _chunk_text(text)

        if not chunks:
            skipped_files.append(filename)
            continue

        processed_files.append(filename)
        for chunk_index, chunk in enumerate(chunks):
            extracted_chunks.append(
                {
                    "text": chunk,
                    "source": filename,
                    "metadata": {
                        "content_type": content_type,
                        "chunk_index": chunk_index,
                        "team": team_config.name,
                    },
                }
            )

    if not extracted_chunks:
        return jsonify(
            {
                "detail": (
                    "No valid text content was extracted from uploaded files. "
                    "Check file type, file size, and text content."
                )
            }
        ), 400

    try:
        vectors = _embed_in_batches([str(item["text"]) for item in extracted_chunks])
    except EmbeddingServiceError as exc:
        return jsonify({"detail": str(exc)}), 503

    documents_to_store = []
    for item, vector in zip(extracted_chunks, vectors):
        documents_to_store.append(
            {
                "text": item["text"],
                "embedding": vector,
                "source": item["source"],
                "metadata": item["metadata"],
            }
        )

    insert_vectors(team_config.collection_name, documents_to_store)

    return jsonify(
        {
            "status": "success",
            "files_received": len(files),
            "files_processed": len(processed_files),
            "files_skipped": len(skipped_files),
            "processed_filenames": processed_files,
            "skipped_filenames": skipped_files,
            "chunks_embedded": len(documents_to_store),
            "collection_name": team_config.collection_name,
            "embedding_model": settings.ollama_embedding_model,
        }
    )


def _extract_text(raw_bytes: bytes, content_type: str, filename: str) -> str:
    """Extract text from supported upload types."""
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return _extract_pdf_text(raw_bytes)

    decoded_text = raw_bytes.decode("utf-8", errors="ignore")
    return decoded_text.strip()


def _extract_pdf_text(raw_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(raw_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception:
        return ""


def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    """Split text into overlapping chunks while skipping short noise-only chunks."""
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []

    chunks = []
    start = 0
    while start < len(cleaned_text):
        end = start + chunk_size
        chunk = cleaned_text[start:end].strip()
        if len(chunk) >= 40:
            chunks.append(chunk)
        if end >= len(cleaned_text):
            break
        start = max(end - overlap, start + 1)

    return chunks


def _embed_in_batches(texts: list[str]) -> list[list[float]]:
    """Embed text chunks in smaller batches to avoid timeout on slower Ollama hosts."""
    batch_size = max(1, settings.embedding_batch_size)
    vectors: list[list[float]] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        vectors.extend(embed_texts(batch))

    return vectors
