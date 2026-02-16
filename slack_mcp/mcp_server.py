"""
MCP Server Implementation for Slack Integration.

Handles Model Context Protocol server setup, tool registration, and request routing.
"""

import json
import logging
from typing import Any, Dict, List

from mcp import types
from mcp.server.lowlevel import Server

from slack_mcp.workspace_manager import WorkspaceManager
from slack_mcp.slack_client import SlackClient, SlackClientError
from slack_mcp.conversations_manager import ConversationsManager
from slack_mcp.users_manager import UsersManager
from slack_mcp.files_manager import FilesManager
from slack_mcp.workspace_operations import WorkspaceOperations

logger = logging.getLogger(__name__)


class SlackMCPServer:  # pylint: disable=too-many-instance-attributes
    """
    MCP server for Slack integration.

    Provides four thematic tools: conversations, users, files, and workspace operations.
    """

    def __init__(self, workspace_manager: WorkspaceManager) -> None:
        """
        Initialize MCP server.

        Args:
            workspace_manager: Workspace configuration manager
        """
        self.workspace_manager = workspace_manager
        self.server_name = "slack-mcp"
        self.server_version = "0.1.0"

        # Initialize MCP server
        self.app = Server(self.server_name)

        # Managers will be initialized when needed
        self._client: SlackClient | None = None
        self._conversations: ConversationsManager | None = None
        self._users: UsersManager | None = None
        self._files: FilesManager | None = None
        self._workspace_ops: WorkspaceOperations | None = None

        logger.info("Initialized Slack MCP Server v%s", self.server_version)

    async def _get_client(self) -> SlackClient:
        """Get or create Slack client with current workspace token."""
        if self._client is None:
            token = self.workspace_manager.get_oauth_token()
            self._client = SlackClient(token)
            await self._client.validate_auth()
        return self._client

    async def _get_conversations(self) -> ConversationsManager:
        """Get or create conversations manager."""
        if self._conversations is None:
            client = await self._get_client()
            self._conversations = ConversationsManager(client)
        return self._conversations

    async def _get_users(self) -> UsersManager:
        """Get or create users manager."""
        if self._users is None:
            client = await self._get_client()
            self._users = UsersManager(client)
        return self._users

    async def _get_files(self) -> FilesManager:
        """Get or create files manager."""
        if self._files is None:
            client = await self._get_client()
            self._files = FilesManager(client)
        return self._files

    async def _get_workspace_ops(self) -> WorkspaceOperations:
        """Get or create workspace operations manager."""
        if self._workspace_ops is None:
            client = await self._get_client()
            self._workspace_ops = WorkspaceOperations(client)
        return self._workspace_ops

    def register_tools(self) -> None:
        """
        Register all MCP tools with the server.

        Registers four tools:
        - slack_conversations: Message and channel operations
        - slack_users: User profile and presence operations
        - slack_files: File upload and management operations (Phase 3)
        - slack_workspace: Workspace metadata operations (Phase 3)
        """
        logger.info("Registering MCP tools...")

        @self.app.list_tools()  # type: ignore[no-untyped-call,untyped-decorator]
        async def list_tools() -> List[types.Tool]:
            """List all available MCP tools."""
            return [
                types.Tool(
                    name="slack_conversations",
                    description=(
                        "Slack conversations and channel operations.\n\n"
                        "Operations:\n"
                        "- search: Search messages with query and optional filters\n"
                        "- get_history: Read message history from a channel\n"
                        "- get_replies: Read all replies in a thread\n"
                        "- post_message: Post message to channel or thread\n"
                        "- list_channels: List channels with optional type filters\n"
                        "- create_channel: Create a new channel\n"
                        "- archive_channel: Archive a channel\n"
                    ),
                    inputSchema={
                        "type": "object",
                        "required": ["operation"],
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": [
                                    "search",
                                    "get_history",
                                    "get_replies",
                                    "post_message",
                                    "list_channels",
                                    "create_channel",
                                    "archive_channel",
                                ],
                                "description": "Operation to perform",
                            },
                            "query": {
                                "type": "string",
                                "description": "Search query (for search operation)",
                            },
                            "channel": {
                                "type": "string",
                                "description": "Channel ID (C..., G..., or D...)",
                            },
                            "text": {
                                "type": "string",
                                "description": "Message text (for post_message)",
                            },
                            "thread_ts": {
                                "type": "string",
                                "description": "Thread timestamp (for get_replies, post_message)",
                            },
                            "oldest": {
                                "type": "string",
                                "description": (
                                    "Unix timestamp - only messages after this time "
                                    "(for get_history, get_replies)"
                                ),
                            },
                            "latest": {
                                "type": "string",
                                "description": (
                                    "Unix timestamp - only messages before this time "
                                    "(for get_history, get_replies)"
                                ),
                            },
                            "inclusive": {
                                "type": "boolean",
                                "description": (
                                    "Include messages with oldest/latest timestamp "
                                    "(for get_history, get_replies)"
                                ),
                            },
                            "types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": (
                                    "Channel types: public_channel, private_channel, im, mpim"
                                ),
                            },
                            "name": {
                                "type": "string",
                                "description": "Channel name (for create_channel)",
                            },
                            "is_private": {
                                "type": "boolean",
                                "description": "Create private channel",
                            },
                            "member_only": {
                                "type": "boolean",
                                "description": "Only list member channels (default: true)",
                            },
                            "limit": {
                                "type": "integer",
                                "description": (
                                    "Max results (1-100 for search, "
                                    "1-1000 for get_history/get_replies)"
                                ),
                                "minimum": 1,
                                "maximum": 1000,
                            },
                        },
                    },
                ),
                types.Tool(
                    name="slack_users",
                    description=(
                        "Slack user profile and presence operations.\n\n"
                        "Operations:\n"
                        "- list_users: List all workspace users\n"
                        "- get_user: Get user profile by ID or email\n"
                        "- get_presence: Check user presence status\n"
                        "- search_users: Search users by name or email\n"
                    ),
                    inputSchema={
                        "type": "object",
                        "required": ["operation"],
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": [
                                    "list_users",
                                    "get_user",
                                    "get_presence",
                                    "search_users",
                                ],
                                "description": "Operation to perform",
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User ID (U... or W...)",
                            },
                            "email": {
                                "type": "string",
                                "description": "User email address",
                            },
                            "query": {
                                "type": "string",
                                "description": "Search query for users",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max results",
                                "minimum": 1,
                                "maximum": 1000,
                            },
                        },
                    },
                ),
                types.Tool(
                    name="slack_files",
                    description=(
                        "Slack file upload and management operations.\\n\\n"
                        "Operations:\\n"
                        "- upload: Upload file to channels with metadata\\n"
                        "- list_files: List files with filters (user, channel, type)\\n"
                        "- get_file_info: Get detailed file information\\n"
                        "- delete_file: Delete a file\\n"
                    ),
                    inputSchema={
                        "type": "object",
                        "required": ["operation"],
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["upload", "list_files", "get_file_info", "delete_file"],
                                "description": "Operation to perform",
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to upload (for upload)",
                            },
                            "file_id": {
                                "type": "string",
                                "description": "File ID (for get_file_info, delete_file)",
                            },
                            "channels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Channel IDs to share file in (for upload)",
                            },
                            "title": {
                                "type": "string",
                                "description": "File title (for upload)",
                            },
                            "initial_comment": {
                                "type": "string",
                                "description": "Comment to add with file (for upload)",
                            },
                            "thread_ts": {
                                "type": "string",
                                "description": "Thread timestamp for threaded upload",
                            },
                            "channel": {
                                "type": "string",
                                "description": "Channel ID filter (for list_files)",
                            },
                            "user": {
                                "type": "string",
                                "description": "User ID filter (for list_files)",
                            },
                            "types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": (
                                    "File types: all, spaces, snippets, images, gdocs, zips, pdfs"
                                ),
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max results (for list_files)",
                                "minimum": 1,
                                "maximum": 1000,
                            },
                        },
                    },
                ),
                types.Tool(
                    name="slack_workspace",
                    description=(
                        "Slack workspace metadata and multi-workspace operations.\\n\\n"
                        "Operations:\\n"
                        "- get_team_info: Get workspace/team information\\n"
                        "- list_emoji: List custom emoji in workspace\\n"
                        "- get_stats: Get workspace statistics\\n"
                        "- list_workspaces: List all configured workspaces\\n"
                        "- switch_workspace: Switch to a different workspace\\n"
                        "- get_active_workspace: Get current workspace info\\n"
                    ),
                    inputSchema={
                        "type": "object",
                        "required": ["operation"],
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": [
                                    "get_team_info",
                                    "list_emoji",
                                    "get_stats",
                                    "list_workspaces",
                                    "switch_workspace",
                                    "get_active_workspace",
                                ],
                                "description": "Operation to perform",
                            },
                            "workspace_name": {
                                "type": "string",
                                "description": "Workspace name (for switch_workspace)",
                            },
                        },
                    },
                ),
            ]

        @self.app.call_tool()  # type: ignore[untyped-decorator]
        async def call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """
            Handle tool calls.

            Args:
                name: Tool name
                arguments: Tool arguments

            Returns:
                List of content items (text, image, or embedded resources)
            """
            try:
                operation = arguments.get("operation")
                logger.info("Tool call: %s, operation: %s", name, operation)

                if name == "slack_conversations":
                    return await self._handle_conversations(operation, arguments)
                if name == "slack_users":
                    return await self._handle_users(operation, arguments)
                if name == "slack_files":
                    return await self._handle_files(operation, arguments)
                if name == "slack_workspace":
                    return await self._handle_workspace(operation, arguments)

                raise ValueError(f"Unknown tool: {name}")

            except SlackClientError as error:
                logger.error("Slack API error: %s", error)
                return [types.TextContent(type="text", text=f"Slack API error: {error}")]
            except Exception as error:  # pylint: disable=broad-exception-caught
                # Catch all exceptions in tool calls to prevent server crashes
                logger.error("Tool call error: %s", error, exc_info=True)
                return [types.TextContent(type="text", text=f"Error: {error}")]

        logger.info("MCP tools registered successfully")

    async def _handle_conversations(  # pylint: disable=too-many-return-statements,too-many-branches
        self, operation: str | None, arguments: Dict[str, Any]
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle slack_conversations tool operations."""
        conversations = await self._get_conversations()

        if operation == "search":
            query = arguments.get("query")
            if not query:
                raise ValueError("search operation requires 'query' parameter")

            results = await conversations.search_messages(
                query=query,
                channel=arguments.get("channel"),
                limit=arguments.get("limit", 10),
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"Found {len(results)} messages:\n\n{json.dumps(results, indent=2)}",
                )
            ]

        if operation == "get_history":
            channel = arguments.get("channel")
            if not channel:
                raise ValueError("get_history operation requires 'channel' parameter")

            result = await conversations.get_history(
                channel=channel,
                limit=arguments.get("limit", 100),
                oldest=arguments.get("oldest"),
                latest=arguments.get("latest"),
                inclusive=arguments.get("inclusive", False),
            )
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"Retrieved {len(result['messages'])} messages from channel {channel}:\n\n"
                        f"{json.dumps(result, indent=2)}"
                    ),
                )
            ]

        if operation == "get_replies":
            channel = arguments.get("channel")
            thread_ts = arguments.get("thread_ts")
            if not channel or not thread_ts:
                raise ValueError(
                    "get_replies operation requires 'channel' and 'thread_ts' parameters"
                )

            result = await conversations.get_replies(
                channel=channel,
                thread_ts=thread_ts,
                limit=arguments.get("limit", 100),
                oldest=arguments.get("oldest"),
                latest=arguments.get("latest"),
                inclusive=arguments.get("inclusive", False),
            )
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"Retrieved {len(result['messages'])} replies from thread {thread_ts}:\n\n"
                        f"{json.dumps(result, indent=2)}"
                    ),
                )
            ]

        if operation == "post_message":
            channel = arguments.get("channel")
            text = arguments.get("text")
            if not channel or not text:
                raise ValueError("post_message requires 'channel' and 'text' parameters")

            result = await conversations.post_message(
                channel=channel, text=text, thread_ts=arguments.get("thread_ts")
            )
            return [
                types.TextContent(
                    type="text", text=f"Message posted:\n\n{json.dumps(result, indent=2)}"
                )
            ]

        if operation == "list_channels":
            channels = await conversations.list_channels(
                types=arguments.get("types"),
                exclude_archived=arguments.get("exclude_archived", True),
                member_only=arguments.get("member_only", True),
                limit=arguments.get("limit", 100),
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"Found {len(channels)} channels:\n\n{json.dumps(channels, indent=2)}",
                )
            ]

        if operation == "create_channel":
            name = arguments.get("name")
            if not name:
                raise ValueError("create_channel requires 'name' parameter")

            result = await conversations.create_channel(
                name=name, is_private=arguments.get("is_private", False)
            )
            return [
                types.TextContent(
                    type="text", text=f"Channel created:\n\n{json.dumps(result, indent=2)}"
                )
            ]

        if operation == "archive_channel":
            channel = arguments.get("channel")
            if not channel:
                raise ValueError("archive_channel requires 'channel' parameter")

            await conversations.archive_channel(channel=channel)
            return [types.TextContent(type="text", text=f"Channel {channel} archived successfully")]

        raise ValueError(f"Unknown conversations operation: {operation}")

    async def _handle_users(
        self, operation: str | None, arguments: Dict[str, Any]
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle slack_users tool operations."""
        users = await self._get_users()

        if operation == "list_users":
            user_list = await users.list_users(limit=arguments.get("limit", 100))
            return [
                types.TextContent(
                    type="text",
                    text=f"Found {len(user_list)} users:\n\n{json.dumps(user_list, indent=2)}",
                )
            ]

        if operation == "get_user":
            user = await users.get_user(
                user_id=arguments.get("user_id"), email=arguments.get("email")
            )
            return [
                types.TextContent(
                    type="text", text=f"User profile:\n\n{json.dumps(user, indent=2)}"
                )
            ]

        if operation == "get_presence":
            user_id = arguments.get("user_id")
            if not user_id:
                raise ValueError("get_presence requires 'user_id' parameter")

            presence = await users.get_presence(user_id=user_id)
            return [
                types.TextContent(
                    type="text", text=f"User presence:\n\n{json.dumps(presence, indent=2)}"
                )
            ]

        if operation == "search_users":
            query = arguments.get("query")
            if not query:
                raise ValueError("search_users requires 'query' parameter")

            results = await users.search_users(query=query)
            return [
                types.TextContent(
                    type="text",
                    text=f"Found {len(results)} users:\n\n{json.dumps(results, indent=2)}",
                )
            ]

        raise ValueError(f"Unknown users operation: {operation}")

    async def _handle_files(
        self, operation: str | None, arguments: Dict[str, Any]
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle slack_files tool operations."""
        files = await self._get_files()

        if operation == "upload":
            file_path = arguments.get("file_path")
            if not file_path:
                raise ValueError("upload operation requires 'file_path' parameter")

            result = await files.upload_file(
                file_path=file_path,
                channels=arguments.get("channels"),
                title=arguments.get("title"),
                initial_comment=arguments.get("initial_comment"),
                thread_ts=arguments.get("thread_ts"),
            )
            return [
                types.TextContent(
                    type="text", text=f"File uploaded:\n\n{json.dumps(result, indent=2)}"
                )
            ]

        if operation == "list_files":
            file_list = await files.list_files(
                channel=arguments.get("channel"),
                user=arguments.get("user"),
                types=arguments.get("types"),
                limit=arguments.get("limit", 100),
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"Found {len(file_list)} files:\n\n{json.dumps(file_list, indent=2)}",
                )
            ]

        if operation == "get_file_info":
            file_id = arguments.get("file_id")
            if not file_id:
                raise ValueError("get_file_info requires 'file_id' parameter")

            file_info = await files.get_file_info(file_id=file_id)
            return [
                types.TextContent(
                    type="text", text=f"File info:\n\n{json.dumps(file_info, indent=2)}"
                )
            ]

        if operation == "delete_file":
            file_id = arguments.get("file_id")
            if not file_id:
                raise ValueError("delete_file requires 'file_id' parameter")

            await files.delete_file(file_id=file_id)
            return [types.TextContent(type="text", text=f"File {file_id} deleted successfully")]

        raise ValueError(f"Unknown files operation: {operation}")

    async def _handle_workspace(
        self, operation: str | None, arguments: Dict[str, Any]
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle slack_workspace tool operations."""
        if operation == "get_team_info":
            workspace_ops = await self._get_workspace_ops()
            team_info = await workspace_ops.get_team_info()
            return [
                types.TextContent(
                    type="text", text=f"Team info:\n\n{json.dumps(team_info, indent=2)}"
                )
            ]

        if operation == "list_emoji":
            workspace_ops = await self._get_workspace_ops()
            emoji_list = await workspace_ops.list_emoji()
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"Found {len(emoji_list)} custom emoji:\n\n"
                        f"{json.dumps(emoji_list, indent=2)}"
                    ),
                )
            ]

        if operation == "get_stats":
            workspace_ops = await self._get_workspace_ops()
            stats = await workspace_ops.get_workspace_stats()
            return [
                types.TextContent(
                    type="text", text=f"Workspace stats:\n\n{json.dumps(stats, indent=2)}"
                )
            ]

        if operation == "list_workspaces":
            workspaces = self.workspace_manager.list_workspaces()
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"Found {len(workspaces)} workspaces:\n\n"
                        f"{json.dumps(workspaces, indent=2)}"
                    ),
                )
            ]

        if operation == "switch_workspace":
            workspace_name = arguments.get("workspace_name")
            if not workspace_name:
                raise ValueError("switch_workspace requires 'workspace_name' parameter")

            self.workspace_manager.switch_workspace(workspace_name)
            # Reset client and managers to use new workspace
            self._client = None
            self._conversations = None
            self._users = None
            self._files = None
            self._workspace_ops = None
            return [
                types.TextContent(
                    type="text", text=f"Switched to workspace: {workspace_name}"
                )
            ]

        if operation == "get_active_workspace":
            active = self.workspace_manager.get_active_workspace()
            return [
                types.TextContent(
                    type="text", text=f"Active workspace:\n\n{json.dumps(active, indent=2)}"
                )
            ]

        raise ValueError(f"Unknown workspace operation: {operation}")

    def get_server_info(self) -> Dict[str, str]:
        """
        Get server metadata.

        Returns:
            Dictionary with server name and version
        """
        return {"name": self.server_name, "version": self.server_version}
