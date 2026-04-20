import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.utils.config import settings


def generate_answer(context: str, question: str, prompt_template: str) -> str:
    """
    Generate an answer using retrieved context and a team prompt template.

    The backend calls the configured Ollama server. During laptop development,
    OLLAMA_BASE_URL can point at the VM where llama3 is running.
    """
    prompt = _build_prompt(context=context, question=question, prompt_template=prompt_template)
    return _generate_with_ollama(prompt=prompt, context=context, question=question)


def _build_prompt(context: str, question: str, prompt_template: str) -> str:
    """Build the final LLM prompt from team prompt, context, and question."""
    return f"""{prompt_template}

Context:
{context or "No retrieved context."}

Question:
{question}

Answer:"""


def _generate_locally(context: str, question: str) -> str:
    """
    Return a transparent local answer from retrieved context.

    This keeps the chat endpoint testable and makes missing infrastructure clear.
    """
    if not context.strip():
        return (
            "I could not find retrieved context for this question. "
            "Check that Milvus is running, the collection exists, and documents "
            "have been embedded."
        )

    trimmed_context = context.strip()
    if len(trimmed_context) > 1200:
        trimmed_context = f"{trimmed_context[:1200]}..."

    return (
        "Here is the retrieved local context that "
        f"matches your question: {question}\n\n{trimmed_context}"
    )


def _generate_with_ollama(prompt: str, context: str, question: str) -> str:
    """Call Ollama's generate API and fall back to retrieved context if unavailable."""
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.ollama_timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        fallback = _generate_locally(context=context, question=question)
        return (
            "I could not reach the configured Ollama LLM at "
            f"{settings.ollama_base_url} using model {settings.ollama_model}. "
            f"Reason: {exc}\n\n{fallback}"
        )

    answer = response_payload.get("response", "").strip()
    if not answer:
        return _generate_locally(context=context, question=question)

    return answer
