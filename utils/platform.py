"""Platform detection and storage factory."""

import os
import sys

from database.repositories.score_repository import ScoreRepository
from database.storage import LocalSQLiteStorage, RemoteAPIStorage, ScoreStorage


class ConfigurationError(Exception):
    """Raised when required configuration is missing."""

    pass


def is_web() -> bool:
    """Check if running in browser via Emscripten/Pyodide."""
    return sys.platform == "emscripten"


def _get_remote_config(
    api_url: str | None = None,
    api_key: str | None = None,
) -> tuple[str, str]:
    """
    Get and validate remote API configuration.

    Returns (api_url, api_key) tuple.
    Raises ConfigurationError if required values are missing.
    """
    url = api_url or os.getenv("API_URL", "").strip()
    key = api_key or os.getenv("API_KEY", "").strip()

    missing = []
    if not url:
        missing.append("API_URL")
    if not key:
        missing.append("API_KEY")

    if missing:
        raise ConfigurationError(
            f"Remote API requires environment variables: {', '.join(missing)}. "
            f"Set them in .env file or environment."
        )

    return url, key


def get_storage(
    repository: ScoreRepository | None = None,
    api_url: str | None = None,
    api_key: str | None = None,
) -> ScoreStorage:
    """
    Get the appropriate storage backend.

    For web: always uses RemoteAPIStorage
    For desktop: uses LocalSQLiteStorage by default, or RemoteAPIStorage if configured

    Raises:
        ConfigurationError: If remote API is required but API_URL/API_KEY are not set.
    """
    if is_web():
        # Web always uses remote API
        url, key = _get_remote_config(api_url, api_key)
        return RemoteAPIStorage(api_url=url, api_key=key)

    # Desktop: check if remote API is configured
    use_remote = os.getenv("USE_REMOTE_API", "false").lower() == "true"

    if use_remote:
        url, key = _get_remote_config(api_url, api_key)
        return RemoteAPIStorage(api_url=url, api_key=key)

    # Default: local SQLite
    if repository is None:
        raise ValueError("repository required for LocalSQLiteStorage")
    return LocalSQLiteStorage(repository)
