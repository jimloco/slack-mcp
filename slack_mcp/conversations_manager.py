"""
Slack Conversations Manager.

Handles message and channel operations including search, posting,
listing channels, and channel management.
"""

import logging
from typing import Any, Dict, List, Optional, cast

from slack_mcp.slack_client import SlackClient, SlackClientError

logger = logging.getLogger(__name__)


class ConversationsManager:
    """
    Manages Slack conversations and channel operations.

    Provides operations for searching messages, posting to channels,
    listing channels, and managing channel membership.
    """

    def __init__(self, client: SlackClient) -> None:
        """
        Initialize conversations manager.

        Args:
            client: Authenticated Slack client
        """
        self.client = client

    async def search_messages(
        self,
        query: str,
        channel: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search messages in workspace.

        Args:
            query: Search query text
            channel: Optional channel ID to limit search
            limit: Maximum number of results (default 10, max 100)

        Returns:
            List of matching messages

        Raises:
            SlackClientError: If search fails
        """
        if not query or len(query) < 1:
            raise SlackClientError("Search query must not be empty")

        if limit < 1 or limit > 100:
            raise SlackClientError("Limit must be between 1 and 100")

        # Build search query
        search_query = query
        if channel:
            search_query = f"in:{channel} {query}"

        response = await self.client.call_api(
            "search.messages",
            query=search_query,
            count=limit,
        )

        messages = response.get("messages", {}).get("matches", [])
        logger.info("Found %d messages for query: %s", len(messages), query)
        return cast(List[Dict[str, Any]], messages)

    async def post_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post a message to a channel or thread.

        Args:
            channel: Channel ID (C..., G..., or D...)
            text: Message text (supports Slack markdown)
            thread_ts: Optional thread timestamp for replies

        Returns:
            Posted message info including ts and permalink

        Raises:
            SlackClientError: If posting fails
        """
        if not channel:
            raise SlackClientError("Channel ID is required")

        if not text or len(text) < 1:
            raise SlackClientError("Message text must not be empty")

        if len(text) > 40000:
            raise SlackClientError("Message text must be ≤40,000 characters")

        # Validate channel ID format
        if not channel[0] in ["C", "G", "D"]:
            raise SlackClientError("Invalid channel ID format - must start with C, G, or D")

        kwargs: Dict[str, Any] = {
            "channel": channel,
            "text": text,
        }

        if thread_ts:
            kwargs["thread_ts"] = thread_ts

        response = await self.client.call_api("chat.postMessage", **kwargs)

        message_info = {
            "ok": response["ok"],
            "channel": response["channel"],
            "ts": response["ts"],
            "message": response.get("message", {}),
        }

        logger.info("Posted message to channel %s", channel)
        return message_info

    async def list_channels(
        self,
        types: Optional[List[str]] = None,
        exclude_archived: bool = True,
        member_only: bool = True,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List conversations (channels, DMs, groups).

        Args:
            types: Channel types to include (public_channel, private_channel, im, mpim)
            exclude_archived: Whether to exclude archived channels
            member_only: Only return channels the user is a member of (default True)
            limit: Maximum number of channels to return

        Returns:
            List of channel info dictionaries

        Raises:
            SlackClientError: If listing fails
        """
        valid_types = {"public_channel", "private_channel", "im", "mpim"}
        if types:
            invalid = set(types) - valid_types
            if invalid:
                raise SlackClientError(
                    f"Invalid channel types: {invalid}. " f"Valid types: {valid_types}"
                )
            types_param = ",".join(types)
        else:
            types_param = "public_channel,private_channel"

        channels: List[Dict[str, Any]] = []
        cursor = None

        while True:
            kwargs: Dict[str, Any] = {
                "types": types_param,
                "exclude_archived": exclude_archived,
                "limit": min(limit - len(channels), 200),
            }

            if cursor:
                kwargs["cursor"] = cursor

            response = await self.client.call_api("conversations.list", **kwargs)

            batch = response.get("channels", [])

            # Filter by membership if requested
            if member_only:
                batch = [ch for ch in batch if ch.get("is_member", False)]

            channels.extend(batch)

            # Check if we have enough or if there's more
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor or len(channels) >= limit:
                break

        logger.info("Listed %d channels", len(channels))
        return channels[:limit]

    async def create_channel(
        self,
        name: str,
        is_private: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new channel.

        Args:
            name: Channel name (lowercase, no spaces, max 80 chars)
            is_private: Whether to create a private channel

        Returns:
            Created channel info

        Raises:
            SlackClientError: If creation fails
        """
        if not name or len(name) < 1:
            raise SlackClientError("Channel name is required")

        if len(name) > 80:
            raise SlackClientError("Channel name must be ≤80 characters")

        # Validate channel name format
        if not name.islower() or " " in name:
            raise SlackClientError("Channel name must be lowercase with no spaces")

        response = await self.client.call_api(
            "conversations.create",
            name=name,
            is_private=is_private,
        )

        channel = response.get("channel", {})
        logger.info("Created channel: %s", name)
        return cast(Dict[str, Any], channel)

    async def archive_channel(self, channel: str) -> bool:
        """
        Archive a channel.

        Args:
            channel: Channel ID to archive

        Returns:
            True if successful

        Raises:
            SlackClientError: If archiving fails
        """
        if not channel:
            raise SlackClientError("Channel ID is required")

        response = await self.client.call_api(
            "conversations.archive",
            channel=channel,
        )

        logger.info("Archived channel: %s", channel)
        return cast(bool, response["ok"])

    async def get_history(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        channel: str,
        limit: int = 100,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
        inclusive: bool = False,
    ) -> Dict[str, Any]:
        """
        Read message history from a channel.

        Args:
            channel: Channel ID to read from
            limit: Maximum number of messages (default 100, max 1000)
            oldest: Only messages after this Unix timestamp (inclusive if inclusive=True)
            latest: Only messages before this Unix timestamp (inclusive if inclusive=True)
            inclusive: Include messages with latest or oldest timestamp

        Returns:
            Dictionary containing messages array and response metadata

        Raises:
            SlackClientError: If reading fails
        """
        if not channel:
            raise SlackClientError("Channel ID is required")

        if limit < 1 or limit > 1000:
            raise SlackClientError("Limit must be between 1 and 1000")

        # Validate channel ID format
        if not channel[0] in ["C", "G", "D"]:
            raise SlackClientError("Invalid channel ID format - must start with C, G, or D")

        kwargs: Dict[str, Any] = {
            "channel": channel,
            "limit": limit,
            "inclusive": inclusive,
        }

        if oldest:
            kwargs["oldest"] = oldest
        if latest:
            kwargs["latest"] = latest

        response = await self.client.call_api("conversations.history", **kwargs)

        result = {
            "ok": response["ok"],
            "messages": response.get("messages", []),
            "has_more": response.get("has_more", False),
            "response_metadata": response.get("response_metadata", {}),
        }

        logger.info("Retrieved %d messages from channel %s", len(result["messages"]), channel)
        return result

    async def get_replies(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        channel: str,
        thread_ts: str,
        limit: int = 100,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
        inclusive: bool = False,
    ) -> Dict[str, Any]:
        """
        Read replies from a thread.

        Args:
            channel: Channel ID containing the thread
            thread_ts: Timestamp of the parent message
            limit: Maximum number of replies (default 100, max 1000)
            oldest: Only messages after this Unix timestamp (inclusive if inclusive=True)
            latest: Only messages before this Unix timestamp (inclusive if inclusive=True)
            inclusive: Include messages with latest or oldest timestamp

        Returns:
            Dictionary containing messages array (includes parent) and response metadata

        Raises:
            SlackClientError: If reading fails
        """
        if not channel:
            raise SlackClientError("Channel ID is required")

        if not thread_ts:
            raise SlackClientError("Thread timestamp is required")

        if limit < 1 or limit > 1000:
            raise SlackClientError("Limit must be between 1 and 1000")

        # Validate channel ID format
        if not channel[0] in ["C", "G", "D"]:
            raise SlackClientError("Invalid channel ID format - must start with C, G, or D")

        kwargs: Dict[str, Any] = {
            "channel": channel,
            "ts": thread_ts,
            "limit": limit,
            "inclusive": inclusive,
        }

        if oldest:
            kwargs["oldest"] = oldest
        if latest:
            kwargs["latest"] = latest

        response = await self.client.call_api("conversations.replies", **kwargs)

        result = {
            "ok": response["ok"],
            "messages": response.get("messages", []),
            "has_more": response.get("has_more", False),
            "response_metadata": response.get("response_metadata", {}),
        }

        logger.info(
            "Retrieved %d replies from thread %s in channel %s",
            len(result["messages"]),
            thread_ts,
            channel,
        )
        return result
