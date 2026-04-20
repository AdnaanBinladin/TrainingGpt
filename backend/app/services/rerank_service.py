from typing import Any


def rerank_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Rerank retrieval results before answer generation.

    Production implementations can use cross-encoders, LLM reranking, business
    rules, freshness boosts, or permission-aware filtering.
    """
    return sorted(results, key=lambda item: item.get("score", 0.0), reverse=True)
