"""Smoke tests for server API endpoints."""

from fastapi.testclient import TestClient


class TestTokenEndpoint:
    """Tests for /api/tokens endpoint."""

    def test_create_token_returns_token(self, client: TestClient) -> None:
        """POST /api/tokens should return a token."""
        response = client.post("/api/tokens")
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0


class TestScoresEndpoint:
    """Tests for /api/scores endpoint."""

    def test_get_scores_empty(self, client: TestClient) -> None:
        """GET /api/scores should return empty list when no scores exist."""
        response = client.get("/api/scores")
        assert response.status_code == 200
        data = response.json()
        assert "scores" in data
        assert data["scores"] == []

    def test_get_scores_with_limit(self, client: TestClient) -> None:
        """GET /api/scores should accept limit parameter."""
        response = client.get("/api/scores?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "scores" in data

    def test_submit_score_requires_token(self, client: TestClient) -> None:
        """POST /api/scores should require authorization."""
        response = client.post(
            "/api/scores", json={"player_name": "Test", "score": 100}
        )
        assert response.status_code == 401

    def test_submit_score_with_valid_token(self, client: TestClient) -> None:
        """POST /api/scores should accept score with valid token."""
        # First get a token
        token_response = client.post("/api/tokens")
        token = token_response.json()["token"]

        # Submit score with token
        response = client.post(
            "/api/scores",
            json={"player_name": "TestPlayer", "score": 1000},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data

    def test_submit_score_token_is_single_use(self, client: TestClient) -> None:
        """Token should only be usable once."""
        # Get a token
        token_response = client.post("/api/tokens")
        token = token_response.json()["token"]

        # First submission should succeed
        response1 = client.post(
            "/api/scores",
            json={"player_name": "Player1", "score": 100},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response1.status_code == 200

        # Second submission with same token should fail
        response2 = client.post(
            "/api/scores",
            json={"player_name": "Player2", "score": 200},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response2.status_code == 401

    def test_submit_score_validates_player_name(self, client: TestClient) -> None:
        """POST /api/scores should reject empty player names."""
        token_response = client.post("/api/tokens")
        token = token_response.json()["token"]

        response = client.post(
            "/api/scores",
            json={"player_name": "", "score": 100},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400

    def test_submit_score_validates_negative_score(self, client: TestClient) -> None:
        """POST /api/scores should reject negative scores."""
        token_response = client.post("/api/tokens")
        token = token_response.json()["token"]

        response = client.post(
            "/api/scores",
            json={"player_name": "Test", "score": -100},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400

    def test_scores_persist_after_submission(self, client: TestClient) -> None:
        """Submitted scores should appear in GET /api/scores."""
        # Submit a score
        token_response = client.post("/api/tokens")
        token = token_response.json()["token"]
        client.post(
            "/api/scores",
            json={"player_name": "HighScorer", "score": 5000},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Verify it appears in scores list
        response = client.get("/api/scores")
        data = response.json()
        assert len(data["scores"]) == 1
        assert data["scores"][0]["player_name"] == "HighScorer"
        assert data["scores"][0]["score"] == 5000


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_response(self, client: TestClient) -> None:
        """GET / should return a response."""
        response = client.get("/")
        # Either serves index.html or returns API message
        assert response.status_code == 200
