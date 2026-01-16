from datetime import datetime

from pydantic import BaseModel, Field


class ScoreSubmission(BaseModel):
    """Request body for POST /api/scores."""

    player_name: str = Field(..., max_length=20)
    score: int = Field(..., ge=0)


class HighScoreResponse(BaseModel):
    """Single high score entry."""

    id: int
    player_name: str
    score: int
    played_at: datetime


class ScoresResponse(BaseModel):
    """Response for GET /api/scores."""

    scores: list[HighScoreResponse]
