"""
Main entry point for the Slack MCP Server.

Provides command-line interface and async wrapper for the MCP server.
"""

import os
import sys
import logging
import asyncio
import argparse

from slack_mcp.server import run

logger = logging.getLogger("slack_mcp")
logger.setLevel(logging.INFO)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Slack MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m slack_mcp              # Run with stdio transport
  python -m slack_mcp --debug      # Run with debug logging

This MCP server provides tools for Slack workspace integration including
conversations, users, files, and workspace operations.

For setup instructions, see README.md
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Transport type (currently only stdio is supported)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


async def main() -> None:
    """
    Main entry point.

    Parses arguments and starts the MCP server.

    Raises:
        ConfigError: If configuration is invalid
        RuntimeError: If server fails to start
    """
    try:
        args = parse_args()

        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
            os.environ["DEBUG"] = "true"

        logger.info("🚀 Starting Slack MCP Server")
        logger.info("📡 Transport: %s", args.transport)

        await run()

    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested by user")
        sys.exit(0)
    except Exception as error:  # pylint: disable=broad-exception-caught
        # Catch all exceptions at main entry point for graceful error handling
        logger.error("❌ Fatal error: %s", error, exc_info=True)
        sys.exit(1)


def run_main() -> None:
    """
    Synchronous wrapper for async main.

    Used as console script entry point by Poetry.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    run_main()
