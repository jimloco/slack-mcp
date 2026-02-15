# Slack App Manifest for MCP Server

**Quick Setup**: Use this manifest to create a Slack App with all required permissions pre-configured.

## What is an App Manifest?

A Slack App Manifest is a YAML configuration file that defines your app's settings, features, and permissions. Instead of manually clicking through dozens of settings, you can paste this manifest when creating your app to instantly configure everything.

## How to Use This Manifest

### Step 1: Go to Slack App Creation

Visit: **https://api.slack.com/apps**

### Step 2: Create App from Manifest

1. Click **"Create New App"**
2. Select **"From an app manifest"**
3. Choose your workspace
4. Click **"Next"**

### Step 3: Paste the Manifest

Copy the YAML below and paste it into the text box:

```yaml
display_information:
  name: Slack MCP Server
  description: AI assistant integration for Slack workspace operations
  background_color: "#4A154B"
oauth_config:
  scopes:
    user:
      - channels:history
      - channels:read
      - channels:write
      - chat:write
      - emoji:read
      - files:read
      - files:write
      - groups:history
      - groups:read
      - groups:write
      - im:history
      - im:read
      - im:write
      - mpim:history
      - mpim:read
      - search:read
      - team:read
      - users:read
      - users:read.email
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

### Step 4: Review and Create

1. Click **"Next"** to review the configuration
2. Click **"Create"** to create the app
3. You'll see a summary of permissions - these are correct!

### Step 5: Install and Get Token

1. Click **"Install to Workspace"**
2. Review the permissions and click **"Allow"**
3. Copy the **"User OAuth Token"** (starts with `xoxp-`)
4. Save this token in your workspace configuration file

## What This Manifest Configures

### User Token Scopes (18 scopes)

**Conversations (Messages & Channels):**
- `channels:history` - View messages in public channels
- `channels:read` - View basic channel information
- `channels:write` - Create and manage public channels
- `groups:history` - View messages in private channels
- `groups:read` - View basic private channel information
- `groups:write` - Create and manage private channels
- `im:history` - View direct message history
- `im:read` - View basic DM information
- `im:write` - Send direct messages
- `mpim:history` - View group DM history
- `mpim:read` - View group DM information
- `chat:write` - Post messages as you

**Search:**
- `search:read` - Search messages and files

**Users:**
- `users:read` - View workspace members
- `users:read.email` - View email addresses

**Files:**
- `files:read` - View and download files
- `files:write` - Upload and manage files

**Workspace:**
- `team:read` - View workspace information
- `emoji:read` - View custom emoji

### What's NOT Included

This manifest intentionally excludes:

- ❌ **Bot User** - No bot functionality (user tokens only)
- ❌ **Bot Token Scopes** - MCP Server uses user tokens only
- ❌ **Event Subscriptions** - No webhook/event listeners needed
- ❌ **Slash Commands** - MCP operates via Claude Code, not Slack UI
- ❌ **Interactive Components** - No buttons or modals
- ❌ **Admin Scopes** - No workspace administration permissions

## Alternative: Manual Scope Configuration

If you prefer to create the app manually or need to add scopes to an existing app:

1. Go to your app's **"OAuth & Permissions"** page
2. Scroll to **"User Token Scopes"** (NOT Bot Token Scopes)
3. Click **"Add an OAuth Scope"** for each scope listed above
4. After adding all scopes, click **"Reinstall to Workspace"**
5. Copy the new User OAuth Token

## Verifying Your Configuration

After creating your app, verify it has the correct scopes:

### Check OAuth & Permissions Page

Your **"User Token Scopes"** section should show exactly 18 scopes:

```
✓ channels:history    ✓ channels:read     ✓ channels:write
✓ chat:write          ✓ emoji:read        ✓ files:read
✓ files:write         ✓ groups:history    ✓ groups:read
✓ groups:write        ✓ im:history        ✓ im:read
✓ im:write            ✓ mpim:history      ✓ mpim:read
✓ search:read         ✓ team:read         ✓ users:read
✓ users:read.email
```

### Test Connection

After installing the app and configuring the MCP server:

```python
# Test basic connection
slack_workspace(operation='get_team_info')

