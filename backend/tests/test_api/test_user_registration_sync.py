"""
Tests for Clerk user registration sync behaviour.
"""

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.clerk_auth import TokenData, clerk_auth


@pytest.mark.asyncio
async def test_unverified_users_are_blocked(monkeypatch):
    """Ensure Clerk rejects users whose email is not verified."""
    fake_credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="fake-token",
    )

    token_payload = TokenData(
        sub="user_123",
        iat=0,
        exp=0,
        email="user@example.com",
        email_verified=False,
    )

    async def mock_verify_token(token: str) -> TokenData:  # pragma: no cover - simple patch
        return token_payload

    monkeypatch.setattr(clerk_auth, "verify_token", mock_verify_token)

    with pytest.raises(HTTPException) as exc:
        await clerk_auth.get_current_user(fake_credentials)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "not verified" in exc.value.detail.lower()
