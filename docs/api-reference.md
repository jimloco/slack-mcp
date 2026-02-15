# Slack MCP Server - API Reference

**Version**: 0.1.0
**Last Updated**: 2026-02-15

## Overview

The Slack MCP Server provides four thematic tools for interacting with Slack workspaces:

1. **slack_conversations** - Message and channel operations
2. **slack_users** - User profile and presence operations
3. **slack_files** - File upload and management operations
4. **slack_workspace** - Workspace metadata and multi-workspace operations

All tools follow the MCP tool calling convention with JSON-formatted responses.

---

## slack_conversations

Comprehensive message and channel operations for Slack conversations.

### Operations

#### search

Search for messages in the workspace.

**Parameters:**
- `query` (string, required): Search query text
- `channel` (string, optional): Channel ID to limit search (C..., G..., or D...)
- `limit` (integer, optional): Maximum results (default: 10, max: 100)

**Returns:**
- List of matching messages with metadata

**Example:**
```python
slack_conversations(
  operation='search',
  query='project deadline from:@sarah',
  channel='C01234567',
  limit=20
)
```

**Response:**
```json
{
  "matches": [
    {
      "text": "The project deadline is next Friday",
      "user": "U01234567",
      "username": "sarah",
      "ts": "1234567890.123456",
      "channel": {"id": "C01234567", "name": "general"},
      "permalink": "https://workspace.slack.com/archives/C01234567/p1234567890123456"
    }
  ]
}
```

#### post_message

Post a message to a channel or DM.

**Parameters:**
- `channel` (string, required): Channel ID (C..., G..., or D...)
- `text` (string, required): Message text (supports Slack markdown, max 40,000 chars)
- `thread_ts` (string, optional): Thread timestamp for replies

**Returns:**
- Posted message info including timestamp and permalink

**Example:**
```python
slack_conversations(
  operation='post_message',
  channel='C01234567',
  text='Hello team! 👋',
  thread_ts='1234567890.123456'  # Optional: reply in thread
)
```

**Response:**
```json
{
  "ok": true,
  "channel": "C01234567",
  "ts": "1234567890.654321",
  "message": {
    "text": "Hello team! 👋",
    "user": "U98765432"
  }
}
```

#### list_channels

List conversations (channels, DMs, groups) in the workspace.

**Parameters:**
- `types` (array of strings, optional): Channel types to include
  - Valid: `public_channel`, `private_channel`, `im`, `mpim`
  - Default: `["public_channel", "private_channel"]`
- `exclude_archived` (boolean, optional): Exclude archived channels (default: true)
- `limit` (integer, optional): Maximum results (default: 100)

**Returns:**
- List of channel info dictionaries

**Example:**
```python
slack_conversations(
  operation='list_channels',
  types=['public_channel', 'private_channel'],
  exclude_archived=True,
  limit=50
)
```

**Response:**
```json
{
  "channels": [
    {
      "id": "C01234567",
      "name": "general",
      "is_channel": true,
      "is_private": false,
      "is_member": true,
      "num_members": 42,
      "topic": {"value": "Company-wide announcements"}
    }
  ]
}
```

#### create_channel

Create a new channel.

**Parameters:**
- `name` (string, required): Channel name (lowercase, no spaces, max 80 chars)
- `is_private` (boolean, optional): Create private channel (default: false)

**Returns:**
- Created channel info

**Example:**
```python
slack_conversations(
  operation='create_channel',
  name='new-project',
  is_private=False
)
```

**Response:**
```json
{
  "id": "C98765432",
  "name": "new-project",
  "is_channel": true,
  "is_private": false,
  "creator": "U01234567"
}
```

#### archive_channel

Archive a channel.

**Parameters:**
- `channel` (string, required): Channel ID to archive

**Returns:**
- Success boolean

**Example:**
```python
slack_conversations(
  operation='archive_channel',
  channel='C98765432'
)
```

---

## slack_users

User profile and presence operations for workspace members.

### Operations

#### list_users

List all users in the workspace.

**Parameters:**
- `limit` (integer, optional): Maximum results (default: 100, max: 1000)

**Returns:**
- List of user profiles (excludes bots and deleted users by default)

**Example:**
```python
slack_users(
  operation='list_users',
  limit=200
)
```

