"""
Pytest configuration and fixtures for Slack MCP Server tests.

Provides common fixtures for testing configuration, workspace management,
and MCP server components.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

from slack_mcp.workspace_manager import WorkspaceManager
from slack_mcp.mcp_server import SlackMCPServer


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """
    Create a temporary configuration directory.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to temporary config directory
    """
    config_dir = tmp_path / ".config" / "slack-mcp"
    config_dir.mkdir(parents=True, mode=0o700)
    return config_dir


@pytest.fixture
def sample_workspace_config() -> Dict[str, Any]:
    """
    Create a sample workspace configuration.

    Returns:
        Dictionary with sample workspace config
    """
    return {
        "token": "xoxp-test-token-12345",
        "workspace_id": "T01234567",
        "workspace_name": "Test Workspace",
        "default": True
    }


@pytest.fixture
def workspace_config_file(
    temp_config_dir: Path,
    sample_workspace_config: Dict[str, Any]
) -> Path:
    """
    Create a workspace configuration file.

    Args:
        temp_config_dir: Temporary config directory
        sample_workspace_config: Sample config data

    Returns:
        Path to created config file
    """
    config_file = temp_config_dir / "test-workspace.json"
    with config_file.open("w", encoding="utf-8") as f:
        json.dump(sample_workspace_config, f)
    config_file.chmod(0o600)
    return config_file


@pytest.fixture
def workspace_manager() -> WorkspaceManager:
    """
    Create a WorkspaceManager instance for testing.

    Returns:
        WorkspaceManager instance
    """
    return WorkspaceManager()


@pytest.fixture
def mcp_server(workspace_manager: WorkspaceManager) -> SlackMCPServer:
    """
    Create a SlackMCPServer instance for testing.

    Args:
        workspace_manager: WorkspaceManager fixture

    Returns:
        SlackMCPServer instance
    """
    server = SlackMCPServer(workspace_manager)
    server.register_tools()
    return server


@pytest.fixture
def mock_slack_client() -> Mock:
    """
    Create a mock Slack API client.

    Returns:
        Mock Slack client
    """
    mock_client = Mock()
    mock_client.auth_test = Mock(return_value={
        "ok": True,
        "user_id": "U01234567",
        "team_id": "T01234567"
    })
    return mock_client
