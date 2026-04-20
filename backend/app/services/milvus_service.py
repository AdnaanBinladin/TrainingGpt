import uuid
from typing import Any

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from app.services.local_vector_store_service import add_documents, search_documents
from app.utils.config import settings


_IS_CONNECTED = False


def search_vectors(
    collection_name: str,
    embedding: list[float],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Search a team-specific Milvus collection, falling back to local storage on failure.
    """
    try:
        _connect()
        collection = _ensure_collection(collection_name)
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
    Insert embedded documents into Milvus and fall back to local storage if unavailable.
    """
    if not data:
        return

    try:
        _connect()
        collection = _ensure_collection(collection_name)
        insert_payload = _prepare_insert_payload(data)
        collection.insert(insert_payload)
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


def _ensure_collection(collection_name: str) -> Collection:
    if utility.has_collection(collection_name):
        return Collection(collection_name)

    schema = CollectionSchema(
        fields=[
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
            FieldSchema(name=settings.milvus_text_field, dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(
                name=settings.milvus_vector_field,
                dtype=DataType.FLOAT_VECTOR,
                dim=settings.embedding_dimension,
            ),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ],
        description="Team-scoped RAG document chunks",
        enable_dynamic_field=False,
    )

    collection = Collection(name=collection_name, schema=schema)
    collection.create_index(
        field_name=settings.milvus_vector_field,
        index_params={
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        },
    )
    collection.load()
    return collection


def _prepare_insert_payload(documents: list[dict[str, Any]]) -> list[list[Any]]:
    ids: list[str] = []
    texts: list[str] = []
    vectors: list[list[float]] = []
    sources: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for document in documents:
        text = str(document.get("text", "")).strip()
        embedding = document.get("embedding", [])

        if not text or not isinstance(embedding, list):
            continue
        if len(embedding) != settings.embedding_dimension:
            continue

        ids.append(str(document.get("id") or uuid.uuid4()))
        texts.append(text[:8192])
        vectors.append([float(value) for value in embedding])
        sources.append(str(document.get("source", ""))[:1024])
        metadata = document.get("metadata", {})
        metadatas.append(metadata if isinstance(metadata, dict) else {"value": str(metadata)})

    if not ids:
        raise ValueError("No valid documents were prepared for Milvus insertion.")

    return [ids, texts, vectors, sources, metadatas]


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
