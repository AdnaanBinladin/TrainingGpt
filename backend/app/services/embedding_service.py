import hashlib
import math

from app.utils.config import settings


def embed_query(query: str) -> list[float]:
    """
    Convert a user query into an embedding vector.

    This project is local-only. The current implementation uses a deterministic
    bag-of-words hash embedding so upload and chat can be tested with local
    code only.
    """
    return _embed_locally(query.strip())


def _embed_locally(query: str) -> list[float]:
    """
    Create a deterministic bag-of-words hash embedding.

    This is not semantically smart. It exists only so the RAG flow can be
    exercised locally before a real embedding model is configured.
    """
    dimension = settings.embedding_dimension
    vector = [0.0] * dimension

    for token in query.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector

    return [value / norm for value in vector]
