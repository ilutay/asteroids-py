# Stage 1: Build WASM bundle
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy game source files
COPY pyproject.toml uv.lock ./
COPY main.py game.py constants.py api_client.py score_repository.py ./
COPY asteroid.py asteroidfield.py player.py shot.py circleshape.py ./
COPY states/ ./states/
COPY ui/ ./ui/

# Install dependencies and build WASM bundle
RUN uv sync --frozen && \
    uv run pygbag --build main.py

# Stage 2: Runtime
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app/server

# Copy server source
COPY server/pyproject.toml server/uv.lock* ./
COPY server/main.py ./
COPY server/database/ ./database/
COPY server/migrations/ ./migrations/

# Create static/game directory and copy WASM bundle from builder
RUN mkdir -p static/game
COPY --from=builder /app/build/web/ ./static/game/

# Create data directory for SQLite
RUN mkdir -p data

# Install server dependencies
RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
