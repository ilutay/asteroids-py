# Asteroids

A classic Asteroids game built with Pygame, featuring web support via pygame-web and a shared high scores backend.

## Project Structure

```
asteroids-py/
├── main.py                 # Game entry point (async for web compatibility)
├── game.py                 # Main game controller & state machine
├── states/                 # Game states (menu, playing, game over, etc.)
├── database/               # Storage abstraction (local SQLite or remote API)
├── utils/                  # Platform detection utilities
├── server/                 # FastAPI backend for high scores
│   ├── main.py             # API endpoints
│   ├── database.py         # SQLite operations
│   ├── models.py           # Pydantic schemas
│   ├── config.py           # Environment configuration
│   ├── Dockerfile
│   └── pyproject.toml
├── docker-compose.yml      # Production deployment
└── .env.example            # Configuration template
```

## Running Locally

### Desktop Game

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Run the game:
   ```bash
   uv run python main.py
   ```

By default, the game uses local SQLite storage (`./data/asteroids.db`).

### Using Remote API (Optional)

To use the remote high scores API instead of local storage:

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Configure `.env`:

   ```env
   API_URL=https://your-domain.com/api
   API_KEY=your-secret-key
   USE_REMOTE_API=true
   ```

3. Run the game as normal.

## Running the Server

### Local Development

1. Navigate to server directory:

   ```bash
   cd server
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Start the server:

   ```bash
   API_KEY=your-secret-key uv run uvicorn main:app --reload --port 8000
   ```

4. The API is now available at `http://localhost:8000`

### API Endpoints

| Method | Path          | Auth    | Description        |
| ------ | ------------- | ------- | ------------------ |
| GET    | `/health`     | None    | Health check       |
| GET    | `/api/scores` | None    | Get top 10 scores  |
| POST   | `/api/scores` | API Key | Submit a new score |

#### Example Requests

```bash
# Health check
curl http://localhost:8000/health

# Get high scores
curl http://localhost:8000/api/scores

# Submit a score (requires API key)
curl -X POST http://localhost:8000/api/scores \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"player_name": "AAA", "score": 50000}'
```

## Testing

### Test Server Endpoints

1. Start the server (see above)

2. Run endpoint tests:

   ```bash
   # Health check
   curl -s http://localhost:8000/health
   # Expected: {"status":"healthy"}

   # Get scores (empty initially)
   curl -s http://localhost:8000/api/scores
   # Expected: {"scores":[]}

   # Submit without API key (should fail)
   curl -s -X POST http://localhost:8000/api/scores \
     -H "Content-Type: application/json" \
     -d '{"player_name": "TEST", "score": 1000}'
   # Expected: {"detail":"Invalid or missing API key"}

   # Submit with API key (should succeed)
   curl -s -X POST http://localhost:8000/api/scores \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secret-key" \
     -d '{"player_name": "TEST", "score": 1000}'
   # Expected: {"id":1,"message":"Score submitted successfully"}

   # Verify score was saved
   curl -s http://localhost:8000/api/scores
   # Expected: {"scores":[{"id":1,"player_name":"TEST","score":1000,...}]}
   ```

### Test Checklist

- [ ] `GET /health` returns healthy status
- [ ] `GET /api/scores` returns empty list initially
- [ ] `POST /api/scores` without API key returns 401
- [ ] `POST /api/scores` with valid API key succeeds
- [ ] Desktop game works with `USE_REMOTE_API=false` (local SQLite)
- [ ] Desktop game works with `USE_REMOTE_API=true` (hits server)

## Linting & Type Checking

The project uses [ruff](https://docs.astral.sh/ruff/) for linting/formatting and [mypy](https://mypy.readthedocs.io/) for type checking.

### Install Dev Dependencies

```bash
uv sync --group dev
```

### Run Linter

```bash
# Check for errors
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix
```

### Format Code

```bash
# Format all files
uv run ruff format .

# Check formatting without changing files
uv run ruff format --check .
```

### Type Checking

```bash
uv run mypy .
```

### Server Linting

The server has its own pyproject.toml with the same configuration:

```bash
cd server
uv sync --group dev
uv run ruff check .
uv run mypy .
```

## Deployment

### Prerequisites

- A VPS with Ubuntu 22.04+ (or similar Linux distribution)
- Docker and Docker Compose installed
- A domain name (optional, for HTTPS)

### Step 1: Provision VPS

```bash
ssh root@your-vps-ip
```

### Step 2: Install Docker

```bash
curl -fsSL https://get.docker.com | sh
```

### Step 3: Create Project Directory

```bash
mkdir -p /opt/asteroids
cd /opt/asteroids
```

### Step 4: Copy Server Files

From your local machine:

```bash
scp -r server docker-compose.yml root@your-vps-ip:/opt/asteroids/
```

Or clone from git:

```bash
git clone git@github.com:ilutay/asteroids-py.git /opt/asteroids
```

### Step 5: Configure Environment

Generate a secure API key and create `.env`:

```bash
cd /opt/asteroids
echo "API_KEY=$(openssl rand -hex 32)" > .env
cat .env  # Save this key for your game clients
```

### Step 6: Create Data Directory

```bash
mkdir -p /opt/asteroids/data
```

### Step 7: Build and Start Services

```bash
docker-compose up -d --build
docker-compose up -d

```

### Step 8: Verify Deployment

```bash
# Check container is running
docker compose ps

# Check logs
docker-compose logs -f

# Test health endpoint
curl http://localhost:8000/health

# Test scores endpoint
curl http://localhost:8000/api/scores
```

### Step 9: Configure Firewall (Optional)

If using UFW:

```bash
ufw allow 8000/tcp  # Or 80/443 if using nginx
ufw enable
```

### Step 10: Set Up Nginx + HTTPS (Recommended for Production)

1. Install Nginx and Certbot:

   ```bash
   apt update
   apt install -y nginx certbot python3-certbot-nginx
   ```

2. Create Nginx configuration:

   ```bash
   cat > /etc/nginx/sites-available/asteroids << 'EOF'
   server {
       listen 80;
       server_name asteroids.ilutay.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   EOF
   ```

3. Enable the site:

   ```bash
   ln -s /etc/nginx/sites-available/asteroids /etc/nginx/sites-enabled/
   nginx -t
   systemctl reload nginx
   ```

4. Obtain SSL certificate:

   ```bash
   certbot --nginx -d asteroids.ilutay.com
   ```

5. Certbot will automatically configure HTTPS and set up auto-renewal.

### Step 11: Deploy Web Build (Optional)

To serve the pygame-web version:

1. Build locally:

# Install pygbag

uv pip install pygbag

```

# Build for web (creates build/web folder)

uv run pygbag --build main.py

```

2. Copy build to VPS:

```bash
scp -r build/web/* root@your-vps-ip:/opt/asteroids/static/
```

3. The web game will be served at `https://your-domain.com/`

### Updating the Deployment

```bash
cd /opt/asteroids

# Pull latest changes (if using git)
git pull

# Rebuild and restart
docker compose up -d --build

# Check logs for errors
docker compose logs -f
```

### Troubleshooting

**Container won't start:**

```bash
docker-compose logs api
```

**Database permission issues:**

```bash
chmod 755 /opt/asteroids/data
```

**API key not working:**

```bash
# Verify .env is loaded
docker-compose exec api env | grep API_KEY
```

**Port already in use:**

```bash
# Find what's using port 8000
lsof -i :8000
# Or change the port in docker-compose.yml
```
