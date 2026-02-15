"""
Tests for Slack workspace operations.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from slack_mcp.slack_client import SlackClient
from slack_mcp.workspace_operations import WorkspaceOperations


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock Slack client."""
    client = Mock(spec=SlackClient)
    client.call_api = AsyncMock()
    return client


@pytest.fixture
def workspace_ops(mock_client: Mock) -> WorkspaceOperations:
    """Create WorkspaceOperations with mock client."""
    return WorkspaceOperations(mock_client)


class TestWorkspaceOperations:
    """Tests for WorkspaceOperations class."""

    @pytest.mark.asyncio
    async def test_get_team_info_success(
        self, workspace_ops: WorkspaceOperations, mock_client: Mock
    ) -> None:
        """Test successful team info retrieval."""
        mock_client.call_api.return_value = {
            "team": {
                "id": "T123",
                "name": "Test Team",
                "domain": "test-team",
                "email_domain": "example.com",
            }
        }

        result = await workspace_ops.get_team_info()

        assert result["id"] == "T123"
        assert result["name"] == "Test Team"
        mock_client.call_api.assert_called_once_with("team.info")

    @pytest.mark.asyncio
    async def test_list_emoji_success(
        self, workspace_ops: WorkspaceOperations, mock_client: Mock
    ) -> None:
        """Test successful emoji listing."""
        mock_client.call_api.return_value = {
            "emoji": {
                "custom_emoji1": "https://example.com/emoji1.png",
                "custom_emoji2": "https://example.com/emoji2.png",
            }
        }

        result = await workspace_ops.list_emoji()

        assert len(result) == 2
        assert "custom_emoji1" in result
        assert result["custom_emoji1"] == "https://example.com/emoji1.png"
        mock_client.call_api.assert_called_once_with("emoji.list")

    @pytest.mark.asyncio
    async def test_list_emoji_empty(
        self, workspace_ops: WorkspaceOperations, mock_client: Mock
    ) -> None:
        """Test emoji listing with no custom emoji."""
        mock_client.call_api.return_value = {"emoji": {}}

        result = await workspace_ops.list_emoji()

        assert len(result) == 0
        mock_client.call_api.assert_called_once_with("emoji.list")

    @pytest.mark.asyncio
    async def test_get_workspace_stats_success(
        self, workspace_ops: WorkspaceOperations, mock_client: Mock
    ) -> None:
        """Test successful workspace stats retrieval."""
        mock_client.call_api.side_effect = [
            # team.info response
            {"team": {"id": "T123", "name": "Test Team"}},
            # users.list response
            {
                "members": [
                    {"id": "U1", "is_bot": False, "deleted": False},
                    {"id": "U2", "is_bot": False, "deleted": False},
                    {"id": "B1", "is_bot": True, "deleted": False},
                ]
            },
            # conversations.list response
            {
                "channels": [{"id": "C1"}, {"id": "C2"}],
                "response_metadata": {},
            },
            # emoji.list response
            {"emoji": {"emoji1": "url1", "emoji2": "url2"}},
        ]

        result = await workspace_ops.get_workspace_stats()

        assert result["team_info"]["name"] == "Test Team"
        assert result["user_count_sample"] == 2
        assert result["channel_count_sample"] == 2
        assert result["emoji_count"] == 2
        assert mock_client.call_api.call_count == 4

    @pytest.mark.asyncio
    async def test_get_workspace_stats_includes_notes(
        self, workspace_ops: WorkspaceOperations, mock_client: Mock
    ) -> None:
        """Test that stats include sample size notes."""
        mock_client.call_api.side_effect = [
            {"team": {"id": "T123"}},
            {"members": []},
            {"channels": [], "response_metadata": {}},
            {"emoji": {}},
        ]

        result = await workspace_ops.get_workspace_stats()

        assert "user_count_note" in result
        assert "Sample from first page only" in result["user_count_note"]
        assert "channel_count_note" in result
        assert "Sample from first page only" in result["channel_count_note"]
