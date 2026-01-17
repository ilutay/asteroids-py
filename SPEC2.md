# Web Development Workflow

## Quick Start

```bash
# First time setup
make install
make install-server

# Build and run
make deploy
make server
# Open http://localhost:8000
```

## Architecture

FastAPI serves **both** the game files AND the API from the same origin:

```
localhost:8000/         → game HTML/JS/WASM (from server/static/game/)
localhost:8000/api/...  → API endpoints
```

This allows relative API URLs (`/api/scores`) to work without any configuration.

## Development Workflow

### Option 1: Simple (Manual Rebuild)

```bash
# Terminal 1: Start server (auto-reloads server code)
make server

# When you change game code:
make deploy
# Refresh browser
```

### Option 2: Auto-Rebuild (Two Terminals)

```bash
# Terminal 1: Start server
make server

# Terminal 2: Watch for changes and auto-rebuild
make watch
# Refresh browser after rebuild completes
```

### Option 3: Quick Start

```bash
# Build, deploy, and start server in one command
make dev
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `make install` | Install game dependencies |
| `make install-server` | Install server dependencies |
| `make run-desktop` | Run game in desktop mode (pygame) |
| `make build` | Build WASM bundle with pygbag |
| `make deploy` | Build and copy to server static dir |
| `make server` | Start FastAPI server on port 8000 |
| `make watch` | Watch for changes and auto-rebuild |
| `make dev` | Build, deploy, and start server |
| `make clean` | Remove build artifacts |

## Why This Architecture?

### The Problem

When developing with separate servers:
- pygbag dev server on port 8001
- FastAPI API on port 8000

Relative API URLs (`/api/scores`) fail because they resolve to the wrong origin.

### The Solution

Use FastAPI to serve everything:
- Game files: `server/static/game/`
- API endpoints: `/api/*`

Same origin = relative URLs work automatically. No CORS issues, no URL configuration needed.

## Troubleshooting

### High scores not saving?

1. Make sure you're accessing the game at `http://localhost:8000`
2. NOT at `http://localhost:8001` (pygbag dev server)
3. Check browser console for network errors

### Changes not reflecting?

1. Run `make deploy` to rebuild
2. Hard refresh browser (Cmd+Shift+R on Mac)
3. Check that the server is running on port 8000
