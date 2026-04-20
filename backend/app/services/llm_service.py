def generate_answer(context: str, question: str, prompt_template: str) -> str:
    """
    Generate an answer using retrieved context and a team prompt template.

    This project is local-only. The current implementation returns a simple
    extractive answer from retrieved context instead of calling an external LLM.
    """
    _ = prompt_template
    return _generate_locally(context=context, question=question)


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
