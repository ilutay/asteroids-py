import os
import sqlite3
from typing import ClassVar, Self


class DatabaseConnection:
    """Singleton connection manager for SQLite database."""

    _instance: ClassVar["DatabaseConnection | None"] = None
    DB_PATH: ClassVar[str] = "./data/asteroids.db"
    _connection: sqlite3.Connection | None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance  # type: ignore[return-value]

    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
            self._connection = sqlite3.connect(self.DB_PATH)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self) -> None:
        """Close the connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
