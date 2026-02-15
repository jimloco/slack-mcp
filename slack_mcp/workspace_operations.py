"""
Slack Workspace Operations.

Handles workspace-level operations including team info, emoji, and statistics.
"""

import logging
from typing import Any, Dict, cast

from slack_mcp.slack_client import SlackClient

logger = logging.getLogger(__name__)


class WorkspaceOperations:
    """
    Manages Slack workspace-level operations.

    Provides operations for getting team information, listing custom emoji,
    and retrieving workspace statistics.
    """

    def __init__(self, client: SlackClient) -> None:
        """
        Initialize workspace operations.

        Args:
            client: Authenticated Slack client
        """
        self.client = client

    async def get_team_info(self) -> Dict[str, Any]:
        """
        Get workspace/team information.

        Returns:
            Team info dictionary with name, domain, icon, etc.

        Raises:
            SlackClientError: If team info retrieval fails
        """
        response = await self.client.call_api("team.info")

        team_info = response.get("team", {})
        logger.info("Retrieved team info for: %s", team_info.get("name", "unknown"))
        return cast(Dict[str, Any], team_info)

    async def list_emoji(self) -> Dict[str, str]:
        """
        List custom emoji in workspace.

        Returns:
            Dictionary mapping emoji names to image URLs

        Raises:
            SlackClientError: If emoji listing fails
        """
        response = await self.client.call_api("emoji.list")

        emoji_list = response.get("emoji", {})
        logger.info("Listed %d custom emoji", len(emoji_list))
        return cast(Dict[str, str], emoji_list)

    async def get_workspace_stats(self) -> Dict[str, Any]:
        """
        Get workspace statistics by aggregating data from multiple APIs.

        Returns:
            Dictionary with workspace statistics including:
            - team_info: Basic team information
            - user_count: Number of active users
            - channel_count: Number of public channels
            - emoji_count: Number of custom emoji

        Raises:
            SlackClientError: If stats retrieval fails
        """
        stats: Dict[str, Any] = {}

        # Get team info
        team_response = await self.client.call_api("team.info")
        stats["team_info"] = team_response.get("team", {})

        # Get user count
        users_response = await self.client.call_api("users.list", limit=1)
        # Note: We don't paginate here, just get the response metadata
        # to avoid loading all users
        members = users_response.get("members", [])
        # Filter active, non-bot users
        active_users = [
            u for u in members if not u.get("is_bot", False) and not u.get("deleted", False)
        ]
        stats["user_count_sample"] = len(active_users)
        stats["user_count_note"] = "Sample from first page only"

        # Get channel count
        channels_response = await self.client.call_api(
            "conversations.list", types="public_channel", limit=1
        )
        # Get response metadata for total count if available
        response_metadata = channels_response.get("response_metadata", {})
        stats["response_metadata"] = response_metadata

        # Count channels from first page
        channels = channels_response.get("channels", [])
        stats["channel_count_sample"] = len(channels)
        stats["channel_count_note"] = "Sample from first page only"

        # Get emoji count
        emoji_response = await self.client.call_api("emoji.list")
        emoji = emoji_response.get("emoji", {})
        stats["emoji_count"] = len(emoji)

        logger.info("Retrieved workspace stats for team: %s", stats["team_info"].get("name"))
        return stats
