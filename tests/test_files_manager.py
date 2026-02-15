"""
Tests for Slack files manager.
"""

import os
import tempfile
import pytest
from unittest.mock import AsyncMock, Mock

from slack_mcp.slack_client import SlackClient, SlackClientError
from slack_mcp.files_manager import FilesManager


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock Slack client."""
    client = Mock(spec=SlackClient)
    client.call_api = AsyncMock()
    return client


@pytest.fixture
def files_manager(mock_client: Mock) -> FilesManager:
    """Create FilesManager with mock client."""
    return FilesManager(mock_client)


@pytest.fixture
def temp_file() -> str:
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content")
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestFilesManager:
    """Tests for FilesManager class."""

    @pytest.mark.asyncio
    async def test_upload_file_success(
        self, files_manager: FilesManager, mock_client: Mock, temp_file: str
    ) -> None:
        """Test successful file upload."""
        mock_client.call_api.return_value = {
            "file": {"id": "F123", "name": "test.txt", "permalink": "https://..."}
        }

        result = await files_manager.upload_file(
            file_path=temp_file, channels=["C123"], title="Test File"
        )

        assert result["id"] == "F123"
        mock_client.call_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_missing_path(self, files_manager: FilesManager) -> None:
        """Test upload with empty file path."""
        with pytest.raises(SlackClientError, match="File path is required"):
            await files_manager.upload_file(file_path="")

    @pytest.mark.asyncio
    async def test_upload_file_not_found(self, files_manager: FilesManager) -> None:
        """Test upload with non-existent file."""
        with pytest.raises(SlackClientError, match="File not found"):
            await files_manager.upload_file(file_path="/nonexistent/file.txt")

    @pytest.mark.asyncio
    async def test_upload_file_invalid_channel(
        self, files_manager: FilesManager, temp_file: str
    ) -> None:
        """Test upload with invalid channel ID."""
        with pytest.raises(SlackClientError, match="Invalid channel ID format"):
            await files_manager.upload_file(file_path=temp_file, channels=["invalid"])

    @pytest.mark.asyncio
    async def test_list_files_success(
        self, files_manager: FilesManager, mock_client: Mock
    ) -> None:
        """Test successful file listing."""
        mock_client.call_api.return_value = {
            "files": [
                {"id": "F123", "name": "file1.txt"},
                {"id": "F456", "name": "file2.txt"},
            ],
            "paging": {"pages": 1},
        }

        results = await files_manager.list_files(limit=10)

        assert len(results) == 2
        assert results[0]["id"] == "F123"
        mock_client.call_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_files_with_pagination(
        self, files_manager: FilesManager, mock_client: Mock
    ) -> None:
        """Test file listing with pagination."""
        mock_client.call_api.side_effect = [
            {"files": [{"id": "F1", "name": "file1.txt"}], "paging": {"pages": 2}},
            {"files": [{"id": "F2", "name": "file2.txt"}], "paging": {"pages": 2}},
        ]

        results = await files_manager.list_files(limit=200)

        assert len(results) == 2
        assert mock_client.call_api.call_count == 2

    @pytest.mark.asyncio
    async def test_list_files_invalid_limit(self, files_manager: FilesManager) -> None:
        """Test listing with invalid limit."""
        with pytest.raises(SlackClientError, match="Limit must be between 1 and 1000"):
            await files_manager.list_files(limit=2000)

    @pytest.mark.asyncio
    async def test_list_files_invalid_types(self, files_manager: FilesManager) -> None:
        """Test listing with invalid file types."""
        with pytest.raises(SlackClientError, match="Invalid file types"):
            await files_manager.list_files(types=["invalid_type"])

    @pytest.mark.asyncio
    async def test_list_files_with_filters(
        self, files_manager: FilesManager, mock_client: Mock
    ) -> None:
        """Test file listing with filters."""
        mock_client.call_api.return_value = {
            "files": [{"id": "F123", "name": "image.png"}],
            "paging": {"pages": 1},
        }

        results = await files_manager.list_files(
            channel="C123", user="U456", types=["images"], limit=10
        )

        assert len(results) == 1
        call_args = mock_client.call_api.call_args
        assert call_args.kwargs["channel"] == "C123"
        assert call_args.kwargs["user"] == "U456"
        assert call_args.kwargs["types"] == "images"

    @pytest.mark.asyncio
    async def test_get_file_info_success(
        self, files_manager: FilesManager, mock_client: Mock
    ) -> None:
        """Test successful file info retrieval."""
        mock_client.call_api.return_value = {
            "file": {
                "id": "F123",
                "name": "test.txt",
                "size": 1024,
                "mimetype": "text/plain",
            }
        }

        result = await files_manager.get_file_info(file_id="F123")

        assert result["id"] == "F123"
        assert result["size"] == 1024
        mock_client.call_api.assert_called_once_with("files.info", file="F123")

    @pytest.mark.asyncio
    async def test_get_file_info_empty_id(self, files_manager: FilesManager) -> None:
        """Test get_file_info with empty file ID."""
        with pytest.raises(SlackClientError, match="File ID is required"):
            await files_manager.get_file_info(file_id="")

    @pytest.mark.asyncio
    async def test_get_file_info_invalid_id_format(
        self, files_manager: FilesManager
    ) -> None:
        """Test get_file_info with invalid ID format."""
        with pytest.raises(SlackClientError, match="Invalid file ID format"):
            await files_manager.get_file_info(file_id="invalid")

    @pytest.mark.asyncio
    async def test_delete_file_success(
        self, files_manager: FilesManager, mock_client: Mock
    ) -> None:
        """Test successful file deletion."""
        mock_client.call_api.return_value = {"ok": True}

        result = await files_manager.delete_file(file_id="F123")

        assert result is True
        mock_client.call_api.assert_called_once_with("files.delete", file="F123")

    @pytest.mark.asyncio
    async def test_delete_file_empty_id(self, files_manager: FilesManager) -> None:
        """Test delete with empty file ID."""
        with pytest.raises(SlackClientError, match="File ID is required"):
            await files_manager.delete_file(file_id="")

    @pytest.mark.asyncio
    async def test_delete_file_invalid_id_format(
        self, files_manager: FilesManager
    ) -> None:
        """Test delete with invalid ID format."""
        with pytest.raises(SlackClientError, match="Invalid file ID format"):
            await files_manager.delete_file(file_id="invalid")