# Test search scope
slack_conversations(operation='search', query='test')

# Test user scope
slack_users(operation='list_users', limit=5)

# Test file scope
slack_files(operation='list_files', limit=5)
```

If any operation fails with `missing_scope` error, return to OAuth & Permissions and add the missing scope.

## Updating Scopes Later

If you need to add scopes after initial setup:

1. Go to **"OAuth & Permissions"** in your app settings
2. Scroll to **"User Token Scopes"**
3. Click **"Add an OAuth Scope"** and select the scope
4. Click **"Reinstall to Workspace"** at the top of the page
5. **Important**: Copy the NEW User OAuth Token
6. Update your `~/.config/slack-mcp/{workspace}.json` with the new token

## Security Considerations

### Token Type: User OAuth Token

This manifest configures **User Token Scopes** which means:

- ✅ The app acts as **you** (the installing user)
- ✅ Can only access what **you** can access
- ✅ Respects your permissions and channel memberships
- ✅ More secure than bot tokens for personal use

### What the App Can Do

With these scopes, the MCP Server can:

- ✅ Read messages you can read
- ✅ Post messages as you
- ✅ Create channels (if you have permission)
- ✅ Upload files as you
- ✅ Search messages you can search
- ✅ View users and workspace info

### What the App CANNOT Do

- ❌ Access channels you're not a member of (unless public)
- ❌ Delete other users' messages
- ❌ Change workspace settings
- ❌ Manage users or permissions
- ❌ Access admin-only information
- ❌ Bypass any Slack security controls

## Multi-Workspace Setup

If you manage multiple Slack workspaces:

### Option 1: One App, Multiple Installs (Recommended)

1. Create ONE Slack App using this manifest
2. Install it to each workspace separately
3. Each installation gives you a different User OAuth Token
4. Save each token in a separate config file:
   ```
   ~/.config/slack-mcp/workspace1.json
   ~/.config/slack-mcp/workspace2.json
   ~/.config/slack-mcp/workspace3.json
   ```

### Option 2: Separate Apps per Workspace

1. Create a separate Slack App for each workspace
2. Use this same manifest for each app
3. Install each app to its respective workspace
4. Save each token in its own config file

Both approaches work - Option 1 is simpler to maintain.

## Troubleshooting

### Error: "App manifest is invalid"

**Cause**: YAML formatting issue

**Solution**:
- Ensure proper indentation (2 spaces, not tabs)
- Don't add or remove any scopes (use the exact YAML above)
- Copy the entire YAML block including the first line

### Error: "missing_scope" when using MCP server

**Cause**: A required scope wasn't added

**Solution**:
1. Check which scope is missing (error will say which one)
2. Go to OAuth & Permissions → User Token Scopes
3. Add the missing scope
4. Reinstall to Workspace
5. Copy the new token to your config file

### Can't Find "User Token Scopes"

**Cause**: Looking at Bot Token Scopes instead

**Solution**:
- Scroll down on the OAuth & Permissions page
- You'll see **two** sections: "Bot Token Scopes" and "User Token Scopes"
- We only use **User Token Scopes** (the second section)

### Token Starts with "xoxb-" Instead of "xoxp-"

**Cause**: Copied the Bot User OAuth Token instead of User OAuth Token

**Solution**:
1. On the OAuth & Permissions page, scroll up
2. Look for **"User OAuth Token"** (NOT "Bot User OAuth Token")
3. Copy the token that starts with `xoxp-`

## Next Steps

After creating your Slack App:

1. ✅ Install the app to your workspace
2. ✅ Copy the User OAuth Token (xoxp-...)
3. ✅ Create workspace config: `~/.config/slack-mcp/{workspace}.json`
4. ✅ Set proper permissions: `chmod 600 ~/.config/slack-mcp/*.json`
5. ✅ Configure Claude Code to use the MCP server
6. ✅ Test the connection with a simple operation

See [README.md](../README.md) for detailed configuration and usage instructions.

---

**Last Updated**: 2026-02-15
**Manifest Version**: 1.0
**Compatible with**: Slack MCP Server v0.1.0+
