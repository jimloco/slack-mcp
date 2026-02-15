"""
Tests for enhanced WorkspaceManager functionality (Phase 3).
"""

import pytest
from unittest.mock import Mock, patch

from slack_mcp.workspace_manager import WorkspaceManager
from slack_mcp.config import ConfigError


class TestWorkspaceManagerEnhanced:
    """Tests for enhanced WorkspaceManager functionality."""

    def test_get_active_workspace_success(self) -> None:
        """Test getting active workspace details."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.get_default_workspace") as mock_default:
            mock_default.return_value = "test-workspace"
            with patch("slack_mcp.workspace_manager.load_workspace_config") as mock_load:
                mock_load.return_value = {
                    "token": "xoxp-test",
                    "workspace_name": "Test Workspace",
                    "workspace_id": "T123",
                    "default": True,
                }

                result = manager.get_active_workspace()

                assert result["name"] == "test-workspace"
                assert result["workspace_name"] == "Test Workspace"
                assert result["workspace_id"] == "T123"
                assert result["is_default"] is True

    def test_get_active_workspace_with_explicit_workspace(self) -> None:
        """Test getting active workspace after explicit switch."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.load_workspace_config") as mock_load:
            mock_load.return_value = {
                "token": "xoxp-test",
                "workspace_name": "Other Workspace",
                "workspace_id": "T456",
                "default": False,
            }

            manager.switch_workspace("other-workspace")
            result = manager.get_active_workspace()

            assert result["name"] == "other-workspace"
            assert result["workspace_name"] == "Other Workspace"
            assert result["is_default"] is False

    def test_list_workspaces_success(self) -> None:
        """Test listing all workspaces."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.list_available_workspaces") as mock_list:
            mock_list.return_value = ["workspace1", "workspace2"]
            with patch("slack_mcp.workspace_manager.load_workspace_config") as mock_load:
                mock_load.side_effect = [
                    {
                        "token": "xoxp-1",
                        "workspace_name": "Workspace 1",
                        "workspace_id": "T111",
                        "default": True,
                    },
                    {
                        "token": "xoxp-2",
                        "workspace_name": "Workspace 2",
                        "workspace_id": "T222",
                        "default": False,
                    },
                ]

                result = manager.list_workspaces()

                assert len(result) == 2
                assert result[0]["name"] == "workspace1"
                assert result[0]["workspace_name"] == "Workspace 1"
                assert result[0]["is_default"] is True
                assert result[1]["name"] == "workspace2"
                assert result[1]["is_default"] is False

    def test_list_workspaces_with_errors(self) -> None:
        """Test listing workspaces with some failing to load."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.list_available_workspaces") as mock_list:
            mock_list.return_value = ["good-workspace", "bad-workspace"]
            with patch("slack_mcp.workspace_manager.load_workspace_config") as mock_load:
                mock_load.side_effect = [
                    {"token": "xoxp-1", "workspace_name": "Good"},
                    ConfigError("Invalid config"),
                ]

                result = manager.list_workspaces()

                assert len(result) == 2
                assert result[0]["name"] == "good-workspace"
                assert "error" not in result[0]
                assert result[1]["name"] == "bad-workspace"
                assert "error" in result[1]
                assert "Invalid config" in result[1]["error"]

    def test_switch_workspace_success(self) -> None:
        """Test successful workspace switching."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.get_default_workspace") as mock_default:
            mock_default.return_value = "default-workspace"
            with patch("slack_mcp.workspace_manager.load_workspace_config") as mock_load:
                mock_load.side_effect = [
                    {"token": "xoxp-default"},
                    {"token": "xoxp-other"},
                ]

                # Initially on default workspace
                current = manager.get_current_workspace()
                assert current == "default-workspace"

                # Switch to other workspace
                manager.switch_workspace("other-workspace")
                current = manager.get_current_workspace()
                assert current == "other-workspace"

    def test_switch_workspace_invalid(self) -> None:
        """Test switching to invalid workspace."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.load_workspace_config") as mock_load:
            mock_load.side_effect = ConfigError("Workspace not found")

            with pytest.raises(ConfigError, match="Workspace not found"):
                manager.switch_workspace("nonexistent-workspace")

    def test_get_current_workspace_uses_default(self) -> None:
        """Test that get_current_workspace uses default when none set."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.get_default_workspace") as mock_default:
            mock_default.return_value = "default-workspace"

            current = manager.get_current_workspace()

            assert current == "default-workspace"
            mock_default.assert_called_once()

    def test_clear_cache_all(self) -> None:
        """Test clearing all workspace cache."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.load_workspace_config") as mock_load:
            mock_load.return_value = {"token": "xoxp-test"}

            # Load a workspace to populate cache
            _ = manager.get_workspace_config("test-workspace")
            assert "test-workspace" in manager._workspace_configs

            # Clear all cache
            manager.clear_cache()
            assert len(manager._workspace_configs) == 0

    def test_clear_cache_specific_workspace(self) -> None:
        """Test clearing cache for specific workspace."""
        manager = WorkspaceManager()

        with patch("slack_mcp.workspace_manager.load_workspace_config") as mock_load:
            mock_load.return_value = {"token": "xoxp-test"}

            # Load two workspaces
            _ = manager.get_workspace_config("workspace1")
            _ = manager.get_workspace_config("workspace2")
            assert len(manager._workspace_configs) == 2

            # Clear cache for workspace1
            manager.clear_cache("workspace1")
            assert "workspace1" not in manager._workspace_configs
            assert "workspace2" in manager._workspace_configs
