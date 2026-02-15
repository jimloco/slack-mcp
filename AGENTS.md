# AI Agent Implementation Guide: Slack MCP Server

> **CRITICAL:** This document is MANDATORY reading for ALL AI agents (primary and sub-agents) working on this project. No exceptions.

## CRITICAL WORKFLOW RULES

**Git Commit Policy:**
- **NEVER commit without explicit user instruction**
- Always verify functionality is working before committing
- Wait for user confirmation after testing
- Exception: Only commit when user explicitly says "commit" or "git commit"

## Project Overview

**Project Name:** Slack MCP Server
**Type:** MCP Server
**Architecture:** Single Repository Python Package with Poetry Dependency Management
**Classification:** Personal Tool (handles confidential OAuth tokens)

## MANDATORY: Documentation Review Requirements

### Before ANY Implementation Work

**ALL AI agents MUST:**

1. **Read Complete Project Documentation**
   - `docs/project-charter.md` - Business objectives and scope
   - `docs/requirements.md` - MVP features and technical requirements
   - `docs/functional-requirements.md` - Solution design and security requirements
   - `docs/implementation.md` - Technical architecture and implementation roadmap
   - Review all feature specifications in `docs/features/` directory

2. **Understand Project Context**
   - **Primary Purpose**: Provide AI assistants with comprehensive access to Slack workspaces through user-level OAuth operations
   - **Security Classification**: Confidential - handles OAuth tokens and user data from Slack workspaces
   - **Single Repository Architecture**: Professional Python 3.12+ package with proper MCP server structure
   - **Python 3.12+ Compliance**: Strict dependency management and virtual environment requirements

3. **Confirm Understanding Before Proceeding**
   - Verify business requirements understanding
   - Acknowledge security classification requirements (OAuth token protection)
   - Confirm single repository coordination approach
   - Validate Python 3.12+ workflow execution plan
   - Understand MCP protocol and STDIO transport requirements

### At Each Major Implementation Step

**MANDATORY CHECKPOINT PROCESS:**

1. **Reference Documentation**: Re-read relevant documentation sections
2. **Validate Approach**: Ensure approach aligns with documented specifications
3. **Security Review**: Confirm security requirements are being met (token protection)
4. **Integration Check**: Verify work integrates with existing MCP architecture
5. **Progress Update**: Document progress against implementation spec

## Security Requirements (CRITICAL)

### Data Classification and Handling

