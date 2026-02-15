"""
Slack API Client Wrapper.

Provides async Slack API client with authentication validation,
error handling, and rate limit management.
"""

import logging
from typing import Any, Dict, Optional

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackClientError(Exception):
    """Exception raised for Slack API client errors."""


class SlackClient:
    """
    Wrapper for Slack AsyncWebClient with authentication and error handling.

    Provides a simplified interface to the Slack API with automatic
    OAuth token management and error handling.
    """

    def __init__(self, oauth_token: str) -> None:
        """
        Initialize Slack client with OAuth token.

        Args:
            oauth_token: User OAuth token (xoxp-...)

        Raises:
            SlackClientError: If token format is invalid
        """
        if not oauth_token.startswith("xoxp-"):
            raise SlackClientError("Invalid OAuth token format - must be user token (xoxp-...)")

        self.token = oauth_token
        self.client = AsyncWebClient(token=oauth_token)
        self._auth_info: Optional[Dict[str, Any]] = None

        logger.debug("Initialized Slack client")

    async def validate_auth(self) -> Dict[str, Any]:
        """
        Validate OAuth token and get auth info.

        Returns:
            Authentication info dictionary with user_id, team_id, etc.

        Raises:
            SlackClientError: If authentication fails
        """
        if self._auth_info is not None:
            return self._auth_info

        try:
            response = await self.client.auth_test()
            self._auth_info = {
                "ok": response["ok"],
                "url": response.get("url", ""),
                "team": response.get("team", ""),
                "user": response.get("user", ""),
                "team_id": response.get("team_id", ""),
                "user_id": response.get("user_id", ""),
            }
            logger.info(
                "Auth validated - Team: %s, User: %s",
                self._auth_info["team"],
                self._auth_info["user"],
            )
            return self._auth_info

        except SlackApiError as error:
            logger.error("Auth validation failed: %s", error.response["error"])
            raise SlackClientError(f"Authentication failed: {error.response['error']}") from error

    async def call_api(self, method: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Slack API method with error handling.

        Args:
            method: API method name (e.g., 'conversations.list')
            **kwargs: Method-specific parameters

        Returns:
            API response data dictionary

        Raises:
            SlackClientError: If API call fails
        """
        try:
            # Get the method from the client
            api_method = getattr(self.client, method.replace(".", "_"))
            response = await api_method(**kwargs)

            if not response["ok"]:
                raise SlackClientError(f"API call failed: {response.get('error', 'Unknown error')}")

            return dict(response.data)

        except SlackApiError as error:
            error_msg = error.response.get("error", "Unknown error")
            logger.error("Slack API error (%s): %s", method, error_msg)

            # Handle specific error cases
            if error_msg in ("invalid_auth", "token_revoked"):
                raise SlackClientError(
                    "OAuth token is invalid or revoked. Please regenerate token."
                ) from error
            if error_msg == "missing_scope":
                raise SlackClientError(
                    f"Missing required OAuth scope for {method}. "
                    "Please add required scopes and reinstall app."
                ) from error
            if error_msg == "ratelimited":
                retry_after = error.response.headers.get("Retry-After", "60")
                raise SlackClientError(
                    f"Rate limited. Retry after {retry_after} seconds."
                ) from error

            raise SlackClientError(f"Slack API error: {error_msg}") from error

        except AttributeError as error:
            raise SlackClientError(f"Unknown API method: {method}") from error

    def get_auth_info(self) -> Optional[Dict[str, Any]]:
        """
        Get cached authentication info.

        Returns:
            Authentication info if validated, None otherwise
        """
        return self._auth_info
