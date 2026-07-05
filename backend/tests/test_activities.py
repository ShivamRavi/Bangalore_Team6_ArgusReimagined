import pytest
from httpx import AsyncClient
import asyncio

@pytest.mark.asyncio
async def test_worksheet_earns_10_euros(client: AsyncClient):
    """Test that completing a worksheet awards 10 euros."""
    # Register and login user
    user_data = {"username": "worksheet_user", "password": "securepass123"}
    resp = await client.post("/api/v1/auth/register", json=user_data)
    assert resp.status_code == 201
    
    resp = await client.post("/api/v1/auth/login", data=user_data)
    assert resp.status_code == 200
    tokens = resp.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # Get initial balance
    resp = await client.get("/api/v1/users/me", headers=headers)
    initial_balance = resp.json()["euros_balance"]
    
    # Complete worksheet activity
    activity_data = {
        "resource_id": "123e4567-e89b-12d3-a456-426614174000",
        "activity_type": "worksheet"
    }
    resp = await client.post("/api/v1/activities/complete", json=activity_data, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["euros_awarded"] == 10
    
    # Check balance increased by 10
    resp = await client.get("/api/v1/users/me", headers=headers)
    final_balance = resp.json()["euros_balance"]
    assert final_balance == initial_balance + 10
