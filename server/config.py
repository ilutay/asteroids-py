import os
import sys
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.api_key: str = os.getenv("API_KEY", "").strip()
        self.database_path: str = os.getenv("DATABASE_PATH", "./data/asteroids.db")

    def validate(self) -> list[str]:
        """Validate settings and return list of errors."""
        errors = []
        if not self.api_key:
            errors.append("API_KEY environment variable is not set")
        return errors


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_settings_on_startup() -> None:
    """Validate settings on server startup. Exits if critical settings are missing."""
    settings = get_settings()
    errors = settings.validate()

    if errors:
        print("=" * 60, file=sys.stderr)
        print("CONFIGURATION ERROR - Server cannot start", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please set the required environment variables and restart.", file=sys.stderr)
        print("Example: export API_KEY=your-secret-key", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        sys.exit(1)
