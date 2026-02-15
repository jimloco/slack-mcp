"""
Tests for Slack conversations manager.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from slack_mcp.slack_client import SlackClient, SlackClientError
from slack_mcp.conversations_manager import ConversationsManager


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock Slack client."""
    client = Mock(spec=SlackClient)
    client.call_api = AsyncMock()
    return client


@pytest.fixture
def conversations_manager(mock_client: Mock) -> ConversationsManager:
    """Create ConversationsManager with mock client."""
    return ConversationsManager(mock_client)


class TestConversationsManager:
    """Tests for ConversationsManager class."""

    @pytest.mark.asyncio
    async def test_search_messages_success(
        self, conversations_manager: ConversationsManager, mock_client: Mock
    ) -> None:
        """Test successful message search."""
        mock_client.call_api.return_value = {
            "messages": {"matches": [{"text": "test message", "user": "U123"}]}
        }

        results = await conversations_manager.search_messages("test query", limit=10)

        assert len(results) == 1
        assert results[0]["text"] == "test message"
        mock_client.call_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_messages_empty_query(
        self, conversations_manager: ConversationsManager
    ) -> None:
        """Test search with empty query."""
        with pytest.raises(SlackClientError, match="Search query must not be empty"):
            await conversations_manager.search_messages("")

    @pytest.mark.asyncio
    async def test_search_messages_invalid_limit(
        self, conversations_manager: ConversationsManager
    ) -> None:
        """Test search with invalid limit."""
        with pytest.raises(SlackClientError, match="Limit must be between 1 and 100"):
            await conversations_manager.search_messages("test", limit=200)

    @pytest.mark.asyncio
    async def test_post_message_success(
        self, conversations_manager: ConversationsManager, mock_client: Mock
    ) -> None:
        """Test successful message posting."""
        mock_client.call_api.return_value = {
            "ok": True,
            "channel": "C123",
            "ts": "1234567890.123456",
            "message": {"text": "test"},
        }

        result = await conversations_manager.post_message("C123", "test message")

        assert result["ok"] is True
        assert result["channel"] == "C123"
        mock_client.call_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_message_invalid_channel(
        self, conversations_manager: ConversationsManager
    ) -> None:
        """Test posting with invalid channel ID."""
        with pytest.raises(SlackClientError, match="Invalid channel ID format"):
            await conversations_manager.post_message("invalid", "test")

    @pytest.mark.asyncio
    async def test_post_message_empty_text(
        self, conversations_manager: ConversationsManager
    ) -> None:
        """Test posting with empty text."""
        with pytest.raises(SlackClientError, match="Message text must not be empty"):
            await conversations_manager.post_message("C123", "")

    @pytest.mark.asyncio
    async def test_post_message_text_too_long(
        self, conversations_manager: ConversationsManager
    ) -> None:
        """Test posting with text exceeding limit."""
        long_text = "x" * 40001
        with pytest.raises(SlackClientError, match="Message text must be ≤40,000 characters"):
            await conversations_manager.post_message("C123", long_text)

    @pytest.mark.asyncio
    async def test_list_channels_success(
        self, conversations_manager: ConversationsManager, mock_client: Mock
    ) -> None:
        """Test successful channel listing."""
        mock_client.call_api.return_value = {
            "channels": [
                {"id": "C123", "name": "general", "is_member": True},
                {"id": "C456", "name": "random", "is_member": True},
            ],
            "response_metadata": {},
        }

        results = await conversations_manager.list_channels(limit=100)

        assert len(results) == 2
        assert results[0]["name"] == "general"
        mock_client.call_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_channels_with_pagination(
        self, conversations_manager: ConversationsManager, mock_client: Mock
    ) -> None:
        """Test channel listing with pagination."""
        mock_client.call_api.side_effect = [
            {
                "channels": [{"id": "C1", "name": "ch1", "is_member": True}],
                "response_metadata": {"next_cursor": "abc123"},
            },
            {"channels": [{"id": "C2", "name": "ch2", "is_member": True}], "response_metadata": {}},
        ]

        results = await conversations_manager.list_channels(limit=100)

        assert len(results) == 2
        assert mock_client.call_api.call_count == 2

    @pytest.mark.asyncio
    async def test_list_channels_invalid_types(
        self, conversations_manager: ConversationsManager
    ) -> None:
        """Test listing with invalid channel types."""
        with pytest.raises(SlackClientError, match="Invalid channel types"):
            await conversations_manager.list_channels(types=["invalid_type"])

    @pytest.mark.asyncio
    async def test_list_channels_member_only(
        self, conversations_manager: ConversationsManager, mock_client: Mock
    ) -> None:
        """Test listing only channels user is member of."""
        mock_client.call_api.return_value = {
            "channels": [
                {"id": "C123", "name": "member-channel", "is_member": True},
                {"id": "C456", "name": "non-member-channel", "is_member": False},
                {"id": "C789", "name": "another-member", "is_member": True},
            ],
            "response_metadata": {},
        }

        # Test with member_only=True (default)
        results = await conversations_manager.list_channels(limit=100)
        assert len(results) == 2
        assert all(ch.get("is_member") for ch in results)

        # Test with member_only=False
        results = await conversations_manager.list_channels(member_only=False, limit=100)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_create_channel_success(
        self, conversations_manager: ConversationsManager, mock_client: Mock
    ) -> None:
        """Test successful channel creation."""
        mock_client.call_api.return_value = {
            "channel": {"id": "C123", "name": "new-channel"}
        }

        result = await conversations_manager.create_channel("new-channel")

        assert result["name"] == "new-channel"
        mock_client.call_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_channel_invalid_name(
        self, conversations_manager: ConversationsManager
    ) -> None:
        """Test channel creation with invalid name."""
        with pytest.raises(SlackClientError, match="Channel name must be lowercase"):
            await conversations_manager.create_channel("Bad Channel")

    @pytest.mark.asyncio
    async def test_archive_channel_success(
        self, conversations_manager: ConversationsManager, mock_client: Mock
    ) -> None:
        """Test successful channel archiving."""
        mock_client.call_api.return_value = {"ok": True}

        result = await conversations_manager.archive_channel("C123")

        assert result is True
        mock_client.call_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_archive_channel_empty_id(
        self, conversations_manager: ConversationsManager
    ) -> None:
        """Test archiving with empty channel ID."""
        with pytest.raises(SlackClientError, match="Channel ID is required"):
            await conversations_manager.archive_channel("")
