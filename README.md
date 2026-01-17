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
   uv run uvicorn main:app --port 8000
   ```
3. Open http://localhost:8000/ in your browser

## Controls

- **Arrow Keys**: Rotate and thrust
- **Space**: Fire
- **Escape**: Pause game

## API Endpoints

- `POST /api/tokens` - Generate submission token
- `GET /api/scores?limit=10` - Get top scores
- `POST /api/scores` - Submit score (requires Bearer token)

## VPS Deployment (Docker)

Deploy to a VPS at `asteroids.***.com` using Docker Compose.

### Initial Deployment

1. SSH into VPS
2. Clone repository:
   ```bash
   cd /opt
   sudo git clone <repo-url> asteroids
   cd asteroids
   ```
3. Build and start:
   ```bash
   sudo docker compose up -d --build
   ```
4. Configure Nginx (see below)
5. Setup SSL with certbot

### Nginx Configuration

Create `/etc/nginx/sites-available/asteroids`:

```nginx
server {
    listen 80;
    server_name asteroids.ilutay.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Then:

```bash
sudo ln -s /etc/nginx/sites-available/asteroids /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d asteroids.***.com
```

### Updates

```bash
cd /opt/asteroids
sudo git pull
sudo docker compose up -d --build
```

### Data Persistence

SQLite database is stored in a Docker volume (`asteroids-data`) and survives container rebuilds.
