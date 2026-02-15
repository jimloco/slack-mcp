"""
Tests for Slack API client wrapper.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from slack_sdk.errors import SlackApiError

from slack_mcp.slack_client import SlackClient, SlackClientError


class TestSlackClient:
    """Tests for SlackClient class."""

    def test_init_valid_token(self) -> None:
        """Test initialization with valid OAuth token."""
        client = SlackClient("xoxp-valid-token")
        assert client.token == "xoxp-valid-token"
        assert client._auth_info is None

    def test_init_invalid_token(self) -> None:
        """Test initialization with invalid OAuth token."""
        with pytest.raises(SlackClientError, match="Invalid OAuth token format"):
            SlackClient("xoxb-bot-token")  # Bot token, not user token

    @pytest.mark.asyncio
    async def test_validate_auth_success(self) -> None:
        """Test successful authentication validation."""
        client = SlackClient("xoxp-test-token")

        mock_response = {
            "ok": True,
            "url": "https://test.slack.com/",
            "team": "Test Team",
            "user": "testuser",
            "team_id": "T12345",
            "user_id": "U12345",
        }

        with patch.object(client.client, "auth_test", new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_response
            result = await client.validate_auth()

        assert result["team"] == "Test Team"
        assert result["user"] == "testuser"
        assert client._auth_info is not None

    @pytest.mark.asyncio
    async def test_validate_auth_failure(self) -> None:
        """Test authentication validation failure."""
        client = SlackClient("xoxp-invalid-token")

        mock_response = {"error": "invalid_auth"}

        with patch.object(client.client, "auth_test", new_callable=AsyncMock) as mock_auth:
            mock_auth.side_effect = SlackApiError("Auth failed", mock_response)

            with pytest.raises(SlackClientError, match="Authentication failed"):
                await client.validate_auth()

    @pytest.mark.asyncio
    async def test_call_api_success(self) -> None:
        """Test successful API call."""
        client = SlackClient("xoxp-test-token")

        mock_response = Mock()
        mock_response.__getitem__ = Mock(return_value=True)
        mock_response.data = {"ok": True, "channel": "C12345"}

        with patch.object(client.client, "conversations_list", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = mock_response
            result = await client.call_api("conversations.list", limit=10)

        assert result["ok"] is True
        assert result["channel"] == "C12345"

    @pytest.mark.asyncio
    async def test_call_api_rate_limited(self) -> None:
        """Test API call with rate limiting."""
        client = SlackClient("xoxp-test-token")

        # Create a mock response that supports both dict access and has headers
        mock_response = Mock()
        mock_response.__getitem__ = Mock(return_value="ratelimited")
        mock_response.get = Mock(return_value="ratelimited")
        mock_response.headers = {"Retry-After": "30"}

        with patch.object(client.client, "chat_postMessage", new_callable=AsyncMock) as mock_api:
            mock_api.side_effect = SlackApiError("Rate limited", mock_response)

            with pytest.raises(SlackClientError, match="Rate limited"):
                await client.call_api("chat.postMessage", channel="C123", text="test")

    @pytest.mark.asyncio
    async def test_call_api_missing_scope(self) -> None:
        """Test API call with missing OAuth scope."""
        client = SlackClient("xoxp-test-token")

        mock_response = {"error": "missing_scope"}

        with patch.object(client.client, "users_list", new_callable=AsyncMock) as mock_api:
            mock_api.side_effect = SlackApiError("Missing scope", mock_response)

            with pytest.raises(SlackClientError, match="Missing required OAuth scope"):
                await client.call_api("users.list")

    def test_get_auth_info_not_validated(self) -> None:
        """Test getting auth info before validation."""
        client = SlackClient("xoxp-test-token")
        assert client.get_auth_info() is None

    @pytest.mark.asyncio
    async def test_get_auth_info_after_validation(self) -> None:
        """Test getting auth info after validation."""
        client = SlackClient("xoxp-test-token")

        mock_response = {
            "ok": True,
            "team": "Test Team",
            "user": "testuser",
            "team_id": "T12345",
            "user_id": "U12345",
        }

        with patch.object(client.client, "auth_test", new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_response
            await client.validate_auth()

        auth_info = client.get_auth_info()
        assert auth_info is not None
        assert auth_info["team"] == "Test Team"
