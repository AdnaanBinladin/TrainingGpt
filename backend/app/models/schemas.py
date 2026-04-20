from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatRequest:
    """Incoming chat request scoped to a specific team."""

    team: str
    query: str
    error: str | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ChatRequest":
        """
        Validate the raw Flask JSON payload.

        This is intentionally lightweight for the scaffold. Production code can
        replace it with Marshmallow, Pydantic, or another validation layer.
        """
        team = str(payload.get("team", "cloud")).strip().lower()
        query = str(payload.get("query", "")).strip()

        if not team:
            team = "cloud"
        if not query:
            return cls(team=team, query="", error="'query' is required")

        return cls(team=team, query=query)


@dataclass
class ChatResponse:
    """Response returned by the RAG pipeline."""

    team: str
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a JSON-serializable dictionary."""
        return {
            "team": self.team,
            "answer": self.answer,
            "sources": self.sources,
            "metadata": self.metadata,
        }


@dataclass
class TeamConfig:
    """Resolved team configuration used by shared backend services."""

    name: str
    collection_name: str
    prompt_template: str
    settings: dict[str, Any] = field(default_factory=dict)
