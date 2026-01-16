from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import db
from config import get_settings, validate_settings_on_startup
from models import HighScoreResponse, ScoresResponse, ScoreSubmission


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate configuration on startup."""
    validate_settings_on_startup()
    yield


app = FastAPI(title="Asteroids High Scores API", lifespan=lifespan)

# CORS for web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(x_api_key: str | None = Header(None)) -> None:
    """Verify the API key from header."""
    settings = get_settings()
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server",
        )
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/scores", response_model=ScoresResponse)
def get_scores():
    """Get top 10 high scores."""
    scores = db.get_top_scores(10)
    return ScoresResponse(
        scores=[HighScoreResponse(**score) for score in scores]
    )


@app.post("/api/scores", status_code=status.HTTP_201_CREATED)
def submit_score(
    submission: ScoreSubmission,
    x_api_key: str | None = Header(None),
):
    """Submit a new score. Requires API key."""
    verify_api_key(x_api_key)
    score_id = db.save_score(submission.player_name, submission.score)
    return {"id": score_id, "message": "Score submitted successfully"}


# Mount static files for pygame-web build (if directory exists)
static_path = Path("/app/static")
if static_path.exists():
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
