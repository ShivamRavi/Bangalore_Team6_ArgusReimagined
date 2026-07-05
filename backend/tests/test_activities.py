import pytest

@pytest.mark.asyncio
async def test_video_distracted_earns_2_euros(client: AsyncClient, db):
    """Test that distracted video (completed, >3 interruptions) awards 2 euros."""
    # Register and login user
    user_data = {"username": "videodist_user", "password": "securepass123"}
    resp = await client.post("/auth/register", json=user_data)
    resp = await client.post("/auth/login", json=user_data)
    tokens = resp.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    resp = await client.get("/users/me", headers=headers)
    initial_balance = resp.json()["euros_balance"]
    activity_data = {
        "resource_id": "550e8400-e29b-41d4-a716-446655440001",
        "activity_type": "video",
        "completed": true,
        "focus_interruptions": 5
    }
    resp = await client.post("/activities/complete", json=activity_data, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["euros_awarded"] == 2
    resp = await client.get("/users/me", headers=headers)
    final_balance = resp.json()["euros_balance"]
    assert final_balance == initial_balance + 2

@pytest.mark.asyncio
async def test_activity_idempotency(client: AsyncClient, db):
    """Test that duplicate activity requests are idempotent."""
    # Register and login user
    user_data = {"username": "idempotent_user", "password": "securepass123"}
    reg_response = await client.post("/api/v1/auth/register", json=user_data)
    login_response = await client.post("/api/v1/auth/login", data=user_data)
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    # Get initial balance
    balance_resp = await client.get("/api/v1/users/me", headers=headers)
    initial_balance = balance_resp.json()["euros_balance"]
    # Activity completion data
    activity_data = {
        "resource_id": "123e4567-e89b-12d3-a456-426614174000",
        "activity_type": "worksheet",
    }
    # First request
    response1 = await client.post("/api/v1/activities/complete", json=activity_data, headers=headers)
    assert response1.status_code == 200
    data1 = response1.json()
    # Second identical request
    response2 = await client.post("/api/v1/activities/complete", json=activity_data, headers=headers)
    assert response2.status_code == 200
    data2 = response2.json()
    # Should return same record (idempotent)
    assert data1["id"] == data2["id"]

@pytest.mark.asyncio
async def test_concurrent_activity_requests_no_double_spending(client: AsyncClient, db):
    """Test that concurrent requests for same activity do not result in double-spending."""
    # Register and login user
    user_data = {"username": "concurrent_user", "password": "securepass123"}
    reg_response = await client.post("/api/v1/auth/register", json=user_data)
    login_response = await client.post("/api/v1/auth/login", data=user_data)
    tokens = login_response.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me_response = await client.get("/api/v1/users/me", headers=headers)
    initial_balance = me_response.json()["euros_balance"]
    activity_data = {
        "resource_id": "550e8400-e29b-41d4-a716-446655440001",
        "activity_type": "worksheet",
    }
    # Make 5 concurrent requests for the same activity
    tasks = [client.post("/activities/complete", json=activity_data, headers=headers) for _ in range(5)]
    responses = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in responses)
    data_list = [r.json() for r in responses]
    first_id = data_list[0]["id"]
    assert all(d["id"] == first_id for d in data_list)
    assert all(d["euros_awarded"] == 10 for d in data_list)
    # Check final balance - should only be increased by 10 euros (not 50) proving no double-spending
    balance_resp = await client.get("/api/v1/users/me", headers=headers)
    final_balance = balance_resp.json()["euros_balance"]
    # Key assertion: despite 5 concurrent requests, balance should only increase by 10 euros
    assert final_balance == initial_balance + 10

@pytest.mark.asyncio
async def test_mixed_activities(client: AsyncClient, db):
    """Test completing different activity types and verify correct euro awards."""
    # Register and login user
    user_data = {"username": "mixed_user", "password": "securepass123"}
    resp = await client.post("/api/v1/auth/register", json=user_data)
    resp = await client.post("/api/v1/auth/login", data=user_data)
    tokens = resp.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    # Get initial balance
    resp = await client.get("/api/v1/users/me", headers=headers)
    initial_balance = resp.json()["euros_balance"]

    # Complete various activities
    activity_data = {
        "resource_id": "11111111-1111-1111-1111-111111111111",
        "activity_type": "worksheet",
    }
    resp = await client.post("/api/v1/activities/complete", json=activity_data, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    data = resp.json()
    assert data["euros_awarded"] == 10

    activity_data = {
        "resource_id": "22222222-2222-2222-2222-222222222222",
        "activity_type": "podcast",
        "foreground_time_seconds": 200,
    }
    resp = await client.post("/activities/complete", json=activity_data, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
