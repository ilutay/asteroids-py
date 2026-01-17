# Asteroids

A classic Asteroids game built with Pygame, deployable to the web using Pygbag.

## Requirements

- Python 3.12+
- uv (for dependency management)

## Development Setup

### Game (Desktop)

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py
```

### Server

```bash
# Install server dependencies
cd server
uv sync

# Run the server
uv run uvicorn main:app --port 8001 --reload
```

## Web Deployment

### Build the Game for Web

```bash
# Build WASM bundle
uv run pygbag --build main.py

# Copy build to server static directory
cp -r build/web/* server/static/game/
```

### Run Full Stack

1. Build the game (see above)
2. Start the server:
   ```bash
   cd server
   uv run uvicorn main:app --port 8001
   ```
3. Open http://localhost:8001/ in your browser

## Controls

- **Arrow Keys**: Rotate and thrust
- **Space**: Fire
- **Escape**: Pause game

## API Endpoints

- `POST /api/tokens` - Generate submission token
- `GET /api/scores?limit=10` - Get top scores
- `POST /api/scores` - Submit score (requires Bearer token)
