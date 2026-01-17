.PHONY: install install-server build deploy run run-desktop server watch dev lint format test clean help

# Default target
help:
	@echo "Asteroids - Build Commands"
	@echo ""
	@echo "  make install        Install game dependencies"
	@echo "  make install-server Install server dependencies"
	@echo "  make run-desktop    Run game in desktop mode"
	@echo "  make build          Build WASM bundle with pygbag"
	@echo "  make deploy         Build and copy to server static dir"
	@echo "  make server         Start the FastAPI server"
	@echo "  make dev            Build, deploy, and start server"
	@echo "  make watch          Watch for changes and auto-rebuild"
	@echo "  make lint           Run ruff linter"
	@echo "  make format         Format code with ruff"
	@echo "  make clean          Remove build artifacts"

# Install dependencies
install:
	uv sync

install-server:
	cd server && uv sync

# Run desktop version
run-desktop:
	uv run python main.py

# Build WASM bundle
build:
	@echo "Preparing clean build directory..."
	rm -rf build/app
	mkdir -p build/app/states build/app/ui
	cp main.py game.py api_client.py constants.py asteroid.py asteroidfield.py circleshape.py player.py shot.py score_repository.py build/app/
	cp states/*.py build/app/states/
	cp ui/*.py build/app/ui/
	cp pyproject.toml build/app/
	@echo "Building with pygbag..."
	cd build/app && uv run pygbag --build main.py
	@echo "Build complete. Output in build/app/build/web/"

# Deploy to server static directory
deploy: build
	rm -rf server/static/game/*
	cp -r build/app/build/web/* server/static/game/

# Start server
server:
	cd server && uv run uvicorn main:app --port 8000 --reload

# Watch for changes and auto-rebuild (uses fswatch on macOS)
# Run in a separate terminal while 'make server' runs in another
watch:
	@echo "Watching for changes... (Press Ctrl+C to stop)"
	@echo "Run 'make server' in another terminal"
	@fswatch -o *.py states/*.py ui/*.py | xargs -n1 -I{} make deploy

# Full dev workflow: build, deploy, start server
dev: deploy server

# Linting
lint:
	uv pip install ruff -q
	uv run ruff check . --exclude .venv

# Format code
format:
	uv pip install ruff -q
	uv run ruff format . --exclude .venv

# Run server tests
test:
	cd server && uv sync --extra dev && uv run pytest -v

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf server/static/game/*
	rm -f .pygbag
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
