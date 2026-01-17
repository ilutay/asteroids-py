import logging
import sys
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Browser uses relative URL (served from same origin)
# Desktop needs full URL for local server
BROWSER_API_URL = "/api"
DESKTOP_API_URL = "http://localhost:8000/api"


def _is_browser() -> bool:
    """Check if running in browser (pygbag/WASM) at runtime."""
    return sys.platform == "emscripten"


def _log(msg: str) -> None:
    """Log message - print for browser (shows in console), logging for desktop."""
    if _is_browser():
        print(f"[API] {msg}")
    else:
        _log(msg)


def _get_api_base_url() -> str:
    """Return appropriate API URL based on platform."""
    return BROWSER_API_URL if _is_browser() else DESKTOP_API_URL


@dataclass
class HighScore:
    id: int
    player_name: str
    score: int
    played_at: str


class APIClient:
    """Async HTTP client for high scores API with platform detection."""

    def __init__(self):
        self._token: Optional[str] = None
        _log(f"APIClient initialized, is_browser={_is_browser()}, base_url={_get_api_base_url()}")

    async def _fetch_json(
        self, method: str, path: str, data: Optional[dict] = None
    ) -> dict:
        """Make HTTP request and return JSON response."""
        base_url = _get_api_base_url()
        url = f"{base_url}{path}"
        _log(f"API request: {method} {url}")

        if _is_browser():
            return await self._browser_fetch(method, url, data)
        else:
            return await self._desktop_fetch(method, url, data)

    async def _browser_fetch(
        self, method: str, url: str, data: Optional[dict] = None
    ) -> dict:
        """Use JavaScript fetch for pygbag HTTP requests."""
        try:
            import json
            import platform as platform_module

            # Access JavaScript globals via platform module
            window = platform_module.window

            js_headers = {"Content-Type": "application/json"}
            if self._token:
                js_headers["Authorization"] = f"Bearer {self._token}"

            # Build fetch options as JS object
            options_dict = {
                "method": method,
                "headers": js_headers,
            }
            if data is not None:
                options_dict["body"] = json.dumps(data)

            # Convert Python dict to JS object
            options = window.JSON.parse(json.dumps(options_dict))

            # Use pygbag's ffi.JsProxy for proper promise handling
            from platform import ffi

            # Call fetch and properly await the JS promise
            response = await ffi.proxy(window.fetch(url, options))

            if response.status >= 400:
                _log(f"Browser fetch failed with status {response.status}")
                return {}

            # Await the JSON promise
            json_data = await ffi.proxy(response.json())

            # Convert JS object to Python dict
            return json.loads(window.JSON.stringify(json_data))
        except Exception as e:
            _log(f"Browser fetch error: {e}")
            return {}

    async def _desktop_fetch(
        self, method: str, url: str, data: Optional[dict] = None
    ) -> dict:
        """Use aiohttp for desktop testing."""
        import aiohttp

        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        async with aiohttp.ClientSession() as session:
            try:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            _log(f"GET {url} failed with status {response.status}")
                            return {}
                        result = await response.json()
                        _log(f"GET {url} success: {result}")
                        return result
                elif method == "POST":
                    async with session.post(
                        url, json=data, headers=headers
                    ) as response:
                        if response.status not in (200, 201):
                            text = await response.text()
                            _log(f"POST {url} failed with status {response.status}: {text}")
                            return {}
                        result = await response.json()
                        _log(f"POST {url} success: {result}")
                        return result
            except aiohttp.ClientError as e:
                _log(f"HTTP client error for {method} {url}: {e}")
                return {}

        return {}

    async def _get_token(self) -> Optional[str]:
        """Get a submission token from the server."""
        result = await self._fetch_json("POST", "/tokens")
        token = result.get("token")
        if token:
            _log("Got submission token")
        else:
            _log("Failed to get submission token")
        return token

    async def get_highest_score(self) -> int:
        """Return the highest score, or 0 if none exist."""
        result = await self._fetch_json("GET", "/scores?limit=1")
        scores = result.get("scores", [])
        if scores:
            return scores[0].get("score", 0)
        return 0

    async def get_top_scores(self, limit: int = 10) -> list[HighScore]:
        """Retrieve top N scores."""
        _log(f"Fetching top {limit} scores")
        result = await self._fetch_json("GET", f"/scores?limit={limit}")
        scores = result.get("scores", [])
        _log(f"Got {len(scores)} scores")
        return [
            HighScore(
                id=s.get("id", 0),
                player_name=s.get("player_name", ""),
                score=s.get("score", 0),
                played_at=s.get("played_at", ""),
            )
            for s in scores
        ]

    async def is_high_score(self, score: int) -> bool:
        """Check if score qualifies for top 10."""
        if score == 0:
            return False
        result = await self._fetch_json("GET", "/scores?limit=10")
        scores = result.get("scores", [])
        if len(scores) < 10:
            return True
        # Check if this score beats any in top 10
        lowest_top_score = min(s.get("score", 0) for s in scores)
        return score > lowest_top_score

    async def save_score(self, player_name: str, score: int) -> Optional[int]:
        """Submit a new high score. Returns the new row ID or None on failure."""
        _log(f"Saving score: player={player_name}, score={score}")

        # Get a token first
        self._token = await self._get_token()
        if not self._token:
            _log("Cannot save score: failed to get token")
            return None

        result = await self._fetch_json(
            "POST",
            "/scores",
            {"player_name": player_name, "score": score},
        )
        self._token = None  # Token is single-use

        row_id = result.get("id")
        if row_id:
            _log(f"Score saved successfully with id={row_id}")
        else:
            _log(f"Failed to save score: {result}")
        return row_id
