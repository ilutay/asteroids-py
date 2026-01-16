import glob
import os
import sqlite3


class Migrator:
    """Runs SQL migrations in order based on version prefix."""

    MIGRATIONS_DIR = "./migrations"

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def run_migrations(self) -> None:
        """Execute all pending migrations."""
        self._ensure_schema_table()
        applied = self._get_applied_versions()

        migration_files = sorted(glob.glob(f"{self.MIGRATIONS_DIR}/V*.sql"))

        for filepath in migration_files:
            filename = os.path.basename(filepath)
            version = filename.split("__")[0]
            description = filename.split("__")[1].replace(".sql", "") if "__" in filename else ""

            if version not in applied:
                self._apply_migration(filepath, version, description)

    def _ensure_schema_table(self) -> None:
        """Create schema_version table if it doesn't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        self.conn.commit()

    def _get_applied_versions(self) -> set[str]:
        """Return set of already-applied migration versions."""
        cursor = self.conn.execute("SELECT version FROM schema_version")
        return {row[0] for row in cursor.fetchall()}

    def _apply_migration(self, filepath: str, version: str, description: str) -> None:
        """Execute a single migration file."""
        with open(filepath) as f:
            sql = f.read()

        self.conn.executescript(sql)
        self.conn.execute(
            "INSERT INTO schema_version (version, description) VALUES (?, ?)",
            (version, description),
        )
        self.conn.commit()
        print(f"Applied migration: {version} - {description}")