**Response:**
```json
{
  "members": [
    {
      "id": "U01234567",
      "name": "sarah",
      "real_name": "Sarah Johnson",
      "profile": {
        "email": "sarah@example.com",
        "title": "Engineering Manager",
        "phone": "+1-555-1234",
        "display_name": "Sarah"
      },
      "tz": "America/Los_Angeles",
      "is_admin": false,
      "is_owner": false
    }
  ]
}
```

#### get_user

Get detailed user profile by ID or email.

**Parameters:**
- `user_id` (string, optional): User ID (U... or W...)
- `email` (string, optional): User email address

**Note:** Either `user_id` or `email` is required (not both).

**Returns:**
- User profile dictionary

**Example by ID:**
```python
slack_users(
  operation='get_user',
  user_id='U01234567'
)
```

**Example by Email:**
```python
slack_users(
  operation='get_user',
  email='sarah@example.com'
)
```

#### get_presence

Check user's presence status.

**Parameters:**
- `user_id` (string, required): User ID

**Returns:**
- Presence info (active/away)

**Example:**
```python
slack_users(
  operation='get_presence',
  user_id='U01234567'
)
```

**Response:**
```json
{
  "ok": true,
  "presence": "active",
  "online": true,
  "auto_away": false,
  "manual_away": false
}
```

#### search_users

Search users by name or email.

**Parameters:**
- `query` (string, required): Search query

**Returns:**
- List of matching users

**Example:**
```python
slack_users(
  operation='search_users',
  query='sarah'
)
```

---

## slack_files

File upload and management operations.

### Operations

#### upload

Upload a file to Slack.

**Parameters:**
- `file_path` (string, required): Path to file to upload
- `channels` (array of strings, optional): Channel IDs to share file in
- `title` (string, optional): File title
- `initial_comment` (string, optional): Comment to add with file
- `thread_ts` (string, optional): Thread timestamp for threaded uploads

**File Size Limit:** 10MB (enforced by server for safety)

**Returns:**
- Uploaded file info

**Example:**
```python
slack_files(
  operation='upload',
  file_path='/Users/me/documents/report.pdf',
  channels=['C01234567', 'C98765432'],
  title='Q4 Report',
  initial_comment='Here is the quarterly report'
)
```

**Response:**
```json
{
  "id": "F01234567",
  "name": "report.pdf",
  "title": "Q4 Report",
  "mimetype": "application/pdf",
  "size": 2048000,
  "url_private": "https://files.slack.com/...",
  "permalink": "https://workspace.slack.com/files/..."
}
```

#### list_files

List files in workspace with filters.

**Parameters:**
- `channel` (string, optional): Filter by channel ID
- `user` (string, optional): Filter by user ID
- `types` (array of strings, optional): File types to include
  - Valid: `all`, `spaces`, `snippets`, `images`, `gdocs`, `zips`, `pdfs`
  - Default: `all`
- `limit` (integer, optional): Maximum results (default: 100, max: 1000)

**Returns:**
- List of file info dictionaries

**Example:**
```python
slack_files(
  operation='list_files',
  channel='C01234567',
  types=['pdfs', 'images'],
  limit=50
)
```

#### get_file_info

Get detailed information about a file.

**Parameters:**
- `file_id` (string, required): File ID (F...)

**Returns:**
- File info dictionary

**Example:**
```python
slack_files(
  operation='get_file_info',
  file_id='F01234567'
)
```

#### delete_file

Delete a file.

**Parameters:**
- `file_id` (string, required): File ID to delete

**Returns:**
- Success boolean

**Example:**
```python
slack_files(
  operation='delete_file',
  file_id='F01234567'
)
```

---

## slack_workspace

Workspace metadata and multi-workspace management operations.

### Operations

#### get_team_info

Get workspace/team information.

**Parameters:**
None

**Returns:**
- Team info dictionary

**Example:**
```python
slack_workspace(
  operation='get_team_info'
)
```

**Response:**
```json
{
  "id": "T01234567",
  "name": "Acme Corp",
  "domain": "acmecorp",
  "email_domain": "acme.com",
  "icon": {
    "image_default": true,
    "image_68": "https://...",
    "image_132": "https://..."
  }
}
```

#### list_emoji

List custom emoji in workspace.

**Parameters:**
None

**Returns:**
- Dictionary mapping emoji names to image URLs

**Example:**
```python
slack_workspace(
  operation='list_emoji'
)
```

**Response:**
```json
{
  "party-parrot": "https://emoji.slack-edge.com/...",
  "custom-logo": "https://emoji.slack-edge.com/...",
  "success": "alias:white_check_mark"
}
```

