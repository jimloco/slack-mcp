# Workspace Configuration Schema

**Version**: 0.1.0
**Last Updated**: 2026-02-15

## Overview

Slack MCP Server uses JSON configuration files stored in `~/.config/slack-mcp/` to manage workspace connections. Each workspace has its own configuration file.

## Configuration File Location

```
~/.config/slack-mcp/{workspace-name}.json
```

**Examples:**
- `~/.config/slack-mcp/acme-corp.json`
- `~/.config/slack-mcp/personal-workspace.json`
- `~/.config/slack-mcp/client-team.json`

## Required Permissions

All configuration files **must** have `600` permissions (read/write for owner only):

```bash
chmod 600 ~/.config/slack-mcp/*.json
```

This ensures OAuth tokens are protected from unauthorized access.

## Schema Definition

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["token"],
  "properties": {
    "token": {
      "type": "string",
      "pattern": "^xoxp-[0-9]+-[0-9]+-[0-9]+-[a-f0-9]+$",
      "description": "Slack User OAuth Token"
    },
    "workspace_id": {
      "type": "string",
      "pattern": "^T[A-Z0-9]+$",
      "description": "Slack Workspace/Team ID"
    },
    "workspace_name": {
      "type": "string",
      "description": "Friendly display name for workspace"
    },
    "default": {
      "type": "boolean",
      "default": false,
      "description": "Whether this is the default workspace"
    }
  }
}
```

### Field Descriptions

#### `token` (required)

**Type:** string
**Pattern:** `^xoxp-[0-9]+-[0-9]+-[0-9]+-[a-f0-9]+$`
**Description:** Slack User OAuth Token

The OAuth token for accessing Slack API as a user. Must start with `xoxp-` (user token prefix).

**How to Obtain:**
1. Create a Slack App at https://api.slack.com/apps
2. Add required User Token Scopes in "OAuth & Permissions"
3. Install app to your workspace
4. Copy the "User OAuth Token" (starts with `xoxp-`)

**Security:**
- Never commit this token to version control
- Never share this token
- Rotate tokens periodically
- Use 600 file permissions to protect

**Example:**
```json
{
  "token": "xoxp-YOUR-USER-OAUTH-TOKEN-HERE"
}
```

#### `workspace_id` (optional)

**Type:** string
**Pattern:** `^T[A-Z0-9]+$`
**Description:** Slack Workspace/Team ID

The unique identifier for your Slack workspace. Starts with `T`.

**How to Find:**
1. In Slack, go to Workspace Settings
2. Look for "Workspace ID" or "Team ID"
3. Or use the `team.info` API after authentication

**Example:**
```json
{
  "workspace_id": "T01234567"
}
```

#### `workspace_name` (optional)

**Type:** string
**Description:** Friendly display name for the workspace

A human-readable name for the workspace. Used in multi-workspace listings and logs.

**Example:**
```json
{
  "workspace_name": "Acme Corporation"
}
```

#### `default` (optional)

**Type:** boolean
**Default:** `false`
**Description:** Whether this workspace should be the default

If `true`, this workspace will be used when no specific workspace is requested. Only one workspace should have `default: true`.

**Example:**
```json
{
  "default": true
}
```

## Complete Examples

### Minimal Configuration

```json
{
  "token": "xoxp-YOUR-USER-OAUTH-TOKEN-HERE"
}
```

This is the minimum valid configuration. The server will work with just the OAuth token.

### Standard Configuration

```json
{
  "token": "xoxp-YOUR-USER-OAUTH-TOKEN-HERE",
  "workspace_id": "T01234567",
  "workspace_name": "Acme Corporation"
}
```

Recommended configuration including workspace identification.

### Default Workspace Configuration

```json
{
  "token": "xoxp-YOUR-USER-OAUTH-TOKEN-HERE",
  "workspace_id": "T01234567",
  "workspace_name": "Acme Corporation",
  "default": true
}
```

Configuration for the default workspace used when no workspace is specified.

## Multi-Workspace Setup

### Example: Multiple Workspaces

**File:** `~/.config/slack-mcp/acme-corp.json`
```json
{
  "token": "xoxp-ACME-CORP-USER-OAUTH-TOKEN",
  "workspace_id": "T11111111",
  "workspace_name": "Acme Corporation",
  "default": true
}
```

**File:** `~/.config/slack-mcp/client-team.json`
```json
{
  "token": "xoxp-CLIENT-TEAM-USER-OAUTH-TOKEN",
  "workspace_id": "T22222222",
  "workspace_name": "Client Team Workspace"
}
```

**File:** `~/.config/slack-mcp/personal.json`
```json
{
  "token": "xoxp-PERSONAL-WORKSPACE-USER-OAUTH-TOKEN",
  "workspace_id": "T33333333",
  "workspace_name": "Personal Workspace"
}
```

### Workspace Selection Priority

1. **Explicitly specified workspace**: When using `slack_workspace(operation='switch_workspace', workspace_name='...')`
2. **Default workspace**: Workspace with `"default": true`
3. **First alphabetically**: If no default set, first workspace file alphabetically

## Configuration Validation

The server validates configurations on load:

### Valid Token Format
- Must start with `xoxp-` (user token)
- Must match pattern: `xoxp-{numbers}-{numbers}-{numbers}-{hex}`

**Invalid tokens will be rejected:**
- ❌ `xoxb-...` (bot token, not user token)
- ❌ `xoxa-...` (app-level token)
- ❌ Tokens not matching the pattern

### File Permissions
- Must be exactly `600` (rw-------)
- Owner read/write only
- No group or other permissions

**Invalid permissions will be rejected:**
- ❌ `644` (world-readable)
- ❌ `755` (world-readable and executable)
- ❌ `666` (world-writable)

### JSON Syntax
- Must be valid JSON
- No trailing commas
- No comments (JSON doesn't support comments)

## Security Best Practices

### 1. Token Protection

**DO:**
- ✅ Store tokens only in `~/.config/slack-mcp/` with 600 permissions
- ✅ Use separate tokens for each workspace
- ✅ Rotate tokens periodically (every 90 days recommended)
- ✅ Revoke tokens when no longer needed

**DON'T:**
- ❌ Commit tokens to git repositories
- ❌ Share tokens via email or messaging
- ❌ Use the same token across multiple machines
- ❌ Store tokens in environment variables

### 2. File Permissions

```bash
# Correct permissions
chmod 700 ~/.config/slack-mcp           # Directory: owner only
chmod 600 ~/.config/slack-mcp/*.json    # Files: owner read/write only

# Verify permissions
ls -la ~/.config/slack-mcp/
# Should show: drwx------ for directory
#             -rw------- for files
```

### 3. Token Monitoring

- Regularly review active tokens in Slack App settings
- Check "Workspace Apps" in Slack admin for installed apps
- Monitor API usage in your Slack App dashboard
- Remove unused workspace configurations

### 4. Workspace Isolation

- Use separate Slack Apps for different purposes
- Don't share OAuth tokens between workspaces
- Create workspace-specific tokens with minimal required scopes

## Troubleshooting

### Error: "Config not found"

**Cause:** No configuration file exists for the workspace.

**Solution:**
```bash
# List available workspaces
ls ~/.config/slack-mcp/

# Create configuration file
cat > ~/.config/slack-mcp/my-workspace.json << 'EOF'
{
  "token": "xoxp-your-token-here",
  "workspace_name": "My Workspace"
}
EOF

# Set correct permissions
chmod 600 ~/.config/slack-mcp/my-workspace.json
```

### Error: "Config must have 600 permissions"

**Cause:** Configuration file has incorrect permissions.

**Solution:**
```bash
chmod 600 ~/.config/slack-mcp/*.json
```

### Error: "Invalid OAuth token format"

**Cause:** Token doesn't match required pattern (must start with `xoxp-`).

**Solution:**
1. Verify you copied the **User OAuth Token** (not Bot Token)
2. Ensure token starts with `xoxp-`
3. Check for extra whitespace or line breaks in the token
4. Regenerate token if necessary

### Error: "missing_scope"

**Cause:** OAuth token doesn't have required scopes.

**Solution:**
1. Go to your Slack App's "OAuth & Permissions" page
2. Add required User Token Scopes (see [API Reference](./api-reference.md#oauth-scopes-required))
3. Click "Reinstall App" to update permissions
4. Copy the new token to your config file

## Configuration Updates

### Updating OAuth Token

When you need to update a token (rotation, scope changes, etc.):

1. **Generate new token** in Slack App settings
2. **Update config file**:
   ```bash
   vi ~/.config/slack-mcp/workspace-name.json
   # Update "token" field
   ```
3. **Verify permissions**:
   ```bash
   chmod 600 ~/.config/slack-mcp/workspace-name.json
   ```
4. **Test connection**:
   ```python
   slack_workspace(operation='get_team_info')
   ```

### Adding New Workspace

```bash
# Create new config file
cat > ~/.config/slack-mcp/new-workspace.json << 'EOF'
{
  "token": "xoxp-new-token-here",
  "workspace_id": "T12345678",
  "workspace_name": "New Workspace"
}
EOF

# Set permissions
chmod 600 ~/.config/slack-mcp/new-workspace.json

# List all workspaces
slack_workspace(operation='list_workspaces')

# Switch to new workspace
slack_workspace(
  operation='switch_workspace',
  workspace_name='new-workspace'
)
```

### Removing Workspace

```bash
# Remove configuration file
rm ~/.config/slack-mcp/old-workspace.json

# Revoke token in Slack App settings (recommended)
```

## Migration Guide

### From Environment Variables

If you previously stored tokens in environment variables:

1. **Create config directory**:
   ```bash
   mkdir -p ~/.config/slack-mcp
   chmod 700 ~/.config/slack-mcp
   ```

2. **Create config file**:
   ```bash
   cat > ~/.config/slack-mcp/default.json << EOF
   {
     "token": "$SLACK_TOKEN",
     "workspace_name": "Default Workspace",
     "default": true
   }
   EOF
   ```

3. **Set permissions**:
   ```bash
   chmod 600 ~/.config/slack-mcp/default.json
   ```

4. **Remove environment variable** (more secure):
   ```bash
   unset SLACK_TOKEN
   # Also remove from .bashrc, .zshrc, etc.
   ```

### From Single Workspace to Multi-Workspace

1. **Rename existing config** to a workspace-specific name:
   ```bash
   mv ~/.config/slack-mcp/config.json \
      ~/.config/slack-mcp/primary-workspace.json
   ```

2. **Add additional workspaces** following the [Adding New Workspace](#adding-new-workspace) guide

3. **Set one workspace as default**:
   ```json
   {
     "token": "xoxp-...",
     "default": true
   }
   ```

---

**Last Updated**: 2026-02-15
**Schema Version**: 1.0
