"""
Configuration management for Slack MCP Server.

Handles loading and validation of workspace configurations from ~/.config/slack-mcp/
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, cast

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Exception raised for configuration errors."""


def get_config_dir() -> Path:
    """
    Get the configuration directory path.

    Returns:
        Path to ~/.config/slack-mcp/ directory

    Raises:
        ConfigError: If directory doesn't exist or has incorrect permissions
    """
    config_dir = Path.home() / ".config" / "slack-mcp"

    if not config_dir.exists():
        raise ConfigError(
            f"Configuration directory not found: {config_dir}\n"
            "Please create it with: mkdir -p ~/.config/slack-mcp"
        )

    # Check directory permissions (should be 700)
    dir_mode = config_dir.stat().st_mode & 0o777
    if dir_mode != 0o700:
        logger.warning("Config directory has permissions %o, should be 700 for security", dir_mode)

    return config_dir


def load_workspace_config(workspace_name: str) -> Dict[str, Any]:
    """
    Load workspace configuration from file.

    Args:
        workspace_name: Name of the workspace config file (without .json)

    Returns:
        Dictionary containing workspace configuration

    Raises:
        ConfigError: If config file not found or invalid
    """
    config_dir = get_config_dir()
    config_file = config_dir / f"{workspace_name}.json"

    if not config_file.exists():
        raise ConfigError(
            f"Workspace config not found: {config_file}\n"
            f"Available configs: {list_available_workspaces()}"
        )

    # Check file permissions (should be 600)
    file_mode = config_file.stat().st_mode & 0o777
    if file_mode != 0o600:
        raise ConfigError(
            f"Config file {config_file} must have 600 permissions\n"
            f"Current permissions: {oct(file_mode)}\n"
            f"Fix with: chmod 600 {config_file}"
        )

    # Load and validate configuration
    try:
        with config_file.open("r", encoding="utf-8") as f:
            config = cast(Dict[str, Any], json.load(f))
    except json.JSONDecodeError as error:
        raise ConfigError(f"Invalid JSON in config file {config_file}: {error}") from error

    # Validate required fields
    if "token" not in config:
        raise ConfigError(f"Config file {config_file} missing required 'token' field")

    if not isinstance(config["token"], str) or not config["token"].startswith("xoxp-"):
        raise ConfigError(
            f"Invalid token format in {config_file} - must be user OAuth token (xoxp-...)"
        )

    logger.info("Loaded configuration for workspace: %s", workspace_name)
    # Never log the actual token value

    return config


def list_available_workspaces() -> list[str]:
    """
    List all available workspace configurations.

    Returns:
        List of workspace names (config file names without .json extension)

    Raises:
        ConfigError: If config directory doesn't exist
    """
    config_dir = get_config_dir()
    workspace_files = config_dir.glob("*.json")
    return [f.stem for f in workspace_files]


def get_default_workspace() -> str:
    """
    Get the default workspace name.

    Returns:
        Name of the workspace marked as default, or first available workspace

    Raises:
        ConfigError: If no workspaces are configured
    """
    workspaces = list_available_workspaces()

    if not workspaces:
        raise ConfigError(
            "No workspace configurations found in ~/.config/slack-mcp/\n"
            "Please create a workspace config file. See README.md for instructions."
        )

    # Check each workspace for "default": true
    for workspace_name in workspaces:
        try:
            config = load_workspace_config(workspace_name)
            if config.get("default", False):
                logger.info("Using default workspace: %s", workspace_name)
                return workspace_name
        except ConfigError:
            continue

    # No default found, use first available
    default = workspaces[0]
    logger.info("No default workspace configured, using: %s", default)
    return default
