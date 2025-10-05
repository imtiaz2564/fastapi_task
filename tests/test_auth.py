# import pytest
# from httpx import AsyncClient
# from asgi_lifespan import LifespanManager
# from app.main import app
#
# @pytest.mark.asyncio
# async def test_register_and_login():
#     async with LifespanManager(app):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             # Register
#             res = await client.post("/auth/register", json={"username": "user1", "password": "pass"})
#             assert res.status_code in [200, 201]
#             assert res.json()["username"] == "user1"
#
#             # Login
#             res = await client.post("/auth/login", json={"username": "user1", "password": "pass"})
#             data = res.json()
#             assert res.status_code == 200
#             assert "access_token" in data
#             assert data["token_type"] == "bearer"
# tests/test_auth_simple.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_register_success(self, client):
        """Test successful user registration"""
        user_data = {
            "username": "newtestuser",
            "password": "testpassword123"
        }

        response = client.post("/auth/register", json=user_data)
        print(f"Register Response: {response.status_code} - {response.text}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "password" not in data

    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username"""
        user_data = {
            "username": "duplicateuser",
            "password": "password123"
        }

        # First registration
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == status.HTTP_200_OK

        # Second registration
        response2 = client.post("/auth/register", json=user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"].lower()

    def test_register_invalid_data(self, client):
        """Test registration with invalid data"""
        # Missing password
        response = client.post("/auth/register", json={"username": "testuser"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing username
        response = client.post("/auth/register", json={"password": "password123"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client):
        """Test successful login"""
        user_data = {
            "username": "loginuser",
            "password": "loginpass123"
        }

        # Register first
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK

        # Then login
        login_response = client.post("/auth/login", json=user_data)
        print(f"Login Response: {login_response.status_code} - {login_response.text}")

        assert login_response.status_code == status.HTTP_200_OK
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client):
        """Test login with non-existent username"""
        user_data = {
            "username": "nonexistentuser",
            "password": "password123"
        }

        response = client.post("/auth/login", json=user_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client):
        """Test login with wrong password"""
        # Register user first
        user_data = {
            "username": "passworduser",
            "password": "correctpassword"
        }
        client.post("/auth/register", json=user_data)

        # Try login with wrong password
        wrong_data = {
            "username": "passworduser",
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=wrong_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_logout_success(self, client):
        """Test successful logout"""
        # Register and login
        user_data = {
            "username": "logouttestuser",
            "password": "logoutpass123"
        }

        # Register
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK

        # Login
        login_response = client.post("/auth/login", json=user_data)
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]

        # Logout
        logout_response = client.post("/auth/logout", json={"token": token})
        print(f"Logout Response: {logout_response.status_code} - {logout_response.text}")

        assert logout_response.status_code == status.HTTP_200_OK
        assert "success" in logout_response.json()["message"].lower()

    def test_logout_invalid_token(self, client):
        """Test logout with invalid token"""
        response = client.post("/auth/logout", json={"token": "invalid_token_123"})
        print(f"Invalid token logout: {response.status_code} - {response.text}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_logout_missing_token(self, client):
        """Test logout without token"""
        response = client.post("/auth/logout", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_complete_auth_flow(self, client):
        """Test complete authentication flow"""
        user_data = {
            "username": "flowtestuser",
            "password": "flowpass123"
        }

        # Register
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK

        # Login
        login_response = client.post("/auth/login", json=user_data)
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]

        # Logout
        logout_response = client.post("/auth/logout", json={"token": token})
        assert logout_response.status_code == status.HTTP_200_OK


class TestPasswordUtils:
    """Test password utility functions"""

    def test_hash_and_verify_password(self):
        from app.utils import hash_password, verify_password

        password = "testpassword123"
        hashed = hash_password(password)

        # Should not be the same as plain text
        assert hashed != password
        # Should verify correctly
        assert verify_password(password, hashed) is True
        # Should fail with wrong password
        assert verify_password("wrongpassword", hashed) is False


class TestTokenUtils:
    """Test token utility functions"""

    def test_create_access_token(self):
        from app.utils import create_access_token

        data = {"sub": "123"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0