"""Client-side score repository that wraps the async API client."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api_client import APIClient


@dataclass
class HighScore:
    id: int
    player_name: str
    score: int
    played_at: str


class ScoreRepository:
    """Wraps APIClient to provide interface for game states."""

    def __init__(self, api_client: "APIClient"):
        self.api_client = api_client

    async def get_highest_score(self) -> int:
        """Return the highest score."""
        return await self.api_client.get_highest_score()

    async def get_top_scores(self, limit: int = 10) -> list[HighScore]:
        """Retrieve top N scores."""
        api_scores = await self.api_client.get_top_scores(limit)
        return [
            HighScore(
                id=s.id,
                player_name=s.player_name,
                score=s.score,
                played_at=s.played_at,
            )
            for s in api_scores
        ]

    async def is_high_score(self, score: int) -> bool:
        """Check if score qualifies for top 10."""
        return await self.api_client.is_high_score(score)

    async def save_score(self, player_name: str, score: int) -> int | None:
        """Submit a new high score."""
        return await self.api_client.save_score(player_name, score)
