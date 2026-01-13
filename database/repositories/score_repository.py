import sqlite3
from dataclasses import dataclass
from datetime import datetime


@dataclass
class HighScore:
    id: int
    player_name: str
    score: int
    played_at: datetime


class ScoreRepository:
    """Data access for high scores table."""

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def save_score(self, player_name: str, score: int) -> int:
        """Insert a new high score. Returns the new row ID."""
        cursor = self.conn.execute(
            "INSERT INTO high_scores (player_name, score) VALUES (?, ?)",
            (player_name, score),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_top_scores(self, limit: int = 10) -> list[HighScore]:
        """Retrieve top N scores, ordered by score descending."""
        cursor = self.conn.execute(
            "SELECT id, player_name, score, played_at FROM high_scores "
            "ORDER BY score DESC LIMIT ?",
            (limit,),
        )
        results = []
        for row in cursor.fetchall():
            results.append(
                HighScore(
                    id=row["id"],
                    player_name=row["player_name"],
                    score=row["score"],
                    played_at=row["played_at"],
                )
            )
        return results

    def get_highest_score(self) -> int:
        """Return the highest score, or 0 if no scores exist."""
        cursor = self.conn.execute("SELECT MAX(score) as max_score FROM high_scores")
        result = cursor.fetchone()
        return result["max_score"] or 0 if result else 0

    def is_high_score(self, score: int) -> bool:
        """Check if score qualifies for top 10."""
        if score == 0:
            return False
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM high_scores WHERE score > ?",
            (score,),
        )
        count = cursor.fetchone()["count"]
        # Qualifies if fewer than 10 scores beat it
        return count < 10
