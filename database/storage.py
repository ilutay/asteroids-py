"""Storage abstraction for high scores - supports local SQLite and remote API."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .repositories.score_repository import HighScore, ScoreRepository

logger = logging.getLogger(__name__)


@dataclass
class SaveResult:
    """Result of a save operation."""

    success: bool
    error_message: str | None = None


class ScoreStorage(Protocol):
    """Protocol defining the interface for score storage backends."""

    def save_score(self, player_name: str, score: int) -> SaveResult:
        """Save a new score. Returns SaveResult indicating success/failure."""
        ...

    def get_top_scores(self, limit: int = 10) -> list[HighScore]:
        """Retrieve top N scores."""
        ...

    def get_highest_score(self) -> int:
        """Return the highest score, or 0 if none."""
        ...

    def is_high_score(self, score: int) -> bool:
        """Check if score qualifies for top 10."""
        ...


class LocalSQLiteStorage:
    """Local SQLite storage using existing ScoreRepository."""

    def __init__(self, repository: ScoreRepository):
        self._repo = repository

    def save_score(self, player_name: str, score: int) -> SaveResult:
        try:
            self._repo.save_score(player_name, score)
            return SaveResult(success=True)
        except Exception as e:
            logger.error(f"Failed to save score locally: {e}")
            return SaveResult(success=False, error_message=str(e))

    def get_top_scores(self, limit: int = 10) -> list[HighScore]:
        return self._repo.get_top_scores(limit)

    def get_highest_score(self) -> int:
        return self._repo.get_highest_score()

    def is_high_score(self, score: int) -> bool:
        return self._repo.is_high_score(score)


class RemoteAPIStorage:
    """Remote API storage for web client and optionally desktop."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self._is_web = self._detect_web()
        # Cache for web async loading
        self._cached_scores: list[HighScore] = []
        self._scores_loaded = False

    def _detect_web(self) -> bool:
        import sys

        return sys.platform == "emscripten"

    def save_score(self, player_name: str, score: int) -> SaveResult:
        if self._is_web:
            return self._save_score_web(player_name, score)
        else:
            return self._save_score_desktop(player_name, score)

    def _save_score_web(self, player_name: str, score: int) -> SaveResult:
        """Fire-and-forget score submission for web (Pyodide/Emscripten).

        Note: Returns success optimistically since we can't block for the response.
        The actual save happens asynchronously.
        """
        import asyncio
        import json

        async def _async_save() -> None:
            try:
                from pyodide.http import pyfetch

                response = await pyfetch(
                    f"{self.api_url}/scores",
                    method="POST",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key,
                    },
                    body=json.dumps({
                        "player_name": player_name,
                        "score": score,
                    }),
                )
                if response.status >= 400:
                    logger.error(
                        f"Failed to save score (web): HTTP {response.status}"
                    )
            except Exception as e:
                logger.error(f"Failed to save score (web): {e}")

        asyncio.create_task(_async_save())
        # Optimistic return - we can't block in the game loop
        return SaveResult(success=True)

    def _save_score_desktop(self, player_name: str, score: int) -> SaveResult:
        """Synchronous score submission for desktop."""
        import json
        import urllib.error
        import urllib.request

        data = json.dumps({
            "player_name": player_name,
            "score": score,
        }).encode("utf-8")

        request = urllib.request.Request(
            f"{self.api_url}/scores",
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status >= 400:
                    error_msg = f"Server returned HTTP {response.status}"
                    logger.error(f"Failed to save score: {error_msg}")
                    return SaveResult(success=False, error_message=error_msg)
            return SaveResult(success=True)
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP error {e.code}: {e.reason}"
            logger.error(f"Failed to save score: {error_msg}")
            return SaveResult(success=False, error_message=error_msg)
        except urllib.error.URLError as e:
            error_msg = f"Connection error: {e.reason}"
            logger.error(f"Failed to save score: {error_msg}")
            return SaveResult(success=False, error_message=error_msg)
        except TimeoutError:
            error_msg = "Request timed out"
            logger.error(f"Failed to save score: {error_msg}")
            return SaveResult(success=False, error_message=error_msg)

    def get_top_scores(self, limit: int = 10) -> list[HighScore]:
        if self._is_web:
            # Return cached scores for web (populated by async loading)
            return self._cached_scores[:limit]
        return self._get_top_scores_desktop(limit)

    def load_scores_async(self) -> None:
        """Start async loading of scores for web version. Call this on state enter."""
        if not self._is_web:
            return

        import asyncio

        async def _async_load() -> None:
            try:
                from pyodide.http import pyfetch

                response = await pyfetch(
                    f"{self.api_url}/scores",
                    method="GET",
                    headers={"Accept": "application/json"},
                )
                if response.ok:
                    import json

                    data = json.loads(await response.string())
                    scores = []
                    for item in data.get("scores", []):
                        played_at = item.get("played_at", "")
                        if isinstance(played_at, str):
                            played_at = datetime.fromisoformat(
                                played_at.replace("Z", "+00:00")
                            )
                        scores.append(
                            HighScore(
                                id=item["id"],
                                player_name=item["player_name"],
                                score=item["score"],
                                played_at=played_at,
                            )
                        )
                    self._cached_scores = scores
                    self._scores_loaded = True
                    logger.info(f"Loaded {len(scores)} scores from server")
                else:
                    logger.error(
                        f"Failed to load scores (web): HTTP {response.status}"
                    )
            except Exception as e:
                logger.error(f"Failed to load scores (web): {e}")

        asyncio.create_task(_async_load())

    def _get_top_scores_desktop(self, limit: int = 10) -> list[HighScore]:
        """Synchronous score fetching for desktop."""
        import json
        import urllib.error
        import urllib.request

        try:
            request = urllib.request.Request(
                f"{self.api_url}/scores",
                headers={"Accept": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                scores = []
                for item in data.get("scores", [])[:limit]:
                    played_at = item.get("played_at", "")
                    if isinstance(played_at, str):
                        played_at = datetime.fromisoformat(
                            played_at.replace("Z", "+00:00")
                        )
                    scores.append(
                        HighScore(
                            id=item["id"],
                            player_name=item["player_name"],
                            score=item["score"],
                            played_at=played_at,
                        )
                    )
                return scores
        except urllib.error.URLError as e:
            logger.error(f"Failed to load scores: {e}")
            return []

    def get_highest_score(self) -> int:
        scores = self.get_top_scores(1)
        return scores[0].score if scores else 0

    def is_high_score(self, score: int) -> bool:
        if score == 0:
            return False
        scores = self.get_top_scores(10)
        if len(scores) < 10:
            return True
        return score > scores[-1].score
