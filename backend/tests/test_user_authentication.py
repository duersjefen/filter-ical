"""
Integration tests for user authentication flows.
Tests registration, login, JWT validation, and account lockout.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.services.auth_service import create_jwt_token


@pytest.mark.integration
class TestUserRegistration:
    """Integration tests for user registration endpoint."""

    def test_register_with_username_and_password(self, test_client: TestClient, test_db: Session):
        """Test user can register with username and password."""
        response = test_client.post(
            "/api/users/register",
            json={
                "username": "testuser123",
                "password": "securepass123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "testuser123"
        assert data["user"]["email"] == "test@example.com"
        assert "token" in data
        assert data["expires_in_days"] == 30

        # Verify user exists in database with hashed password
        user = test_db.query(User).filter(User.username == "testuser123").first()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.password_hash is not None
        assert user.password_hash != "securepass123"  # Should be hashed

    def test_register_username_only(self, test_client: TestClient, test_db: Session):
        """Test username-only registration creates account without password."""
        response = test_client.post(
            "/api/users/register",
            json={"username": "insecureuser"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "insecureuser"
        assert data["user"]["has_password"] is False
        assert "token" in data

        # Verify user has no password
        user = test_db.query(User).filter(User.username == "insecureuser").first()
        assert user is not None
        assert user.password_hash is None or user.password_hash == ""

    def test_register_duplicate_username_fails(self, test_client: TestClient):
        """Test duplicate username registration is rejected."""
        # Create first user
        test_client.post(
            "/api/users/register",
            json={"username": "duplicate", "password": "pass123", "email": "duplicate@example.com"}
        )

        # Try to create duplicate
        response = test_client.post(
            "/api/users/register",
            json={"username": "duplicate", "password": "otherpass", "email": "other@example.com"}
        )
        assert response.status_code in [400, 409]
        assert "already" in response.json()["detail"].lower() or "exists" in response.json()["detail"].lower() or "taken" in response.json()["detail"].lower()

    def test_register_password_requires_email(self, test_client: TestClient):
        """Test that providing password requires email (for password reset)."""
        response = test_client.post(
            "/api/users/register",
            json={
                "username": "passnomail",
                "password": "securepass123"
            }
        )
        # Should fail - password requires email for reset functionality
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()


@pytest.mark.integration
class TestUserLogin:
    """Integration tests for user login endpoint."""

    def test_login_with_valid_credentials(self, test_client: TestClient):
        """Test successful login returns JWT token."""
        # Register user first
        test_client.post(
            "/api/users/register",
            json={"username": "loginuser", "password": "mypassword123", "email": "login@example.com"}
        )

        # Login
        response = test_client.post(
            "/api/users/login",
            json={"username": "loginuser", "password": "mypassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["username"] == "loginuser"
        assert data["expires_in_days"] == 30

    def test_login_with_invalid_password(self, test_client: TestClient):
        """Test invalid password returns 401."""
        # Register user
        test_client.post(
            "/api/users/register",
            json={"username": "secureuser", "password": "correctpass", "email": "secure@example.com"}
        )

        # Try wrong password
        response = test_client.post(
            "/api/users/login",
            json={"username": "secureuser", "password": "wrongpass"}
        )
        assert response.status_code == 401

    def test_login_username_only_account(self, test_client: TestClient):
        """Test username-only accounts can login without password."""
        # Register username-only account
        test_client.post(
            "/api/users/register",
            json={"username": "nopassuser"}
        )

        # Login without password
        response = test_client.post(
            "/api/users/login",
            json={"username": "nopassuser"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["has_password"] is False

    def test_login_nonexistent_user(self, test_client: TestClient):
        """Test login with nonexistent username fails."""
        response = test_client.post(
            "/api/users/login",
            json={"username": "doesnotexist", "password": "anything"}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestJWTTokenValidation:
    """Integration tests for JWT token validation."""

    def test_valid_token_grants_access(self, test_client: TestClient):
        """Test valid JWT token grants access to protected endpoints."""
        # Register and get token
        response = test_client.post(
            "/api/users/register",
            json={"username": "tokenuser", "password": "pass123", "email": "token@example.com"}
        )
        token = response.json()["token"]

        # Access protected endpoint
        response = test_client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "tokenuser"

    def test_missing_token_denies_access(self, test_client: TestClient):
        """Test missing token returns 401."""
        response = test_client.get("/api/users/me")
        assert response.status_code == 401

    def test_invalid_token_denies_access(self, test_client: TestClient):
        """Test invalid/tampered token returns 401."""
        response = test_client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    def test_expired_token_denies_access(self, test_client: TestClient, test_db: Session):
        """Test expired JWT token is rejected."""
        # Create user
        response = test_client.post(
            "/api/users/register",
            json={"username": "expireduser", "password": "pass123", "email": "expired@example.com"}
        )
        user_data = response.json()

        # Get user from database to get user_id
        user = test_db.query(User).filter(User.username == "expireduser").first()
        assert user is not None

        # Create expired token manually using JWT
        import jwt
        from app.core.config import settings
        from datetime import timezone

        now = datetime.now(timezone.utc)
        expired_time = now - timedelta(days=1)  # Expired yesterday

        payload = {
            'user_id': user.id,
            'iat': expired_time.timestamp(),
            'exp': expired_time.timestamp()  # Already expired
        }

        expired_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        # Try to use expired token
        response = test_client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestAccountSecurity:
    """Integration tests for account security features."""

    def test_account_lockout_after_failed_attempts(self, test_client: TestClient):
        """Test account lockout after 5 failed login attempts."""
        # Register user
        test_client.post(
            "/api/users/register",
            json={"username": "lockoutuser", "password": "correctpass", "email": "lockout@example.com"}
        )

        # Make 5 failed login attempts
        for i in range(5):
            response = test_client.post(
                "/api/users/login",
                json={"username": "lockoutuser", "password": "wrongpass"}
            )
            # First 4 should return 401, 5th triggers lockout (403)
            assert response.status_code in [401, 403]

        # 6th attempt should be locked out (403 Forbidden)
        response = test_client.post(
            "/api/users/login",
            json={"username": "lockoutuser", "password": "wrongpass"}
        )
        # Should be account locked
        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()

    def test_username_check_endpoint(self, test_client: TestClient):
        """Test username availability check endpoint."""
        # Register user with password
        test_client.post(
            "/api/users/register",
            json={"username": "taken", "password": "pass", "email": "taken@example.com"}
        )

        # Check taken username - should return exists=True and has_password=True
        response = test_client.get("/api/users/check/taken")
        assert response.status_code == 200
        data = response.json()
        assert data["exists"] is True
        assert data["has_password"] is True
        assert data["username"] == "taken"

        # Check available username - should return 404 Not Found
        response = test_client.get("/api/users/check/available")
        assert response.status_code == 404