#### get_stats

Get workspace statistics.

**Parameters:**
None

**Returns:**
- Workspace statistics (sampled for performance)

**Example:**
```python
slack_workspace(
  operation='get_stats'
)
```

**Response:**
```json
{
  "team_info": {"name": "Acme Corp", "id": "T01234567"},
  "user_count_sample": 15,
  "user_count_note": "Sample from first page only",
  "channel_count_sample": 8,
  "channel_count_note": "Sample from first page only",
  "emoji_count": 42
}
```

#### list_workspaces

List all configured workspaces.

**Parameters:**
None

**Returns:**
- List of workspace configurations

**Example:**
```python
slack_workspace(
  operation='list_workspaces'
)
```

**Response:**
```json
[
  {
    "name": "acme-corp",
    "workspace_name": "Acme Corp",
    "workspace_id": "T01234567",
    "is_current": true,
    "is_default": true
  },
  {
    "name": "other-team",
    "workspace_name": "Other Team",
    "workspace_id": "T98765432",
    "is_current": false,
    "is_default": false
  }
]
```

#### switch_workspace

Switch to a different workspace.

**Parameters:**
- `workspace_name` (string, required): Workspace name to switch to

**Returns:**
- Success message

**Example:**
```python
slack_workspace(
  operation='switch_workspace',
  workspace_name='other-team'
)
```

**Note:** This resets all manager instances to use the new workspace's OAuth token.

#### get_active_workspace

Get information about currently active workspace.

**Parameters:**
None

**Returns:**
- Active workspace info

**Example:**
```python
slack_workspace(
  operation='get_active_workspace'
)
```

**Response:**
```json
{
  "name": "acme-corp",
  "workspace_name": "Acme Corp",
  "workspace_id": "T01234567",
  "is_default": true
}
```

---

## Error Handling

All operations may return errors in the following format:

```json
{
  "error": "error_type",
  "message": "Human-readable error message"
}
```

### Common Error Types

**Authentication Errors:**
- `invalid_auth` - OAuth token is invalid
- `token_revoked` - OAuth token has been revoked
- `missing_scope` - Token missing required OAuth scope

**Validation Errors:**
- `invalid_channel_id` - Channel ID format invalid
- `invalid_user_id` - User ID format invalid
- `invalid_file_id` - File ID format invalid
- `file_not_found` - File path doesn't exist

**Rate Limiting:**
- `rate_limited` - Slack API rate limit exceeded

**Resource Errors:**
- `channel_not_found` - Channel doesn't exist
- `user_not_found` - User doesn't exist
- `file_too_large` - File exceeds size limit

---

## Data Types

### Channel ID
- Format: `C01234567` (public), `G01234567` (private), `D01234567` (DM)
- Length: 9-11 characters
- Prefix: C, G, or D

### User ID
- Format: `U01234567` or `W01234567`
- Length: 9-11 characters
- Prefix: U or W

### File ID
- Format: `F01234567`
- Length: 9-11 characters
- Prefix: F

### Timestamp
- Format: `"1234567890.123456"` (Unix timestamp with microseconds)
- Used for messages and threads

---

## Rate Limits

Slack API has tiered rate limits:

- **Tier 3 methods** (most operations): ~1 request/second
- **Tier 4 methods** (search, files): ~100 requests/minute

The server automatically detects rate limiting and returns user-friendly error messages with retry-after information.

---

## OAuth Scopes Required

Ensure your Slack App has these User Token Scopes:

**Conversations:**
- `channels:read`, `channels:write`, `channels:history`
- `groups:read`, `groups:write`, `groups:history`
- `im:read`, `im:write`, `im:history`
- `mpim:read`, `mpim:history`
- `chat:write`

**Users:**
- `users:read`, `users:read.email`

**Files:**
- `files:read`, `files:write`

**Workspace:**
- `team:read`, `emoji:read`

**Search:**
- `search:read` (for message search)

---

## Best Practices

1. **Pagination**: Use `limit` parameter to control result size
2. **Error Handling**: Always check for error responses
3. **Rate Limiting**: Implement backoff when receiving rate limit errors
4. **Channel IDs**: Use channel IDs (not names) for all operations
5. **File Sizes**: Check file size before upload (10MB limit enforced)
6. **Thread Replies**: Use `thread_ts` for threaded conversations
7. **Workspace Switching**: Reset state when switching workspaces

---

**Last Updated**: 2026-02-15
**API Version**: 0.1.0
