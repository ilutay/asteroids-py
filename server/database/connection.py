import os
import sqlite3
from pathlib import Path


class DatabaseConnection:
    """Singleton connection manager for SQLite database."""

    _instance: "DatabaseConnection | None" = None
    _SERVER_DIR = Path(__file__).parent.parent
    DB_PATH = _SERVER_DIR / "data" / "asteroids.db"

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            os.makedirs(self.DB_PATH.parent, exist_ok=True)
            self._connection = sqlite3.connect(str(self.DB_PATH))
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self) -> None:
        """Close the connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
