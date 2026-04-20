def rewrite_query(user_query: str) -> str:
    """
    Rewrite or expand a user query before retrieval.

    Advanced versions can add conversation history, acronyms, product aliases,
    or team-specific terminology. The current version normalizes whitespace.
    """
    return " ".join(user_query.strip().split())
