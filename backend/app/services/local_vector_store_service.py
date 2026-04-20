import json
import math
import uuid
from pathlib import Path
from typing import Any


STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "local_vector_store.json"


def add_documents(collection_name: str, documents: list[dict[str, Any]]) -> int:
    """
    Store embedded chunks in a local JSON vector store.

    This is a development fallback only. Milvus should remain the production
    storage path once collections and ingestion are configured.
    """
    records = _load_records()

    for document in documents:
        records.append(
            {
                "id": document.get("id") or str(uuid.uuid4()),
                "collection_name": collection_name,
                "text": document["text"],
                "embedding": document["embedding"],
                "source": document.get("source", ""),
                "metadata": document.get("metadata", {}),
            }
        )

    _save_records(records)
    return len(documents)


def search_documents(
    collection_name: str,
    embedding: list[float],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Search locally stored chunks using cosine similarity."""
    records = [
        record
        for record in _load_records()
        if record.get("collection_name") == collection_name
    ]

    scored_records = []
    for record in records:
        score = _cosine_similarity(embedding, record.get("embedding", []))
        scored_records.append(
            {
                "id": record.get("id", ""),
                "text": record.get("text", ""),
                "score": score,
                "source": record.get("source", ""),
                "metadata": record.get("metadata", {}),
            }
        )

    return sorted(scored_records, key=lambda item: item["score"], reverse=True)[:top_k]


def _load_records() -> list[dict[str, Any]]:
    if not STORE_PATH.exists():
        return []

    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save_records(records: list[dict[str, Any]]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot_product / (left_norm * right_norm)
