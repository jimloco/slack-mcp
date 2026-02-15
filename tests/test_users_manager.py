"""
Tests for Slack users manager.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from slack_mcp.slack_client import SlackClient, SlackClientError
from slack_mcp.users_manager import UsersManager


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock Slack client."""
    client = Mock(spec=SlackClient)
    client.call_api = AsyncMock()
    return client


@pytest.fixture
def users_manager(mock_client: Mock) -> UsersManager:
    """Create UsersManager with mock client."""
    return UsersManager(mock_client)


class TestUsersManager:
    """Tests for UsersManager class."""

    @pytest.mark.asyncio
    async def test_list_users_success(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test successful user listing."""
        mock_client.call_api.return_value = {
            "members": [
                {"id": "U123", "name": "user1", "is_bot": False, "deleted": False},
                {"id": "U456", "name": "user2", "is_bot": False, "deleted": False},
            ],
            "response_metadata": {},
        }

        results = await users_manager.list_users(limit=100)

        assert len(results) == 2
        assert results[0]["name"] == "user1"
        mock_client.call_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_users_filters_bots(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test that bots are filtered out."""
        mock_client.call_api.return_value = {
            "members": [
                {"id": "U123", "name": "user1", "is_bot": False, "deleted": False},
                {"id": "B456", "name": "bot1", "is_bot": True, "deleted": False},
                {"id": "U789", "name": "user2", "is_bot": False, "deleted": False},
            ],
            "response_metadata": {},
        }

        results = await users_manager.list_users(limit=100)

        assert len(results) == 2
        assert all(not u.get("is_bot", False) for u in results)

    @pytest.mark.asyncio
    async def test_list_users_filters_deleted(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test that deleted users are filtered out."""
        mock_client.call_api.return_value = {
            "members": [
                {"id": "U123", "name": "user1", "is_bot": False, "deleted": False},
                {"id": "U456", "name": "deleted1", "is_bot": False, "deleted": True},
                {"id": "U789", "name": "user2", "is_bot": False, "deleted": False},
            ],
            "response_metadata": {},
        }

        results = await users_manager.list_users(limit=100)

        assert len(results) == 2
        assert all(not u.get("deleted", False) for u in results)

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test user listing with pagination."""
        mock_client.call_api.side_effect = [
            {
                "members": [
                    {"id": "U1", "name": "user1", "is_bot": False, "deleted": False}
                ],
                "response_metadata": {"next_cursor": "abc123"},
            },
            {
                "members": [
                    {"id": "U2", "name": "user2", "is_bot": False, "deleted": False}
                ],
                "response_metadata": {},
            },
        ]

        results = await users_manager.list_users(limit=100)

        assert len(results) == 2
        assert mock_client.call_api.call_count == 2

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test successful user lookup by ID."""
        mock_client.call_api.return_value = {
            "user": {"id": "U123", "name": "testuser", "real_name": "Test User"}
        }

        result = await users_manager.get_user(user_id="U123")

        assert result["id"] == "U123"
        assert result["name"] == "testuser"
        mock_client.call_api.assert_called_once_with("users.info", user="U123")

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test successful user lookup by email."""
        mock_client.call_api.return_value = {
            "user": {
                "id": "U123",
                "name": "testuser",
                "profile": {"email": "test@example.com"},
            }
        }

        result = await users_manager.get_user(email="test@example.com")

        assert result["id"] == "U123"
        mock_client.call_api.assert_called_once_with(
            "users.lookupByEmail", email="test@example.com"
        )

    @pytest.mark.asyncio
    async def test_get_user_no_params(self, users_manager: UsersManager) -> None:
        """Test get_user with neither ID nor email."""
        with pytest.raises(SlackClientError, match="Either user_id or email is required"):
            await users_manager.get_user()

    @pytest.mark.asyncio
    async def test_get_user_invalid_id_format(
        self, users_manager: UsersManager
    ) -> None:
        """Test get_user with invalid ID format."""
        with pytest.raises(SlackClientError, match="Invalid user ID format"):
            await users_manager.get_user(user_id="invalid")

    @pytest.mark.asyncio
    async def test_get_presence_success(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test successful presence lookup."""
        mock_client.call_api.return_value = {
            "ok": True,
            "presence": "active",
            "online": True,
            "auto_away": False,
            "manual_away": False,
        }

        result = await users_manager.get_presence(user_id="U123")

        assert result["ok"] is True
        assert result["presence"] == "active"
        assert result["online"] is True
        mock_client.call_api.assert_called_once_with("users.getPresence", user="U123")

    @pytest.mark.asyncio
    async def test_get_presence_empty_id(self, users_manager: UsersManager) -> None:
        """Test get_presence with empty user ID."""
        with pytest.raises(SlackClientError, match="User ID is required"):
            await users_manager.get_presence(user_id="")

    @pytest.mark.asyncio
    async def test_get_presence_invalid_id_format(
        self, users_manager: UsersManager
    ) -> None:
        """Test get_presence with invalid ID format."""
        with pytest.raises(SlackClientError, match="Invalid user ID format"):
            await users_manager.get_presence(user_id="invalid")

    @pytest.mark.asyncio
    async def test_search_users_success(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test successful user search."""
        mock_client.call_api.return_value = {
            "members": [
                {
                    "id": "U123",
                    "name": "john",
                    "real_name": "John Doe",
                    "is_bot": False,
                    "deleted": False,
                    "profile": {"email": "john@example.com"},
                },
                {
                    "id": "U456",
                    "name": "jane",
                    "real_name": "Jane Doe",
                    "is_bot": False,
                    "deleted": False,
                    "profile": {"email": "jane@example.com"},
                },
                {
                    "id": "U789",
                    "name": "bob",
                    "real_name": "Bob Smith",
                    "is_bot": False,
                    "deleted": False,
                    "profile": {"email": "bob@example.com"},
                },
            ],
            "response_metadata": {},
        }

        results = await users_manager.search_users(query="doe")

        assert len(results) == 2
        assert all("doe" in u.get("real_name", "").lower() for u in results)

    @pytest.mark.asyncio
    async def test_search_users_by_email(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test user search by email."""
        mock_client.call_api.return_value = {
            "members": [
                {
                    "id": "U123",
                    "name": "john",
                    "real_name": "John Doe",
                    "is_bot": False,
                    "deleted": False,
                    "profile": {"email": "john@example.com"},
                },
            ],
            "response_metadata": {},
        }

        results = await users_manager.search_users(query="john@example")

        assert len(results) == 1
        assert results[0]["id"] == "U123"

    @pytest.mark.asyncio
    async def test_search_users_empty_query(
        self, users_manager: UsersManager
    ) -> None:
        """Test search with empty query."""
        with pytest.raises(SlackClientError, match="Search query must not be empty"):
            await users_manager.search_users(query="")

    @pytest.mark.asyncio
    async def test_search_users_no_matches(
        self, users_manager: UsersManager, mock_client: Mock
    ) -> None:
        """Test search with no matching users."""
        mock_client.call_api.return_value = {
            "members": [
                {
                    "id": "U123",
                    "name": "john",
                    "real_name": "John Doe",
                    "is_bot": False,
                    "deleted": False,
                    "profile": {"email": "john@example.com"},
                },
            ],
            "response_metadata": {},
        }

        results = await users_manager.search_users(query="nonexistent")

        assert len(results) == 0
