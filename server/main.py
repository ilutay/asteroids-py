import logging
import secrets
import time
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Header, Query, Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Server module loaded")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from database import DatabaseConnection, Migrator
from database.repositories import ScoreRepository

# Initialize database
db_connection = DatabaseConnection().get_connection()
Migrator(db_connection).run_migrations()
score_repository = ScoreRepository(db_connection)

# Token storage: token -> (created_at, used)
tokens: dict[str, tuple[float, bool]] = {}
TOKEN_EXPIRY_SECONDS = 3600  # 1 hour

app = FastAPI(title="Asteroids API")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenResponse(BaseModel):
    token: str


class ScoreSubmission(BaseModel):
    player_name: str
    score: int


class ScoreResponse(BaseModel):
    id: int
    player_name: str
    score: int
    played_at: str


class ScoresListResponse(BaseModel):
    scores: list[ScoreResponse]


class ScoreCreatedResponse(BaseModel):
    id: int


def _cleanup_expired_tokens():
    """Remove expired tokens."""
    now = time.time()
    expired = [
        t
        for t, (created_at, _) in tokens.items()
        if now - created_at > TOKEN_EXPIRY_SECONDS
    ]
    for t in expired:
        del tokens[t]


def _validate_token(authorization: Optional[str]) -> bool:
    """Validate Bearer token. Returns True if valid and marks as used."""
    if not authorization or not authorization.startswith("Bearer "):
        return False

    token = authorization[7:]
    _cleanup_expired_tokens()

    if token not in tokens:
        return False

    created_at, used = tokens[token]
    if used:
        return False

    # Mark as used
    tokens[token] = (created_at, True)
    return True


@app.post("/api/tokens", response_model=TokenResponse)
async def create_token():
    """Generate a single-use submission token."""
    _cleanup_expired_tokens()
    token = secrets.token_urlsafe(32)
    tokens[token] = (time.time(), False)
    logger.info("Token created")
    return TokenResponse(token=token)


@app.get("/api/scores", response_model=ScoresListResponse)
async def get_scores(limit: int = Query(default=10, ge=1, le=100)):
    """Get top scores."""
    logger.info(f"GET /api/scores limit={limit}")
    scores = score_repository.get_top_scores(limit)
    logger.info(f"Returning {len(scores)} scores")
    return ScoresListResponse(
        scores=[
            ScoreResponse(
                id=s.id,
                player_name=s.player_name,
                score=s.score,
                played_at=str(s.played_at) if s.played_at else "",
            )
            for s in scores
        ]
    )


@app.post("/api/scores", response_model=ScoreCreatedResponse)
async def submit_score(
    submission: ScoreSubmission,
    authorization: Optional[str] = Header(default=None),
):
    """Submit a new high score. Requires a valid Bearer token."""
    logger.info(f"Score submission: player={submission.player_name}, score={submission.score}")

    if not _validate_token(authorization):
        logger.warning("Score submission rejected: invalid token")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if not submission.player_name or len(submission.player_name) > 20:
        logger.warning(f"Score submission rejected: invalid player name '{submission.player_name}'")
        raise HTTPException(status_code=400, detail="Invalid player name")

    if submission.score < 0:
        logger.warning(f"Score submission rejected: invalid score {submission.score}")
        raise HTTPException(status_code=400, detail="Invalid score")

    row_id = score_repository.save_score(submission.player_name, submission.score)
    logger.info(f"Score saved: id={row_id}, player={submission.player_name}, score={submission.score}")
    return ScoreCreatedResponse(id=row_id)


# Proxy pygame-web archives from CDN
PYGAME_WEB_CDN = "https://pygame-web.github.io"


@app.get("/archives/{path:path}")
async def proxy_pygame_archives(path: str, request: Request):
    """Proxy requests to pygame-web CDN for WASM packages."""
    cdn_url = f"{PYGAME_WEB_CDN}/archives/{path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(cdn_url, follow_redirects=True)
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type"),
            )
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Failed to fetch from CDN")


# Serve static game files from root (must be last to not override API routes)
STATIC_DIR = Path(__file__).parent / "static" / "game"


@app.get("/")
async def root():
    """Serve game index."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "Asteroids API. Game not built yet - run 'make deploy'"
    }


# Serve other game static files (app.apk, favicon.png, etc.) from root
@app.get("/{filename:path}")
async def serve_game_files(filename: str):
    """Serve game static files."""
    # Don't serve if it's an API or archives route
    if filename.startswith("api/") or filename.startswith("archives/"):
        raise HTTPException(status_code=404)

    file_path = STATIC_DIR / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
