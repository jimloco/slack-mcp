"""
Slack Users Manager.

Handles user profile and presence operations including listing users,
getting user details, and checking presence status.
"""

import logging
from typing import Any, Dict, List, Optional, cast

from slack_mcp.slack_client import SlackClient, SlackClientError

logger = logging.getLogger(__name__)


class UsersManager:
    """
    Manages Slack user operations.

    Provides operations for listing users, getting user profiles,
    checking presence, and searching users.
    """

    def __init__(self, client: SlackClient) -> None:
        """
        Initialize users manager.

        Args:
            client: Authenticated Slack client
        """
        self.client = client

    async def list_users(
        self,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List all users in the workspace.

        Args:
            limit: Maximum number of users to return

        Returns:
            List of user info dictionaries

        Raises:
            SlackClientError: If listing fails
        """
        users: List[Dict[str, Any]] = []
        cursor = None

        while True:
            kwargs: Dict[str, Any] = {
                "limit": min(limit - len(users), 200),
            }

            if cursor:
                kwargs["cursor"] = cursor

            response = await self.client.call_api("users.list", **kwargs)

            batch = response.get("members", [])
            # Filter out bots and deleted users by default
            filtered = [
                u for u in batch if not u.get("is_bot", False) and not u.get("deleted", False)
            ]
            users.extend(filtered)

            # Check if we have enough or if there's more
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor or len(users) >= limit:
                break

        logger.info("Listed %d users", len(users))
        return users[:limit]

    async def get_user(
        self,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get user profile by ID or email.

        Args:
            user_id: User ID (U... or W...)
            email: User email address

        Returns:
            User profile dictionary

        Raises:
            SlackClientError: If lookup fails or neither ID nor email provided
        """
        if not user_id and not email:
            raise SlackClientError("Either user_id or email is required")

        if email:
            # Lookup by email
            response = await self.client.call_api(
                "users.lookupByEmail",
                email=email,
            )
            user = response.get("user", {})
        else:
            # Lookup by ID
            if not user_id:
                raise SlackClientError("User ID is required")

            # Validate user ID format
            if not user_id[0] in ["U", "W"]:
                raise SlackClientError("Invalid user ID format - must start with U or W")

            response = await self.client.call_api(
                "users.info",
                user=user_id,
            )
            user = response.get("user", {})

        logger.info("Retrieved user: %s", user.get("id", "unknown"))
        return cast(Dict[str, Any], user)

    async def get_presence(self, user_id: str) -> Dict[str, Any]:
        """
        Get user presence status.

        Args:
            user_id: User ID

        Returns:
            Presence info dictionary with 'presence' field ('active' or 'away')

        Raises:
            SlackClientError: If presence lookup fails
        """
        if not user_id:
            raise SlackClientError("User ID is required")

        # Validate user ID format
        if not user_id[0] in ["U", "W"]:
            raise SlackClientError("Invalid user ID format - must start with U or W")

        response = await self.client.call_api(
            "users.getPresence",
            user=user_id,
        )

        presence_info = {
            "ok": response["ok"],
            "presence": response.get("presence", "unknown"),
            "online": response.get("online", False),
            "auto_away": response.get("auto_away", False),
            "manual_away": response.get("manual_away", False),
        }

        logger.info(
            "Retrieved presence for user %s: %s",
            user_id,
            presence_info["presence"],
        )
        return presence_info

    async def search_users(self, query: str) -> List[Dict[str, Any]]:
        """
        Search users by name or email.

        Args:
            query: Search query (name or email)

        Returns:
            List of matching users

        Raises:
            SlackClientError: If search fails
        """
        if not query or len(query) < 1:
            raise SlackClientError("Search query must not be empty")

        # Get all users and filter locally
        # Note: Slack doesn't have a dedicated user search API
        all_users = await self.list_users(limit=1000)

        query_lower = query.lower()
        matching_users = [
            user
            for user in all_users
            if (
                query_lower in user.get("real_name", "").lower()
                or query_lower in user.get("name", "").lower()
                or query_lower in user.get("profile", {}).get("email", "").lower()
            )
        ]

        logger.info(
            "Found %d users matching query: %s",
            len(matching_users),
            query,
        )
        return matching_users
