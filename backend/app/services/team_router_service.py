from importlib import import_module
from pathlib import Path

from app.models.schemas import TeamConfig


ALLOWED_TEAMS = {"cloud", "dayforce"}
TEAM_PACKAGE_ROOT = "app.teams"
TEAM_FOLDER_ROOT = Path(__file__).resolve().parents[1] / "teams"


class TeamNotFoundError(ValueError):
    """Raised when a request references an unknown or unsupported team."""


def get_team_config(team_name: str) -> TeamConfig:
    """
    Resolve the collection, prompt template, and settings for a team.

    Today this reads local Python config and prompt files. In a multi-tenant
    future, this function can become the adapter to a tenant config database,
    feature flag system, or centralized control plane.
    """
    normalized_team = team_name.strip().lower()
    if normalized_team not in ALLOWED_TEAMS:
        raise TeamNotFoundError(f"Unknown team: {team_name}")

    config_module = import_module(f"{TEAM_PACKAGE_ROOT}.{normalized_team}.config")
    prompt_template = _load_prompt_template(normalized_team)

    return TeamConfig(
        name=normalized_team,
        collection_name=config_module.collection_name,
        prompt_template=prompt_template,
        settings=getattr(config_module, "settings", {}),
    )


def _load_prompt_template(team_name: str) -> str:
    """Load the prompt template owned by a specific team."""
    prompt_path = TEAM_FOLDER_ROOT / team_name / "prompt_template.txt"
    return prompt_path.read_text(encoding="utf-8")
