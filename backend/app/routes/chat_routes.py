from flask import Blueprint, jsonify, request

from app.models.schemas import ChatRequest, ChatResponse
from app.services.embedding_service import embed_query
from app.services.llm_service import generate_answer
from app.services.milvus_service import search_vectors
from app.services.query_rewrite_service import rewrite_query
from app.services.rerank_service import rerank_results
from app.services.team_router_service import TeamNotFoundError, get_team_config


chat_blueprint = Blueprint("chat", __name__, url_prefix="/chat")


@chat_blueprint.post("")
def chat():
    """
    Handle a team-scoped chat request.

    This route shows the intended local RAG orchestration flow. Each step
    delegates to a service that can later gain observability, retries, and
    policy checks without changing the endpoint contract.
    """
    payload = request.get_json(silent=True) or {}
    chat_request = ChatRequest.from_payload(payload)

    if chat_request.error:
        return jsonify({"detail": chat_request.error}), 400

    try:
        team_config = get_team_config(chat_request.team)
    except TeamNotFoundError as exc:
        return jsonify({"detail": str(exc)}), 404

    rewritten_query = rewrite_query(chat_request.query)
    query_embedding = embed_query(rewritten_query)

    raw_results = search_vectors(
        collection_name=team_config.collection_name,
        embedding=query_embedding,
        top_k=team_config.settings.get("top_k", 5),
    )
    ranked_results = rerank_results(raw_results)

    context = "\n\n".join(item.get("text", "") for item in ranked_results if item.get("text"))
    answer = generate_answer(
        context=context,
        question=chat_request.query,
        prompt_template=team_config.prompt_template,
    )

    response = ChatResponse(
        team=chat_request.team,
        answer=answer,
        sources=ranked_results,
        metadata={
            "collection_name": team_config.collection_name,
            "rewritten_query": rewritten_query,
            "retrieved_count": len([item for item in ranked_results if item.get("text")]),
            "embedding_dimension": len(query_embedding),
        },
    )

    return jsonify(response.to_dict())
