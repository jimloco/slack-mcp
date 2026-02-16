# Slack MCP Server

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-1.7+-purple.svg)](https://python-poetry.org/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Code Quality](https://img.shields.io/badge/pylint-10.0/10-brightgreen.svg)](https://www.pylint.org/)

> **⚠️ DISCLAIMER: This project is 100% vibe coded by AI. Buyer beware!**
>
> This entire codebase was generated through AI-assisted development using Claude Code. While it passes all quality gates (Pylint 10/10, mypy strict, 67 tests), security audits (Bandit, pip-audit), and has comprehensive documentation, it has not been battle-tested in production environments. Use at your own risk and review the code before deploying to critical systems.

A Model Context Protocol (MCP) server that provides AI assistants with comprehensive access to Slack workspaces through user-level OAuth operations. Enables seamless integration of Slack conversations, users, files, and workspace operations into AI-assisted workflows.

## Features

### 🔧 Four Thematic MCP Tools

**slack_conversations** - Comprehensive message and channel operations
- Search messages across channels with filters
- Read conversation history from channels chronologically
- Read all replies in a thread
- Post messages to channels/DMs with Slack markdown
- Reply to threads maintaining conversation context
- List, create, and archive channels
- Manage channel members

**slack_users** - Workspace user directory and profiles
- List all workspace users with pagination
- Get detailed user profiles (name, title, email, timezone, status)
- Check user presence/online status
- Search users by name or email

**slack_files** - Document and media sharing automation
- Upload files to channels/DMs
- List files with filters (user, channel, date, type)
- Get file metadata and download URLs
- Delete user's files

**slack_workspace** - Team metadata and configuration
- Get workspace info (name, domain, icon, plan)
- List custom emoji
- Access workspace statistics

### ✨ Key Capabilities

- **Multi-Workspace Support**: Manage multiple Slack workspaces with easy configuration switching
- **User-Level Operations**: Authentic user actions (not bot operations)
- **Async Performance**: Non-blocking I/O for all Slack API calls
- **Rate Limit Handling**: Graceful handling of Slack API rate limits with exponential backoff
- **Type-Safe**: Full type hints with mypy strict validation
- **Secure**: OAuth tokens protected with 600 file permissions, never logged or exposed

## Installation

### Prerequisites

- Python 3.12 or higher
- Poetry 1.7 or higher
- A Slack workspace where you can create apps

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/slack-mcp.git
   cd slack-mcp
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Create a Slack App** (see [Slack App Setup](#slack-app-setup) below)

4. **Configure workspace credentials** (see [Configuration](#configuration) below)

## Slack App Setup

To use this MCP server, you need to create a Slack App and generate a User OAuth Token.

### ⚡ Quick Setup (Recommended)

Use our pre-configured app manifest for instant setup:

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From an app manifest"**
3. Select your workspace and click **"Next"**
4. Copy the YAML from **[docs/slack-manifest.md](docs/slack-manifest.md)** and paste it
5. Click **"Create"** → **"Install to Workspace"** → **"Allow"**
6. Copy the **User OAuth Token** (starts with `xoxp-`)

**Done!** All required scopes are pre-configured. Skip to [Configuration](#configuration).

### 📝 Manual Setup (Alternative)

If you prefer to configure manually:

#### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Enter app name (e.g., "MCP Assistant") and select your workspace
4. Click **"Create App"**

#### Step 2: Configure OAuth Scopes

1. In your app settings, go to **"OAuth & Permissions"**
2. Scroll to **"User Token Scopes"** (NOT Bot Token Scopes)
3. Add the following scopes:

   **Conversations:**
   - `channels:read` - View basic channel info
   - `channels:write` - Manage public channels
   - `channels:history` - View messages in public channels
   - `groups:read` - View basic private channel info
   - `groups:write` - Manage private channels
   - `groups:history` - View messages in private channels
   - `im:read` - View basic DM info
   - `im:write` - Send DMs
   - `im:history` - View DM messages
   - `mpim:read` - View group DM info
   - `mpim:history` - View group DM messages
   - `chat:write` - Post messages

   **Users:**
   - `users:read` - View workspace users
   - `users:read.email` - View user email addresses

   **Files:**
   - `files:read` - View files
   - `files:write` - Upload and manage files

   **Workspace:**
   - `team:read` - View workspace info
   - `emoji:read` - View custom emoji

#### Step 3: Install App and Generate Token

1. Scroll to **"OAuth Tokens for Your Workspace"**
2. Click **"Install to Workspace"**
3. Review permissions and click **"Allow"**
4. Copy the **User OAuth Token** (starts with `xoxp-`)

⚠️ **IMPORTANT**: This is a user-level token that acts as YOU. Keep it secure and never commit it to git.

## Configuration

### Create Configuration Directory

```bash
mkdir -p ~/.config/slack-mcp
chmod 700 ~/.config/slack-mcp
```

### Create Workspace Configuration File

Create a JSON file for each workspace: `~/.config/slack-mcp/{workspace-name}.json`

Example: `~/.config/slack-mcp/my-team.json`
```json
{
  "token": "xoxp-your-user-oauth-token-here",
  "workspace_id": "T01234567",
  "workspace_name": "My Team Workspace",
  "default": true
}
```

**Configuration Schema:**
- `token` (required): User OAuth token from Slack App (xoxp-...)
- `workspace_id` (optional): Slack workspace ID (T...)
- `workspace_name` (optional): Friendly name for the workspace
- `default` (optional): Set to `true` to make this the default workspace

### Secure Your Configuration

```bash
chmod 600 ~/.config/slack-mcp/*.json
```

This ensures only you can read the OAuth tokens.

## Usage with Claude Code

### Add MCP Server to Claude Code (User Level)

Add the MCP server to your user-level Claude Code configuration:

```bash
claude mcp add -s user slack-mcp -- poetry -C /absolute/path/to/slack-mcp run start-mcp
```

Replace `/absolute/path/to/slack-mcp` with the actual path to your cloned repository.

This adds the server to `~/.config/claude/mcp.json` for your user account.

### Test the Server

Restart Claude Code and try:

```
slack_workspace(operation='get_info')
```

You should see your workspace information returned.

## Usage Examples

### Search Messages

```python
slack_conversations(
  operation='search',
  query='from:@sarah project deadline',
  channel='C01234567'
)
```

### Read Channel History

```python
slack_conversations(
  operation='get_history',
  channel='C01234567',
  limit=100,
  oldest='1234567890.123456',  # optional: Unix timestamp
  latest='1234567900.123456',  # optional: Unix timestamp
  inclusive=False              # optional: include oldest/latest timestamps
)
```

### Read Thread Replies

```python
slack_conversations(
  operation='get_replies',
  channel='C01234567',
  thread_ts='1234567890.123456',
  limit=100
)
```

### Post a Message

```python
slack_conversations(
  operation='post_message',
  channel='C01234567',
  text='Hello from AI assistant! 👋'
)
```

### Reply to Thread

```python
slack_conversations(
  operation='post_message',
  channel='C01234567',
  text='Great point!',
  thread_ts='1234567890.123456'
)
```

### List Channels

```python
slack_conversations(
  operation='list_channels',
  types=['public', 'private']
)
```

### Get User Profile

```python
slack_users(
  operation='get_user',
  user_id='U01234567'
)
```

### Upload File

```python
slack_files(
  operation='upload',
  file_path='/path/to/document.pdf',
  channels=['C01234567'],
  title='Meeting Notes',
  initial_comment='Notes from today\'s sync'
)
```

### List Files

```python
slack_files(
  operation='list_files',
  channel='C01234567',
  types=['pdfs', 'images'],
  limit=20
)
```

### Get File Info

```python
slack_files(
  operation='get_file_info',
  file_id='F01234567'
)
```

### Delete File

```python
slack_files(
  operation='delete_file',
  file_id='F01234567'
)
```

### Get Workspace Info

```python
slack_workspace(
  operation='get_team_info'
)
```

### List Custom Emoji

```python
slack_workspace(
  operation='list_emoji'
)
```

### Get Workspace Statistics

```python
slack_workspace(
  operation='get_stats'
)
```

### List All Workspaces

```python
slack_workspace(
  operation='list_workspaces'
)
```

### Switch Workspace

```python
slack_workspace(
  operation='switch_workspace',
  workspace_name='other-team'
)
```

### Get Active Workspace

```python
slack_workspace(
  operation='get_active_workspace'
)
```

## Development

### Setup Development Environment

```bash
# Install dependencies including dev tools
poetry install

# Activate virtual environment
poetry shell
```

### Run Tests

```bash
# Run all tests with coverage
poetry run pytest --cov=slack_mcp

# Run specific test file
poetry run pytest tests/test_mcp_server.py

# Run with verbose output
poetry run pytest -v
```

### Code Quality Checks

```bash
# Linting (target: 10.00/10)
poetry run pylint slack_mcp

# Type checking
poetry run mypy slack_mcp --strict

# Security scanning
poetry run bandit -r slack_mcp

# Dependency audit
poetry run pip-audit

# Code formatting
poetry run black slack_mcp
```

### Run MCP Server Locally

```bash
# Run with Poetry
poetry run start-mcp

# Or directly with Python
poetry run python -m slack_mcp

# With debug logging
poetry run python -m slack_mcp --debug
```

### Test with MCP Inspector

```bash
# Install MCP Inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector

# Test the MCP server
mcp-inspector poetry -C /path/to/slack-mcp run start-mcp
```

## Project Structure

```
slack-mcp/
├── slack_mcp/
│   ├── __init__.py              # Package metadata
│   ├── __main__.py              # Entry point with run_main()
│   ├── server.py                # STDIO server setup with signal handlers
│   ├── mcp_server.py            # MCP server class and tool registration
│   ├── config.py                # Configuration management
│   ├── workspace_manager.py    # Multi-workspace configuration
│   ├── slack_client.py          # Slack API client wrapper
│   ├── conversations_manager.py # Conversations operations
│   ├── users_manager.py         # User operations
│   ├── files_manager.py         # File operations
│   └── workspace_operations.py # Workspace operations
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_mcp_server.py
│   ├── test_config.py
│   ├── test_workspace_manager.py
│   └── ...
├── docs/
│   ├── project-charter.md
│   ├── requirements.md
│   ├── functional-requirements.md
│   └── implementation.md
├── pyproject.toml               # Poetry configuration
├── poetry.lock                  # Dependency lock file
├── AGENTS.md                    # AI agent development guidelines
└── README.md                    # This file
```

## Troubleshooting

### OAuth Token Issues

**Error: "invalid_auth" or "token_revoked"**
- Your OAuth token may have expired or been revoked
- Generate a new User OAuth Token from your Slack App settings
- Update the token in your workspace config file

**Error: "missing_scope"**
- Your token doesn't have required OAuth scopes
- Go to your Slack App's "OAuth & Permissions" page
- Add the missing scopes under "User Token Scopes"
- Reinstall the app to your workspace
- Copy the new token to your config file

### Configuration Issues

**Error: "Config not found"**
- Ensure `~/.config/slack-mcp/{workspace}.json` exists
- Check the workspace name matches what you're trying to use

**Error: "Config must have 600 permissions"**
- Run: `chmod 600 ~/.config/slack-mcp/*.json`

### Rate Limiting

**Error: "rate_limited" or HTTP 429**
- Slack API has rate limits (Tier 3: ~1 request/second, Tier 4: ~100 requests/minute)
- The server implements exponential backoff automatically
- If you see this frequently, reduce API call frequency

### MCP Connection Issues

**Server not showing up in Claude Code**
- Verify the path in `claude mcp add` command is absolute and correct
- Check that Poetry is installed and accessible
- Try restarting Claude Code
- Check Claude Code logs for error messages

## Security Considerations

### OAuth Token Protection

- ✅ **Never commit tokens to git** - Config files are in .gitignore
- ✅ **Use 600 file permissions** - Only your user can read config files
- ✅ **Tokens are never logged** - Server excludes tokens from all logs
- ✅ **No token caching** - Tokens loaded fresh for each session

### Data Privacy

- ✅ **No local storage** - All Slack data is pass-through (no caching)
- ✅ **User permissions respected** - Can only access what your Slack account can access
- ✅ **STDIO transport only** - No network exposure (runs locally)

### Best Practices

- Regularly review your Slack App's OAuth scopes (remove unused scopes)
- Rotate OAuth tokens periodically
- Monitor your Slack App's usage in workspace admin panel
- Use separate Slack Apps for different purposes (not shared tokens)

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Read `AGENTS.md` for development standards
2. Ensure all tests pass: `poetry run pytest`
3. Maintain 10.00/10 pylint score: `poetry run pylint slack_mcp`
4. Add tests for new features (≥80% coverage required)
5. Update documentation as needed

## License

[Specify your license here]

## Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses [Slack Python SDK](https://slack.dev/python-slack-sdk/)
- Inspired by [jira-mcp](https://github.com/yourusername/jira-mcp) multi-workspace patterns

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
