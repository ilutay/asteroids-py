import sqlite3
from datetime import datetime
from pathlib import Path

from config import get_settings

_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    """Get or create the singleton database connection."""
    global _connection
    if _connection is None:
        settings = get_settings()
        db_path = Path(settings.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        _connection = sqlite3.connect(db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _init_schema(_connection)
    return _connection


def _init_schema(conn: sqlite3.Connection) -> None:
    """Initialize database schema if not exists."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS high_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_high_scores_score
        ON high_scores(score DESC)
    """)
    conn.commit()


def save_score(player_name: str, score: int) -> int:
    """Insert a new high score. Returns the new row ID."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO high_scores (player_name, score) VALUES (?, ?)",
        (player_name, score),
    )
    conn.commit()
    return cursor.lastrowid


def get_top_scores(limit: int = 10) -> list[dict]:
    """Retrieve top N scores, ordered by score descending."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT id, player_name, score, played_at FROM high_scores "
        "ORDER BY score DESC LIMIT ?",
        (limit,),
    )
    results = []
    for row in cursor.fetchall():
        played_at = row["played_at"]
        if isinstance(played_at, str):
            played_at = datetime.fromisoformat(played_at.replace("Z", "+00:00"))
        results.append({
            "id": row["id"],
            "player_name": row["player_name"],
            "score": row["score"],
            "played_at": played_at,
        })
    return results
