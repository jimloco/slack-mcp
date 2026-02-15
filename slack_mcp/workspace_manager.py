"""
Workspace Manager for Slack MCP Server.

Manages multiple Slack workspace configurations and provides workspace switching.
"""

import logging
from typing import Dict, Any, Optional, cast

from slack_mcp.config import (
    load_workspace_config,
    list_available_workspaces,
    get_default_workspace,
    ConfigError,
)

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """
    Manages multiple Slack workspace configurations.

    Handles loading, caching, and switching between workspace configurations.
    """

    def __init__(self) -> None:
        """Initialize the workspace manager."""
        self._current_workspace: Optional[str] = None
        self._workspace_configs: Dict[str, Dict[str, Any]] = {}

    def get_current_workspace(self) -> str:
        """
        Get the name of the currently active workspace.

        Returns:
            Name of the current workspace

        Raises:
            ConfigError: If no workspace is set and none can be determined
        """
        if self._current_workspace is None:
            self._current_workspace = get_default_workspace()

        return self._current_workspace

    def get_workspace_config(self, workspace_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a workspace.

        Args:
            workspace_name: Name of workspace, or None for current workspace

        Returns:
            Workspace configuration dictionary

        Raises:
            ConfigError: If workspace not found or config invalid
        """
        if workspace_name is None:
            workspace_name = self.get_current_workspace()

        # Load from cache if available
        if workspace_name not in self._workspace_configs:
            config = load_workspace_config(workspace_name)
            self._workspace_configs[workspace_name] = config
            logger.info("Loaded and cached config for workspace: %s", workspace_name)

        return self._workspace_configs[workspace_name]

    def switch_workspace(self, workspace_name: str) -> None:
        """
        Switch to a different workspace.

        Args:
            workspace_name: Name of workspace to switch to

        Raises:
            ConfigError: If workspace not found
        """
        # Validate workspace exists by loading it
        _ = self.get_workspace_config(workspace_name)

        self._current_workspace = workspace_name
        logger.info("Switched to workspace: %s", workspace_name)

    def list_workspaces(self) -> list[Dict[str, Any]]:
        """
        List all available workspaces with metadata.

        Returns:
            List of workspace info dictionaries
        """
        workspaces = []
        workspace_names = list_available_workspaces()

        for name in workspace_names:
            try:
                config = self.get_workspace_config(name)
                workspaces.append(
                    {
                        "name": name,
                        "workspace_name": config.get("workspace_name", name),
                        "workspace_id": config.get("workspace_id", ""),
                        "is_current": name == self._current_workspace,
                        "is_default": config.get("default", False),
                    }
                )
            except ConfigError as error:
                logger.warning("Failed to load workspace %s: %s", name, error)
                workspaces.append(
                    {"name": name, "error": str(error), "is_current": False, "is_default": False}
                )

        return workspaces

    def get_active_workspace(self) -> Dict[str, Any]:
        """
        Get detailed information about the currently active workspace.

        Returns:
            Dictionary with current workspace details including name,
            workspace_name, workspace_id, and config metadata

        Raises:
            ConfigError: If no workspace is active or config invalid
        """
        current_name = self.get_current_workspace()
        config = self.get_workspace_config(current_name)

        return {
            "name": current_name,
            "workspace_name": config.get("workspace_name", current_name),
            "workspace_id": config.get("workspace_id", ""),
            "is_default": config.get("default", False),
        }

    def get_oauth_token(self, workspace_name: Optional[str] = None) -> str:
        """
        Get OAuth token for a workspace.

        Args:
            workspace_name: Name of workspace, or None for current workspace

        Returns:
            OAuth token string

        Raises:
            ConfigError: If workspace not found or token invalid
        """
        config = self.get_workspace_config(workspace_name)
        return cast(str, config["token"])

    def clear_cache(self, workspace_name: Optional[str] = None) -> None:
        """
        Clear cached workspace configuration.

        Args:
            workspace_name: Name of workspace to clear, or None to clear all
        """
        if workspace_name is None:
            self._workspace_configs.clear()
            logger.info("Cleared all workspace config cache")
        elif workspace_name in self._workspace_configs:
            del self._workspace_configs[workspace_name]
            logger.info("Cleared config cache for workspace: %s", workspace_name)
