"""
Tests for poll endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_poll(client: AsyncClient, auth_headers: dict):
    """Test creating a poll."""
    response = await client.post("/polls", headers=auth_headers, json={
        "title": "Best programming language",
        "options": [
            {"id": "1", "label": "Python"},
            {"id": "2", "label": "JavaScript"},
            {"id": "3", "label": "Rust"},
        ],
    })

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Best programming language"
    assert data["status"] == "draft"
    assert len(data["options"]) == 3


@pytest.mark.asyncio
async def test_create_poll_unauthenticated(client: AsyncClient):
    """Test creating a poll without auth fails."""
    response = await client.post("/polls", json={
        "title": "Test poll",
        "options": [
            {"id": "1", "label": "Option 1"},
            {"id": "2", "label": "Option 2"},
        ],
    })

    # 401 Unauthorized or 403 Forbidden
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_open_poll(client: AsyncClient, auth_headers: dict):
    """Test opening a poll."""
    # Create poll
    create_response = await client.post("/polls", headers=auth_headers, json={
        "title": "Test poll",
        "options": [
            {"id": "1", "label": "A"},
            {"id": "2", "label": "B"},
        ],
    })
    poll_id = create_response.json()["id"]

    # Open poll
    response = await client.post(f"/polls/{poll_id}/open", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "open"


@pytest.mark.asyncio
async def test_vote_on_poll(client: AsyncClient, auth_headers: dict):
    """Test submitting a vote."""
    # Create and open poll
    create_response = await client.post("/polls", headers=auth_headers, json={
        "title": "Vote test",
        "options": [
            {"id": "1", "label": "First"},
            {"id": "2", "label": "Second"},
            {"id": "3", "label": "Third"},
        ],
    })
    poll_id = create_response.json()["id"]
    await client.post(f"/polls/{poll_id}/open", headers=auth_headers)

    # Vote
    response = await client.post(f"/polls/{poll_id}/vote", headers=auth_headers, json={
        "poll_id": poll_id,
        "rankings": [
            {"option_id": "1", "rank": 1},
            {"option_id": "2", "rank": 2},
            {"option_id": "3", "rank": 3},
        ],
    })

    assert response.status_code == 201
    data = response.json()
    assert data["poll_id"] == poll_id


@pytest.mark.asyncio
async def test_cannot_vote_twice(client: AsyncClient, auth_headers: dict):
    """Test that a user cannot vote twice on the same poll."""
    # Create and open poll
    create_response = await client.post("/polls", headers=auth_headers, json={
        "title": "No double vote",
        "options": [
            {"id": "1", "label": "A"},
            {"id": "2", "label": "B"},
        ],
    })
    poll_id = create_response.json()["id"]
    await client.post(f"/polls/{poll_id}/open", headers=auth_headers)

    vote_data = {
        "poll_id": poll_id,
        "rankings": [
            {"option_id": "1", "rank": 1},
            {"option_id": "2", "rank": 2},
        ],
    }

    # First vote
    await client.post(f"/polls/{poll_id}/vote", headers=auth_headers, json=vote_data)

    # Second vote should fail
    response = await client.post(f"/polls/{poll_id}/vote", headers=auth_headers, json=vote_data)

    assert response.status_code == 400
    assert "already voted" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_results(client: AsyncClient, auth_headers: dict):
    """Test getting poll results with Borda count."""
    # Create and open poll
    create_response = await client.post("/polls", headers=auth_headers, json={
        "title": "Results test",
        "options": [
            {"id": "1", "label": "Alpha"},
            {"id": "2", "label": "Beta"},
            {"id": "3", "label": "Gamma"},
        ],
    })
    poll_id = create_response.json()["id"]
    await client.post(f"/polls/{poll_id}/open", headers=auth_headers)

    # Vote (1st place gets 3 points, 2nd gets 2, 3rd gets 1)
    await client.post(f"/polls/{poll_id}/vote", headers=auth_headers, json={
        "poll_id": poll_id,
        "rankings": [
            {"option_id": "1", "rank": 1},  # 3 points
            {"option_id": "2", "rank": 2},  # 2 points
            {"option_id": "3", "rank": 3},  # 1 point
        ],
    })

    # Get results
    response = await client.get(f"/polls/{poll_id}/results")

    assert response.status_code == 200
    data = response.json()
    assert data["total_votes"] == 1
    assert len(data["results"]) == 3

    # Alpha should be first with 3 points
    assert data["results"][0]["label"] == "Alpha"
    assert data["results"][0]["score"] == 3.0
    assert data["results"][0]["rank"] == 1


@pytest.mark.asyncio
async def test_get_poll(client: AsyncClient, auth_headers: dict):
    """Test getting a poll by ID."""
    # Create poll
    create_response = await client.post("/polls", headers=auth_headers, json={
        "title": "Get test",
        "options": [
            {"id": "1", "label": "X"},
            {"id": "2", "label": "Y"},
        ],
    })
    poll_id = create_response.json()["id"]

    # Get poll (no auth required)
    response = await client.get(f"/polls/{poll_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Get test"
