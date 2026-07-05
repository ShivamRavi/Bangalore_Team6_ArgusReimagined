import pytest
from datetime import timedelta
from httpx import AsyncClient

from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_register_student_success(client: AsyncClient):
    """Test successful student registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "2122ES111265",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """Test registering a user with a duplicate username."""
    # Register first user
    response1 = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_user",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1
        }
    )
    assert response1.status_code == 201
    
    # Register second user with same username
    response2 = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_user",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1
        }
    )
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Username already registered"

@pytest.mark.asyncio
async def test_register_student_missing_house_section(client: AsyncClient):
    """Test student registration validation errors for house/section."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "missing_fields_student",
            "password": "password123",
            "role": "STUDENT"
        }
    )
    assert response.status_code == 422
    # Pydantic raises validation errors

@pytest.mark.asyncio
async def test_register_student_invalid_house(client: AsyncClient):
    """Test registration when student house ID does not exist in DB."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "invalid_house_student",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 999, # Non-existent ID
            "section_id": 1
        }
    )
    assert response.status_code == 400
    assert "House with ID 999 does not exist" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register a user
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_user",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1
        }
    )
    
    # Login via OAuth2 Form URL Encoded
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "login_user",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with incorrect password."""
    # Register a user
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "wrong_pwd_user",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1
        }
    )
    
    # Login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong_pwd_user",
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_login_non_existent_user(client: AsyncClient):
    """Test login with a non-existent username."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "nobody_exists",
            "password": "password123"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient):
    """Test retrieving authenticated user profile."""
    # Register user
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "profile_user",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1
        }
    )
    assert reg_response.status_code == 201
    token = reg_response.json()["access_token"]
    
    # Get Profile
    profile_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_response.status_code == 200
    data = profile_response.json()
    assert data["username"] == "profile_user"
    assert data["role"] == "STUDENT"
    assert data["house_name"] == "Poseidon"
    assert data["section_name"] == "Grade 12-A"
    assert data["euros_balance"] == 0
    assert data["current_planet"] == "Mercury"

@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    """Test profile access without auth token."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_expired_token(client: AsyncClient):
    """Test profile access with an expired access token."""
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "expired_token_user",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1,
        },
    )
    assert reg_response.status_code == 201
    from jose import jwt
    from app.config import settings

    payload = jwt.decode(
        reg_response.json()["access_token"],
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_exp": False},
    )
    expired_token = create_access_token(
        subject=payload["sub"],
        expires_delta=timedelta(minutes=-1),
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    """Test refresh token rotation flow."""
    # Register user
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "refresh_user",
            "password": "password123",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1
        }
    )
    assert reg_response.status_code == 201
    refresh_token = reg_response.json()["refresh_token"]
    
    # Refresh
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """Test refresh endpoint with invalid refresh token."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not-a-valid-token"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_otp_login_stub(client: AsyncClient):
    """Test OTP login returns 501 Not Implemented."""
    response = await client.post("/api/v1/auth/otp-login")
    assert response.status_code == 501
    assert "OTP Login is not implemented yet" in response.json()["detail"]
