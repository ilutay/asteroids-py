# SPEC: Pygbag Web Migration

Migrate the Asteroids game from desktop pygame to browser-based deployment using pygbag.

## Overview

Convert the existing pygame Asteroids game to run in web browsers via pygbag (WebAssembly). The desktop version will be deprecated in favor of a web-only future.

## Technical Decisions

### Platform & Runtime
- **Target**: Modern browsers only (Chrome, Firefox, Safari, Edge)
- **Python version**: Downgrade to 3.12 (pygbag WASM compatibility)
- **Framework**: pygame + pygbag
- **Build command**: `pygbag --build main.py` (manual execution)

### Hosting Architecture
- **Same-origin deployment**: Game served from FastAPI backend at `/static/game/`
- **No CORS configuration needed** (same origin)
- **API base URL**: Relative paths (e.g., `/api/scores`)

### Game Loop Refactor
- **Full async refactor** of the game loop
- Convert blocking `while True` loop to async pattern with `await asyncio.sleep(0)`
- Update all state classes to support async operations

### Display & Canvas
- **Responsive canvas**: Scale to fit browser viewport
- **Maintain aspect ratio**: 16:9 (1280x720 internal resolution)
- **CSS-based scaling**: Game logic stays at 1280x720, browser handles visual scaling

### Input
- **Keyboard only**: WASD + Space controls
- **No touch support** in initial release

## Data & Persistence

### High Scores
- **Storage**: FastAPI backend API (not browser local storage)
- **Authentication**: Anonymous tokens for score submission
- **API endpoints**:
  - `GET /api/scores` - Retrieve top 10 scores
  - `POST /api/scores` - Submit new score (requires token)
  - `POST /api/tokens` - Request anonymous submission token

### Offline Behavior
- **Show error state** when API unreachable
- **Disable high-scores features** until API returns
- **Gameplay continues** uninterrupted

## Code Changes

### Remove
- [ ] `logger.py` - File-based logging not supported in browser
- [ ] `.env` file from game directory (server handles config)
- [ ] Direct SQLite imports from game code

### Move to Server
- [ ] `database/connection.py` → `server/database/connection.py`
- [ ] `database/migrator.py` → `server/database/migrator.py`
- [ ] `database/repositories/` → `server/database/repositories/`
- [ ] `migrations/` → `server/migrations/`
- [ ] `data/asteroids.db` → `server/data/asteroids.db`

### Modify
- [ ] `main.py` - Add async entry point for pygbag
- [ ] `game.py` - Convert game loop to async
- [ ] `states/*.py` - Add async support to state methods
- [ ] `pyproject.toml` - Downgrade Python to >=3.12, add pygbag dependency
- [ ] `constants.py` - Update API configuration

### Add
- [ ] `api_client.py` - Async HTTP client for score API
- [ ] `index.html` - Custom template for pygbag (optional)
- [ ] Build instructions in README

## Server API Additions

### New Endpoints
```
POST /api/tokens
  Response: { "token": "<uuid>" }

POST /api/scores
  Headers: Authorization: Bearer <token>
  Body: { "player_name": "AAA", "score": 12500 }
  Response: { "success": true, "rank": 3 }

GET /api/scores?limit=10
  Response: { "scores": [{ "player_name": "AAA", "score": 12500, "rank": 1 }, ...] }
```

### Token Behavior
- Tokens are single-use (one score submission per token)
- Tokens expire after 1 hour
- No user registration required

## File Structure (After Migration)

```
asteroids-py/
├── main.py              # Async entry point
├── game.py              # Async game loop
├── constants.py         # Game config + API paths
├── api_client.py        # NEW: Score API client
├── pyproject.toml       # Python 3.12+, pygbag dependency
├── README.md            # Build instructions
│
├── states/
│   ├── base_state.py
│   ├── main_menu_state.py
│   ├── playing_state.py
│   ├── paused_state.py
│   ├── game_over_state.py
│   └── high_scores_state.py
│
├── ui/
│   └── hud.py
│
├── (game objects)
│   ├── player.py
│   ├── asteroid.py
│   ├── asteroidfield.py
│   ├── shot.py
│   └── circleshape.py
│
├── build/               # pygbag output (gitignored)
│
└── server/
    ├── main.py          # FastAPI app
    ├── database/
    │   ├── connection.py
    │   ├── migrator.py
    │   └── repositories/
    │       └── score_repository.py
    ├── migrations/
    │   ├── V20260113_01__init.sql
    │   └── V20260113_02__high_scores.sql
    ├── data/
    │   └── asteroids.db
    └── static/
        └── game/        # pygbag build output served here
```

## Build & Deploy Process

1. **Build game**: `pygbag --build main.py`
2. **Copy to server**: Move `build/web/` contents to `server/static/game/`
3. **Start server**: `uvicorn server.main:app`
4. **Access game**: `http://localhost:8001/static/game/index.html`

## Migration Steps

### Phase 1: Preparation
1. Downgrade Python requirement to 3.12
2. Add pygbag to dependencies
3. Remove logger.py
4. Move database code to server/

### Phase 2: Async Conversion
1. Convert main.py to async entry point
2. Refactor game.py loop to async
3. Update state classes for async compatibility

### Phase 3: API Integration
1. Create api_client.py with async HTTP requests
2. Add token/score endpoints to FastAPI server
3. Replace ScoreRepository calls with API client calls
4. Add error handling UI for offline state

### Phase 4: Testing & Polish
1. Test in multiple browsers
2. Verify responsive scaling
3. Test offline/error scenarios
4. Update README with build instructions

## Out of Scope
- Touch/mobile controls
- User accounts/registration
- Offline score caching/sync
- Legacy browser support
- CI/CD pipeline
