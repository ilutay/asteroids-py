import os
import sqlite3
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_db() -> Generator[sqlite3.Connection, None, None]:
    """Create a temporary test database."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Create schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS high_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    yield conn

    conn.close()
    os.unlink(path)


@pytest.fixture
def client(test_db: sqlite3.Connection) -> Generator[TestClient, None, None]:
    """Create a test client with isolated database."""
    # Patch the database connection before importing app
    import main
    from database.repositories import ScoreRepository

    # Replace the score repository with one using our test database
    main.score_repository = ScoreRepository(test_db)
    # Clear any tokens from previous tests
    main.tokens.clear()

    with TestClient(main.app) as client:
        yield client
