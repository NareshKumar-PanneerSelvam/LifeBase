import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.models.user import User

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Verifies that the GET /api/v1/health check works and returns a correct structure."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "healthy"
    assert json_data["data"]["database"] == "healthy"

@pytest.mark.asyncio
async def test_complete_auth_flow(client: AsyncClient, db: AsyncSession) -> None:
    """Verifies register, login, profile query, unauthorized blocks, admin blocks,
    token rotation, invalidation reuse mitigation, and final session logout.
    """
    # ---------------------------------------------------------
    # 1. Register user (should auto-login and return AuthResponse)
    # ---------------------------------------------------------
    register_payload = {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
        "role": "USER",
    }
    response = await client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["user"]["email"] == "test@example.com"
    assert "password" not in res_data["data"]["user"]
    assert "access_token" in res_data["data"]
    assert "refresh_token" in res_data["data"]

    # ---------------------------------------------------------
    # 2. Login user (returns AuthResponse)
    # ---------------------------------------------------------
    login_payload = {
        "email": "test@example.com",
        "password": "securepassword123",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    auth_data = res_data["data"]
    assert "access_token" in auth_data
    assert "refresh_token" in auth_data
    assert auth_data["token_type"] == "bearer"
    assert auth_data["user"]["email"] == "test@example.com"

    access_token = auth_data["access_token"]
    refresh_token = auth_data["refresh_token"]

    # ---------------------------------------------------------
    # 3. Access protected GET /users/me
    # ---------------------------------------------------------
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["email"] == "test@example.com"

    # ---------------------------------------------------------
    # 4. Access protected GET /users/me without credentials
    # ---------------------------------------------------------
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401

    # ---------------------------------------------------------
    # 5. Access admin-only route as regular user (should get 403)
    # ---------------------------------------------------------
    response = await client.get("/api/v1/users/admin-only", headers=headers)
    assert response.status_code == 403

    # ---------------------------------------------------------
    # 6. Rotate refresh token
    # ---------------------------------------------------------
    rotate_payload = {"refresh_token": refresh_token}
    response = await client.post("/api/v1/auth/refresh", json=rotate_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    new_tokens = res_data["data"]
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    new_refresh_token = new_tokens["refresh_token"]

    # ---------------------------------------------------------
    # 7. Breach Mitigation: Reuse old refresh token (should fail)
    # ---------------------------------------------------------
    response = await client.post("/api/v1/auth/refresh", json=rotate_payload)
    assert response.status_code == 401

    # ---------------------------------------------------------
    # 8. Logout session
    # ---------------------------------------------------------
    logout_payload = {"refresh_token": new_refresh_token}
    response = await client.post("/api/v1/auth/logout", json=logout_payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # ---------------------------------------------------------
    # 9. Verify logged out token rotation fails
    # ---------------------------------------------------------
    response = await client.post("/api/v1/auth/refresh", json=logout_payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_role_authorization(client: AsyncClient, db: AsyncSession) -> None:
    """Verifies that only users with the 'ADMIN' role can bypass admin gates."""
    # Insert an administrator directly into DB
    admin_user = User(
        email="admin@example.com",
        password_hash=hash_password("adminpassword123"),
        full_name="Admin Power",
        role="ADMIN",
        is_active=True,
    )
    db.add(admin_user)
    await db.commit()

    # Login as admin
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpassword123",
    })
    assert response.status_code == 200
    tokens = response.json()["data"]
    admin_access_token = tokens["access_token"]

    # Request admin route
    headers = {"Authorization": f"Bearer {admin_access_token}"}
    response = await client.get("/api/v1/users/admin-only", headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert "bypassed" in res_data["data"]["message"]
    assert res_data["data"]["role"] == "ADMIN"