**Confidential Data - OAuth Tokens:**
- User OAuth tokens (xoxp-...) stored in ~/.config/slack-mcp/*.json
- **Requirements**: 600 file permissions (user-only), never logged, never committed to git, validated before every Slack API call

**Confidential Data - Slack Workspace Information:**
- Messages, user profiles, file metadata accessed via Slack API
- **Requirements**: No local caching, no persistent storage, pass-through only, respect Slack permissions

**Internal - Application Configuration:**
- Workspace names, Slack workspace IDs, API endpoints
- **Requirements**: Stored in ~/.config/slack-mcp/ with 600 permissions, no secrets in code

### Security Implementation Requirements

**Authentication & Authorization:**
- **Authentication Method**: User OAuth tokens (xoxp-...) manually generated from Slack App
- **Authorization Model**: User-level permissions enforced by Slack API (no privilege escalation)
- **Token Management**: No token refresh (users manually regenerate), validated on startup and before each operation
- **Permission Handling**: Respect Slack OAuth scopes, fail gracefully on insufficient permissions with clear error messages

**Data Protection Standards:**
- **Tokens in Transit**: Tokens only sent to Slack API via HTTPS (enforced by slack-sdk)
- **Tokens at Rest**: Stored in ~/.config/slack-mcp/ with 600 permissions, encrypted by OS filesystem
- **Data Retention**: No message/user data retention, all operations are real-time pass-through to Slack API
- **Memory Cleanup**: No sensitive data kept in memory after operation completes

### Technology-Specific Security Requirements

**Python 3.12 Security Standards:**
- **Input Sanitization**: All user inputs must be validated and sanitized (channel IDs, user IDs, message text, file paths)
- **Dependency Security**: Use safety and bandit for vulnerability scanning
- **Type Safety**: Comprehensive type hints with mypy validation for security-critical code (auth, token handling)

**Zero Trust Security Model Implementation:**
- **Never Trust, Always Verify**: Validate all inputs (channel IDs, user IDs, workspace names), file paths, and external data
- **Principle of Least Privilege**: Request minimal OAuth scopes, no admin permissions
- **Continuous Verification**: Validate OAuth token before every Slack API operation
- **Assume Breach**: No persistent storage of Slack data, tokens can be revoked by user at any time
- **Identity-Centric Security**: All operations require valid OAuth token context

**MCP-Specific Security Requirements:**
- **STDIO Transport**: Server runs locally via STDIO (no network exposure)
- **Tool Parameter Validation**: Validate all MCP tool parameters against schema before processing
- **Error Sanitization**: Never return OAuth tokens or sensitive data in MCP error responses
- **Rate Limit Handling**: Respect Slack API rate limits to prevent account throttling

**Linting and Code Security:**
- **Bandit Security Rules**: Scan for common Python security vulnerabilities (hardcoded passwords, SQL injection, insecure random)
- **No Secrets in Code**: Use git-secrets or similar to prevent credential commits
- **Python Strict Mode**: Use mypy strict mode for type safety validation
- **Dependency Security**: Regular safety audits and automated vulnerability scanning
- **Git Pre-commit Hooks**: Security validation before all commits

**Required Security Linting Configuration:**
```python
# .banditrc - Python security linting
[bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = []  # No skips without security review

# pyproject.toml - Type checking security
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Data Flow Security:**
- **Input Validation**: Sanitize all user inputs (message text, search queries) and validate IDs (channel, user, file)
- **Output Sanitization**: Never include OAuth tokens in logs, error messages, or MCP responses
- **Memory Management**: Immediate cleanup of sensitive data after Slack API response processed

**Slack API Rate Limiting:**
- **Tier Awareness**: Respect Slack API Tier 3/4 rate limits (varies by method)
- **Exponential Backoff**: Implement exponential backoff on 429 rate limit responses
- **User Communication**: Provide clear error messages when rate limited with retry advice
- **No Aggressive Retries**: Never implement tight retry loops that could trigger account throttling

### Security Validation Checkpoints

**Before Each Implementation Phase:**
- [ ] Security requirements reviewed and understood
- [ ] OAuth token protection strategy confirmed
- [ ] Access control patterns validated (user-level only)
- [ ] Audit logging requirements confirmed (no token logging)
- [ ] Python 3.12 type safety enabled and configured
- [ ] Security linting rules active and passing
- [ ] Zero trust principles applied to design
- [ ] MCP tool parameter schemas validated

**During Implementation:**
- [ ] OAuth tokens never logged or exposed
- [ ] No sensitive data exposed in error messages
- [ ] Authentication/authorization properly integrated with Slack API
- [ ] Compliance requirements met (Slack API ToS)
- [ ] All linting rules passing (bandit, mypy, safety)
- [ ] Input validation implemented at every MCP tool boundary
- [ ] Error handling follows security guidelines (no token leakage)
- [ ] Zero trust verification at every Slack API call
- [ ] Rate limiting handled gracefully

## Coding Style and Standards

### Python Package Architecture Requirements

**Professional MCP Server Structure:**
- Use pyproject.toml (Poetry) for dependency management
- Console script entry point: `start-mcp` command via Poetry
- Automatic virtual environment isolation with Poetry
- Modular design: MCPServer, WorkspaceManager, SlackClient, operation managers
- Comprehensive logging with structured error reporting (no token logging)
- Deterministic builds with poetry.lock

**MCP Server Architecture:**
- **STDIO Transport**: Server runs via mcp.server.stdio.stdio_server()
- **Tool Registration**: Register all 4 tools (conversations, users, files, workspace) at startup
- **Async Operations**: All Slack API calls use async/await with slack-sdk async client
- **Signal Handlers**: Graceful shutdown on SIGINT/SIGTERM
- **Error Handling**: Return MCP-formatted errors with actionable messages

### Code Quality Standards

**Python 3.12 Development Requirements:**
- **Python Execution**: Always use `poetry run python` to execute Python scripts
- **Code Compliance**: All code must be PEP8 compliant with Black code formatting
- **Type Safety**: Use type hints for all function parameters and return values
- **Documentation**: Include docstrings for all modules, classes, and functions
- **Environment Isolation**: Always use a virtual environment for development

**Zero Trust Security Model Implementation:**
- **Input Validation**: Never trust input from any source - validate all MCP tool parameters
- **Least Privilege**: Implement least privilege principle for all Slack API scopes
- **Allowlist Validation**: Use strong input validation with explicit allowlists for IDs
- **Secret Management**: Never store OAuth tokens in code - use ~/.config/slack-mcp/ files
- **Exception Handling**: Implement proper exception handling that doesn't leak OAuth tokens
- **Authorization Layers**: Validate OAuth token before every Slack API operation
- **Output Sanitization**: Sanitize all MCP responses to prevent token leakage
- **Security Logging**: Log all security events without exposing OAuth tokens

**Dependency Management Standards:**
- **Poetry Only**: Use Poetry (pyproject.toml) for all dependency management
- **Core Dependencies**: slack-sdk, mcp, anyio, python-dotenv
- **Version Pinning**: Poetry automatically pins dependencies with exact versions in poetry.lock
- **No Manual pip**: Never use pip directly - always use Poetry commands
- **Security Audits**: Run `poetry run pip-audit` before committing dependency changes
- **Update Strategy**: Review and test dependency updates in isolated environment

**Testing Requirements:**
- **Test Framework**: Use pytest for all automated testing
- **Coverage**: Minimum 80% code coverage for all modules
- **Test Types**: Unit tests, integration tests (with mocked Slack API), MCP tool tests
- **Mocking**: Proper mocking for Slack API calls (use pytest-mock or unittest.mock)
- **Test Organization**: Tests mirror source code structure in `tests/` directory
- **MCP Testing**: Test with MCP Inspector for end-to-end validation

**Code Quality Enforcement:**
- **Linting Tools**: pylint (target 10.00/10), flake8, bandit, mypy
- **Pre-commit Hooks**: Automated code quality checks before every commit
- **Continuous Integration**: Linting and testing in CI pipeline (if applicable)
- **Code Reviews**: Peer review before merging to main branch

### Code Security Patterns

**Example 1: Secure OAuth Token Loading**
```python
import json
from pathlib import Path
from typing import Dict

def load_workspace_config(workspace_name: str) -> Dict[str, str]:
    """
    Load workspace configuration with OAuth token securely.

    Args:
        workspace_name: Name of the workspace config file

    Returns:
        Configuration dictionary with token

    Raises:
        ValueError: If config file has incorrect permissions
        FileNotFoundError: If config file doesn't exist
    """
    config_dir = Path.home() / ".config" / "slack-mcp"
    config_file = config_dir / f"{workspace_name}.json"

    # Validate file exists
    if not config_file.exists():
        raise FileNotFoundError(f"Config not found: {config_file}")

    # Check file permissions (Unix-like systems)
    if config_file.stat().st_mode & 0o777 != 0o600:
        raise ValueError(f"{config_file} must have 600 permissions")

    # Load configuration
    with config_file.open("r") as f:
        config = json.load(f)

    # Validate required fields (but never log token)
    if "token" not in config:
        raise ValueError("Config missing required 'token' field")

    logger.info(f"Loaded config for workspace: {workspace_name}")
    # NEVER log the actual token value

    return config
```

**Example 2: Secure Slack API Call with Validation**
```python
from typing import Dict, Any
from slack_sdk.web.async_client import AsyncWebClient

async def post_message_secure(
    client: AsyncWebClient,
    channel_id: str,
    text: str
) -> Dict[str, Any]:
    """
    Post message to Slack with input validation.

    Args:
        client: Authenticated Slack API client
        channel_id: Validated channel ID
        text: Message text to post

    Returns:
        Slack API response

    Raises:
        ValueError: If inputs are invalid
    """
    # Validate channel ID format
    if not channel_id or not channel_id[0] in ['C', 'G', 'D']:
        raise ValueError(f"Invalid channel ID format: {channel_id}")

    # Validate message text
    if not text or len(text) > 40000:
        raise ValueError("Message text must be 1-40000 characters")

    # Sanitize text (prevent injection if using mrkdwn)
    # Note: Slack handles most sanitization, but validate length/format
    sanitized_text = text.strip()

    try:
        response = await client.chat_postMessage(
            channel=channel_id,
            text=sanitized_text
        )
        logger.info(f"Posted message to channel {channel_id}")
        return response.data
    except Exception as error:
        # Log error without exposing token
        logger.error(f"Failed to post message: {error}")
        raise
```

**Example 3: MCP Tool Parameter Validation**
```python
from typing import Dict, Any, List
from mcp import types

def validate_tool_parameters(
    tool_name: str,
    operation: str,
    arguments: Dict[str, Any]
) -> None:
    """
    Validate MCP tool parameters against schema.

    Args:
        tool_name: Name of the MCP tool
        operation: Operation being called
        arguments: Tool arguments

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate operation is allowed
    allowed_ops = {
        "slack_conversations": ["search", "post_message", "list_channels"],
        "slack_users": ["list_users", "get_user"],
        "slack_files": ["upload", "list_files"],
        "slack_workspace": ["get_info", "list_emoji"]
    }

    if operation not in allowed_ops.get(tool_name, []):
        raise ValueError(f"Invalid operation {operation} for tool {tool_name}")

    # Validate required parameters based on operation
    if operation == "post_message":
        if "channel_id" not in arguments or "text" not in arguments:
            raise ValueError("post_message requires channel_id and text")

    # Additional validation logic per operation
```

### Performance Standards

**Performance Requirements:**
- <1s for single-entity operations (post message, get user)
- <2s for search and list operations (10-50 results)
- <5s for large list operations (500+ items with pagination)
- <10s for file uploads (under 10MB)

**Performance Optimization:**
- Use async/await for all Slack API calls (non-blocking I/O)
- Implement connection pooling via slack-sdk WebClient
- Use pagination efficiently for large datasets
- Minimize API calls (batch operations where possible)
- Cache workspace configs in memory (but never cache OAuth tokens on disk)

## Development Workflow

### Environment Setup
1. Install Python 3.12+
2. Install Poetry: `pip install poetry`
3. Clone repository
4. Run `poetry install` to create virtual environment and install dependencies
5. Create ~/.config/slack-mcp/ directory with 700 permissions
6. Create workspace config files (*.json) with 600 permissions
7. Run `poetry run start-mcp` to test (or `poetry run python -m slack_mcp`)

### Making Changes
1. Create feature branch from main
2. Make changes following coding standards
3. Write tests for new functionality
4. Run linting: `poetry run pylint slack_mcp`
5. Run security scan: `poetry run bandit -r slack_mcp`
6. Run type checking: `poetry run mypy slack_mcp --strict`
7. Run tests: `poetry run pytest --cov=slack_mcp`
8. Ensure all checks pass before committing

### Quality Gates
- ✅ Pylint score: **10.00/10** (exact, no tolerance)
- ✅ Test coverage: **≥ 80%**
- ✅ Bandit security scan: **No high-severity issues**
- ✅ Mypy type checking: **No errors in strict mode**
- ✅ All tests: **Passing**

### MCP-Specific Testing
- Test with MCP Inspector: `mcp-inspector poetry -C /path/to/slack-mcp run start-mcp`
- Validate all 4 tools register correctly
- Test each operation with valid and invalid inputs
- Verify error handling returns proper MCP error responses
- Test multi-workspace switching
- Verify graceful shutdown on Ctrl+C (SIGINT)

## MANDATORY Actions for All AI Agents

**✅ MUST DO:**
- ✅ READ all project documentation before starting work
- ✅ FOLLOW security requirements without exception (OAuth token protection)
- ✅ USE Poetry for all dependency management (`poetry add`, `poetry install`)
- ✅ EXECUTE Python with Poetry: `poetry run python <script>`
- ✅ VALIDATE all MCP tool parameters against schema
- ✅ PROTECT OAuth tokens: never log, never expose in errors, 600 file permissions
- ✅ DOCUMENT all functions with docstrings and type hints
- ✅ RUN security linting (bandit, mypy) after every change
- ✅ ACHIEVE 10.00/10 pylint score before committing
- ✅ AUDIT dependencies with `poetry run pip-audit` before adding new ones
- ✅ TEST code with `poetry run pytest` and verify ≥80% coverage
- ✅ TEST with MCP Inspector for end-to-end validation
- ✅ APPLY zero trust principles to all security decisions
- ✅ SANITIZE all inputs at every MCP tool boundary
- ✅ USE async/await for all Slack API calls
- ✅ HANDLE Slack API rate limits gracefully with exponential backoff
- ✅ INCLUDE type hints for all function parameters and returns
- ✅ WRITE comprehensive docstrings for all modules/classes/functions
- ✅ USE pytest for all test automation with proper Slack API mocking
- ✅ IMPLEMENT proper error handling without leaking OAuth tokens
- ✅ RUN all static analysis tools and fix all issues
- ✅ VALIDATE work against implementation spec at each checkpoint
- ✅ WAIT for explicit user instruction before committing to git

**❌ MUST NOT DO:**
- ❌ NEVER skip documentation review phase
- ❌ NEVER compromise OAuth token security (no logging, no exposure in errors)
- ❌ NEVER work outside Poetry virtual environment
- ❌ NEVER use pip directly (always use Poetry)
- ❌ NEVER bypass dependency management with manual installs
- ❌ NEVER commit code with linting errors or warnings
- ❌ NEVER store OAuth tokens in code or commit them to git
- ❌ NEVER log OAuth tokens at any log level (info, debug, error)
- ❌ NEVER cache Slack message/user data locally (pass-through only)
- ❌ NEVER use unsafe types (Any) for security-critical code (auth, tokens)
- ❌ NEVER bypass input validation at MCP tool boundaries
- ❌ NEVER expose detailed Slack API errors to MCP responses (sanitize first)
- ❌ NEVER trust MCP tool parameters without validation
- ❌ NEVER commit workspace config files (*.json) to git
- ❌ NEVER use denylists for validation (use allowlists for IDs)
- ❌ NEVER skip Slack API rate limit handling
- ❌ NEVER disable security warnings without documentation
- ❌ NEVER modify .pylintrc to lower quality standards
- ❌ NEVER commit without running full test suite
- ❌ NEVER push code that doesn't meet quality gates
- ❌ NEVER implement aggressive retry loops (respect rate limits)

## Slack-Specific Best Practices

**Slack API Guidelines:**
- Always use slack-sdk library (official Slack Python SDK)
- Use AsyncWebClient for all async operations
- Handle rate limit responses (429) with exponential backoff
- Respect Slack API Terms of Service
- Include proper User-Agent header (handled by slack-sdk)
- Parse error responses properly (Slack returns structured errors)

**OAuth Scope Management:**
- Request minimal scopes needed for operations
- Document required scopes in README for user setup
- Validate scopes on startup and provide clear error if missing
- Never request admin or workspace-level scopes (user-level only)

**Multi-Workspace Support:**
- Support multiple workspace configs in ~/.config/slack-mcp/
- Allow workspace selection per operation or global default
- Isolate credentials per workspace (no cross-workspace token use)
- Provide friendly workspace names for user reference

## Success Indicators

**Project Success:**
1. **Functionality**: All user stories and acceptance criteria met (4 MCP tools operational)
2. **Quality**: 10.00/10 pylint score, ≥80% test coverage
3. **Security**: Zero high-severity vulnerabilities, OAuth tokens protected, no data leakage
4. **Performance**: All performance targets achieved (<2s typical operations)
5. **Documentation**: Complete documentation for all features and setup
6. **Maintainability**: Clean, well-structured, type-safe, async code

**Implementation Success:**
1. All documentation read and understood
2. OAuth token security fully implemented (600 permissions, no logging, no exposure)
3. Code quality standards met (10.00/10 pylint)
4. Comprehensive test coverage (≥80%)
5. Zero security vulnerabilities
6. All MCP tools tested with MCP Inspector
7. Multi-workspace support working
8. Slack API rate limiting handled gracefully

---

**This document must be referenced at every major implementation step. Security (especially OAuth token protection) and quality are non-negotiable.**
