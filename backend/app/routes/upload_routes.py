from flask import Blueprint, jsonify, request

from app.services.embedding_service import embed_query
from app.services.milvus_service import insert_vectors
from app.services.team_router_service import TeamNotFoundError, get_team_config


upload_blueprint = Blueprint("upload", __name__, url_prefix="/upload")


@upload_blueprint.post("")
def upload_files():
    """
    Accept files for a future embedding pipeline.

    This is a testing stub only. Production code should validate file types,
    store files, extract text/media content, create embeddings, and insert the
    resulting vectors into the correct Milvus collection.
    """
    team_name = request.form.get("team", "cloud")

    try:
        team_config = get_team_config(team_name)
    except TeamNotFoundError as exc:
        return jsonify({"detail": str(exc)}), 404

    files = request.files.getlist("files")

    if not files:
        return jsonify({"detail": "No files uploaded"}), 400

    documents = []
    for uploaded_file in files:
        text = _extract_text(uploaded_file)
        chunks = _chunk_text(text)

        for chunk_index, chunk in enumerate(chunks):
            documents.append(
                {
                    "text": chunk,
                    "embedding": embed_query(chunk),
                    "source": uploaded_file.filename,
                    "metadata": {
                        "content_type": uploaded_file.content_type,
                        "chunk_index": chunk_index,
                    },
                }
            )

    insert_vectors(team_config.collection_name, documents)

    return jsonify(
        {
            "status": "success",
            "files_received": len(files),
            "filenames": [file.filename for file in files],
            "chunks_embedded": len(documents),
            "collection_name": team_config.collection_name,
        }
    )


def _extract_text(uploaded_file) -> str:
    """
    Extract basic text for local RAG testing.

    PDF/image/video extraction is intentionally minimal. Add OCR, video
    transcription, and robust PDF parsing when production ingestion is needed.
    """
    filename = uploaded_file.filename or "uploaded-file"
    content_type = uploaded_file.content_type or "application/octet-stream"
    raw_bytes = uploaded_file.read()

    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return _extract_pdf_text(raw_bytes) or _fallback_file_text(filename, content_type)

    if content_type.startswith("image/") or content_type.startswith("video/"):
        return _fallback_file_text(filename, content_type)

    decoded_text = raw_bytes.decode("utf-8", errors="ignore").strip()
    return decoded_text or _fallback_file_text(filename, content_type)


def _extract_pdf_text(raw_bytes: bytes) -> str:
    """Best-effort PDF extraction if pypdf is installed."""
    try:
        from io import BytesIO

        from pypdf import PdfReader

        reader = PdfReader(BytesIO(raw_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception:
        return ""


def _fallback_file_text(filename: str, content_type: str) -> str:
    return (
        f"Uploaded file: {filename}\n"
        f"Content type: {content_type}\n"
        "No text extraction is configured for this file type yet."
    )


def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    """Split text into simple overlapping chunks."""
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []

    chunks = []
    start = 0
    while start < len(cleaned_text):
        end = start + chunk_size
        chunks.append(cleaned_text[start:end])
        if end >= len(cleaned_text):
            break
        start = max(end - overlap, start + 1)

    return chunks
