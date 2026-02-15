"""
Slack Files Manager.

Handles file operations including upload, listing, info retrieval, and deletion.
"""

import logging
import os
from typing import Any, Dict, List, Optional, cast

from slack_mcp.slack_client import SlackClient, SlackClientError

logger = logging.getLogger(__name__)


class FilesManager:
    """
    Manages Slack file operations.

    Provides operations for uploading files, listing files with filters,
    getting file information, and deleting files.
    """

    def __init__(self, client: SlackClient) -> None:
        """
        Initialize files manager.

        Args:
            client: Authenticated Slack client
        """
        self.client = client

    async def upload_file(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        file_path: str,
        channels: Optional[List[str]] = None,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file to Slack.

        Args:
            file_path: Path to file to upload
            channels: Optional list of channel IDs to share file in
            title: Optional file title
            initial_comment: Optional comment to add with file
            thread_ts: Optional thread timestamp for threaded uploads

        Returns:
            Uploaded file info including file ID and permalink

        Raises:
            SlackClientError: If upload fails
        """
        if not file_path:
            raise SlackClientError("File path is required")

        if not os.path.exists(file_path):
            raise SlackClientError(f"File not found: {file_path}")

        if not os.path.isfile(file_path):
            raise SlackClientError(f"Path is not a file: {file_path}")

        # Check file size (Slack has a 1GB limit, but we'll enforce 10MB for safety)
        file_size = os.path.getsize(file_path)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise SlackClientError(
                f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)"
            )

        kwargs: Dict[str, Any] = {
            "file": file_path,
        }

        if channels:
            # Validate channel IDs
            for channel in channels:
                if not channel or channel[0] not in ["C", "G", "D"]:
                    raise SlackClientError(
                        f"Invalid channel ID format: {channel}. Must start with C, G, or D"
                    )
            kwargs["channels"] = ",".join(channels)

        if title:
            kwargs["title"] = title

        if initial_comment:
            kwargs["initial_comment"] = initial_comment

        if thread_ts:
            kwargs["thread_ts"] = thread_ts

        response = await self.client.call_api("files.upload", **kwargs)

        file_info = response.get("file", {})
        logger.info("Uploaded file: %s", file_info.get("id", "unknown"))
        return cast(Dict[str, Any], file_info)

    async def list_files(  # pylint: disable=too-many-locals
        self,
        channel: Optional[str] = None,
        user: Optional[str] = None,
        types: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List files in workspace.

        Args:
            channel: Optional channel ID to filter by
            user: Optional user ID to filter by
            types: Optional file types to filter (all, spaces, snippets, images, etc.)
            limit: Maximum number of files to return

        Returns:
            List of file info dictionaries

        Raises:
            SlackClientError: If listing fails
        """
        if limit < 1 or limit > 1000:
            raise SlackClientError("Limit must be between 1 and 1000")

        valid_types = {
            "all",
            "spaces",
            "snippets",
            "images",
            "gdocs",
            "zips",
            "pdfs",
        }
        if types:
            invalid = set(types) - valid_types
            if invalid:
                raise SlackClientError(
                    f"Invalid file types: {invalid}. Valid types: {valid_types}"
                )
            types_param = ",".join(types)
        else:
            types_param = "all"

        files: List[Dict[str, Any]] = []
        page = 1
        pages_needed = (limit + 99) // 100  # Round up to get number of pages

        while page <= pages_needed:
            kwargs: Dict[str, Any] = {
                "count": min(100, limit - len(files)),
                "page": page,
                "types": types_param,
            }

            if channel:
                kwargs["channel"] = channel

            if user:
                kwargs["user"] = user

            response = await self.client.call_api("files.list", **kwargs)

            batch = response.get("files", [])
            files.extend(batch)

            # Check if there are more pages
            paging = response.get("paging", {})
            total_pages = paging.get("pages", 1)
            if page >= total_pages or len(files) >= limit:
                break

            page += 1

        logger.info("Listed %d files", len(files))
        return files[:limit]

    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a file.

        Args:
            file_id: File ID (F...)

        Returns:
            File info dictionary

        Raises:
            SlackClientError: If file lookup fails
        """
        if not file_id:
            raise SlackClientError("File ID is required")

        if not file_id[0] == "F":
            raise SlackClientError("Invalid file ID format - must start with F")

        response = await self.client.call_api("files.info", file=file_id)

        file_info = response.get("file", {})
        logger.info("Retrieved file info: %s", file_id)
        return cast(Dict[str, Any], file_info)

    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file.

        Args:
            file_id: File ID to delete

        Returns:
            True if successful

        Raises:
            SlackClientError: If deletion fails
        """
        if not file_id:
            raise SlackClientError("File ID is required")

        if not file_id[0] == "F":
            raise SlackClientError("Invalid file ID format - must start with F")

        response = await self.client.call_api("files.delete", file=file_id)

        logger.info("Deleted file: %s", file_id)
        return cast(bool, response["ok"])
