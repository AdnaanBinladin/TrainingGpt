from typing import Any

from pymilvus import Collection, connections, utility

from app.services.local_vector_store_service import add_documents, search_documents
from app.utils.config import settings


_IS_CONNECTED = False


def search_vectors(
    collection_name: str,
    embedding: list[float],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Search a team-specific Milvus collection.

    The collection name is supplied by team routing, which lets each team keep
    isolated data today and enables tenant-aware routing later.
    """
    try:
        _connect()

        if not utility.has_collection(collection_name):
            return search_documents(collection_name, embedding, top_k)

        collection = Collection(collection_name)
        collection.load()

        search_results = collection.search(
            data=[embedding],
            anns_field=settings.milvus_vector_field,
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=top_k,
            output_fields=[settings.milvus_text_field, "source", "metadata"],
        )

        results = [_hit_to_dict(hit) for hit in search_results[0]]
        if results:
            return results

        return search_documents(collection_name, embedding, top_k)
    except Exception as exc:
        local_results = search_documents(collection_name, embedding, top_k)
        if local_results:
            for result in local_results:
                result.setdefault("metadata", {})
                result["metadata"]["retrieval_fallback"] = "local_json_store"
            return local_results

        return [
            {
                "id": "retrieval-error",
                "text": "",
                "score": 0.0,
                "error": f"Milvus search failed and local store is empty: {exc}",
            }
        ]


def insert_vectors(collection_name: str, data: list[dict[str, Any]]) -> None:
    """
    Insert embedded documents into a team-specific Milvus collection.

    This is a placeholder for ingestion workflows. Production code should
    validate schemas, create collections if needed, and handle batch failures.
    """
    try:
        _connect()

        if not utility.has_collection(collection_name):
            add_documents(collection_name, data)
            return

        collection = Collection(collection_name)
        collection.insert(data)
        collection.flush()
    except Exception:
        add_documents(collection_name, data)


def _connect() -> None:
    """Create a shared Milvus connection for this process."""
    global _IS_CONNECTED

    if _IS_CONNECTED:
        return

    connections.connect(
        alias="default",
        host=settings.milvus_host,
        port=str(settings.milvus_port),
    )
    _IS_CONNECTED = True


def _hit_to_dict(hit: Any) -> dict[str, Any]:
    """Normalize a Milvus hit into the shape consumed by the chat route."""
    entity = getattr(hit, "entity", None)

    def get_field(name: str, default: Any = None) -> Any:
        if entity is None:
            return default
        try:
            return entity.get(name)
        except Exception:
            return default

    return {
        "id": str(getattr(hit, "id", "")),
        "text": get_field(settings.milvus_text_field, ""),
        "score": float(getattr(hit, "score", 0.0)),
        "source": get_field("source", ""),
        "metadata": get_field("metadata", {}),
    }
