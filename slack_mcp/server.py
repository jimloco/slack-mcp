"""
MCP server STDIO transport setup.

Handles server initialization, signal handling, and STDIO communication.
"""

import logging
import os
import signal
from typing import Any

from dotenv import load_dotenv
from mcp.server.stdio import stdio_server

from slack_mcp.mcp_server import SlackMCPServer
from slack_mcp.workspace_manager import WorkspaceManager

logger = logging.getLogger(__name__)


def signal_handler(sig: int, _frame: Any) -> None:
    """
    Handle termination signals for graceful shutdown.

    Args:
        sig: Signal number
        _frame: Current stack frame (unused)
    """
    logger.info("Received signal %s, shutting down gracefully...", sig)
    signal.signal(sig, signal.SIG_DFL)
    os.kill(os.getpid(), sig)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


async def run() -> None:
    """
    Main MCP server entry point.

    Initializes workspace manager, MCP server, and starts STDIO transport.

    Raises:
        ConfigError: If configuration is invalid
        RuntimeError: If server fails to start
    """
    try:
        logger.info("🚀 Initializing Slack MCP Server")

        # Load environment variables (if .env file exists)
        load_dotenv()
        if os.getenv("DEBUG"):
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")

        # Initialize workspace manager
        workspace_manager = WorkspaceManager()
        logger.info("✅ Workspace manager initialized")

        # Try to load current workspace config to validate setup
        current_workspace = workspace_manager.get_current_workspace()
        logger.info("📋 Current workspace: %s", current_workspace)

        # Initialize MCP server
        mcp_server = SlackMCPServer(workspace_manager)
        mcp_server.register_tools()

        server_info = mcp_server.get_server_info()
        logger.info("📋 Server: %s v%s", server_info["name"], server_info["version"])

        # Start STDIO server
        async with stdio_server() as (read_stream, write_stream):
            logger.info("🎯 MCP server running on STDIO transport")
            await mcp_server.app.run(
                read_stream,
                write_stream,
                mcp_server.app.create_initialization_options(),
            )

    except Exception as error:
        logger.error("❌ Server error: %s", error, exc_info=True)
        raise
