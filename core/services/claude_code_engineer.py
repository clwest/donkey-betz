"""
Claude Code Engineer Service
==============================

Gives Rigby (PA) the ability to spawn autonomous Claude Code engineering
sessions that can read files, write code, create git branches, and open PRs.

This is the bridge between Rigby's operational awareness and Claude Code's
engineering capabilities. When Rigby identifies a bug, a needed feature,
or a code change, he can dispatch this service to do the actual work.

Architecture:
- Rigby calls claude_code_tool via PA function calling
- Tool handler dispatches a Celery task on the code_jobs queue
- Task calls Anthropic Claude API with codebase tools (file read, write, git)
- Results posted back to the conversation via WebSocket
- If code changes are made, a PR is created automatically

Tools available to the engineer:
- read_file: Read any file in the repository
- write_file: Write/create files
- search_code: Search for patterns across the codebase
- git_diff: See current changes
- git_branch: Create a branch
- git_commit: Commit changes
- create_pr: Open a pull request on GitHub
"""
import json
import logging
import os
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = '/app'  # Railway container path — may be read-only
WRITABLE_ROOT = '/tmp/engineer-workspace'  # Writable clone for git operations

SYSTEM_PROMPT = """You are Claude Code Engineer, an autonomous coding agent deployed inside the Donkey Betz platform.

You have been invoked by Rigby (the PA) to perform an engineering task. You have REAL tools to read files, write code, search the codebase, and create git branches/commits/PRs.

RULES:
- Read before writing. Understand existing code before modifying it.
- Make minimal, focused changes. Don't refactor beyond what's asked.
- Always create a branch, never commit to main directly.
- Write clear commit messages explaining the "why."
- If the task is unclear, say so instead of guessing.
- Report what you did concisely — Rigby and Chris will see your response.

CODEBASE:
- Django 5.0 + PostgreSQL + Celery + Redis + React frontend
- core/ has agents, services, tasks, views, models
- frontend/src/ has React components, stores, hooks
- 82 agents, 77 spiders, 134 services

After completing your task, summarize what you changed and provide the PR link if applicable.
"""

# Tool definitions for the Claude API
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file from the repository. Returns the file content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to repo root (e.g. 'core/tasks.py')"},
                "start_line": {"type": "integer", "description": "Start reading from this line (1-indexed)"},
                "end_line": {"type": "integer", "description": "Stop reading at this line"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_code",
        "description": "Search for a pattern across the codebase using grep.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern to search for"},
                "file_glob": {"type": "string", "description": "File pattern to search in (e.g. '*.py', 'core/**/*.py')"},
                "max_results": {"type": "integer", "description": "Maximum results to return", "default": 20},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to repo root"},
                "content": {"type": "string", "description": "Full file content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "git_command",
        "description": "Run a git command. Use for: branch, add, commit, diff, status, log.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Git subcommand and args (e.g. 'checkout -b fix/my-fix', 'add core/tasks.py', 'commit -m \"fix: thing\"')"},
            },
            "required": ["command"],
        },
    },
    {
        "name": "create_pr",
        "description": "Create a GitHub pull request from the current branch.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "PR title"},
                "body": {"type": "string", "description": "PR description"},
            },
            "required": ["title", "body"],
        },
    },
    {
        "name": "create_github_repo",
        "description": "Create a new GitHub repository. Use when starting a new project/app.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Repository name (e.g. 'dogwalkr-app')"},
                "description": {"type": "string", "description": "Short description of the repo"},
                "private": {"type": "boolean", "description": "Whether the repo is private (default: true)"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "create_workspace",
        "description": "Create a workspace in the Donkey Betz platform linked to a GitHub repo. Organizes deliverables, agent work, and project files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Workspace name (e.g. 'DogWalkr')"},
                "description": {"type": "string", "description": "What this project is for"},
                "git_remote_url": {"type": "string", "description": "GitHub repo URL to link (optional)"},
            },
            "required": ["name"],
        },
    },
]


def _ensure_git_repo():
    """
    Clone the repo into a writable temp directory.
    Railway's /app/ is read-only for the appuser, so we shallow-clone
    into /tmp/engineer-workspace/ which is always writable.
    Updates REPO_ROOT globally so all tools use the writable copy.
    """
    global REPO_ROOT

    # If writable workspace already exists, use it
    if os.path.exists(os.path.join(WRITABLE_ROOT, '.git')):
        REPO_ROOT = WRITABLE_ROOT
        logger.info("[ClaudeEngineer] Using existing writable workspace")
        return

    github_token = os.environ.get('GITHUB_TOKEN', '')
    repo_slug = os.environ.get('GITHUB_REPO', 'clwest/donkey-betz-platform')

    logger.info(f"[ClaudeEngineer] Cloning repo into {WRITABLE_ROOT}...")

    try:
        # Write credential helper BEFORE clone so git can authenticate
        clone_url = f'https://github.com/{repo_slug}.git'
        if github_token:
            helper_path = '/tmp/git-credential-helper.sh'
            with open(helper_path, 'w') as f:
                f.write(f'#!/bin/sh\necho "username=x-access-token"\necho "password={github_token}"\n')
            os.chmod(helper_path, 0o755)
            os.environ['GIT_ASKPASS'] = helper_path

        # Shallow clone into writable directory
        result = subprocess.run(
            f'git clone --depth=1 -c credential.helper="{helper_path if github_token else ""}" {clone_url} {WRITABLE_ROOT}',
            shell=True, capture_output=True, text=True, timeout=120
        )

        if result.returncode == 0:
            # Configure git user
            subprocess.run('git config user.email "claude-code@donkeybetz.com"',
                         shell=True, cwd=WRITABLE_ROOT, capture_output=True, timeout=10)
            subprocess.run('git config user.name "Claude Code Engineer"',
                         shell=True, cwd=WRITABLE_ROOT, capture_output=True, timeout=10)

            # Write credential helper for push operations
            helper_path = '/tmp/git-credential-helper.sh'
            if github_token:
                with open(helper_path, 'w') as f:
                    f.write(f'#!/bin/sh\necho "username=x-access-token"\necho "password={github_token}"\n')
                os.chmod(helper_path, 0o755)
                subprocess.run(f'git config credential.helper "{helper_path}"',
                             shell=True, cwd=WRITABLE_ROOT, capture_output=True, timeout=10)

            REPO_ROOT = WRITABLE_ROOT
            logger.info(f"[ClaudeEngineer] Repo cloned successfully to {WRITABLE_ROOT}")
        else:
            logger.warning(f"[ClaudeEngineer] Clone failed: {result.stderr[:300]}")
            # Fall back to /app/ read-only access
            logger.info("[ClaudeEngineer] Falling back to /app/ (read-only)")

    except Exception as e:
        logger.warning(f"[ClaudeEngineer] Git setup failed: {e}")
        logger.info("[ClaudeEngineer] Falling back to /app/ (read-only)")


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a string."""
    try:
        if tool_name == "read_file":
            path = os.path.join(REPO_ROOT, tool_input["path"])
            if not os.path.exists(path):
                return f"Error: File not found: {tool_input['path']}"
            with open(path) as f:
                lines = f.readlines()
            start = tool_input.get("start_line", 1) - 1
            end = tool_input.get("end_line", len(lines))
            selected = lines[start:end]
            return ''.join(selected)[:50000]  # Cap at 50KB

        elif tool_name == "search_code":
            pattern = tool_input["pattern"]
            glob = tool_input.get("file_glob", "*.py")
            max_results = tool_input.get("max_results", 20)
            cmd = ["grep", "-rn", "--include", glob, pattern, REPO_ROOT]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            lines = result.stdout.strip().split('\n')[:max_results]
            # Remove repo root prefix for cleaner output
            cleaned = [l.replace(REPO_ROOT + '/', '') for l in lines]
            return '\n'.join(cleaned) or "No matches found"

        elif tool_name == "write_file":
            path = os.path.join(REPO_ROOT, tool_input["path"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(tool_input["content"])
            return f"Written {len(tool_input['content'])} bytes to {tool_input['path']}"

        elif tool_name == "git_command":
            cmd = f"git {tool_input['command']}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=REPO_ROOT, timeout=60
            )
            output = result.stdout + result.stderr
            return output[:10000] or "(no output)"

        elif tool_name == "create_pr":
            # Try gh CLI first, fall back to GitHub API
            github_token = os.environ.get('GITHUB_TOKEN', '')
            title = tool_input.get("title", "")
            body = tool_input.get("body", "")

            # Get current branch
            branch_result = subprocess.run(
                "git rev-parse --abbrev-ref HEAD",
                shell=True, capture_output=True, text=True, cwd=REPO_ROOT, timeout=10
            )
            branch = branch_result.stdout.strip() or "main"

            if github_token:
                # Use GitHub API directly (more reliable than gh CLI in containers)
                import urllib.request
                api_url = "https://api.github.com/repos/clwest/donkey-betz-platform/pulls"
                pr_data = json.dumps({
                    "title": title,
                    "body": body + "\n\n🤖 Created by Claude Code Engineer",
                    "head": branch,
                    "base": "main",
                }).encode()
                req = urllib.request.Request(api_url, data=pr_data, method="POST")
                req.add_header("Authorization", f"token {github_token}")
                req.add_header("Content-Type", "application/json")
                req.add_header("Accept", "application/vnd.github.v3+json")
                try:
                    resp = urllib.request.urlopen(req, timeout=30)
                    pr_resp = json.loads(resp.read().decode())
                    return f"PR created: {pr_resp.get('html_url', 'unknown')}"
                except Exception as api_err:
                    return f"GitHub API PR creation failed: {api_err}"
            else:
                return "Error: GITHUB_TOKEN not set — cannot create PR"

        elif tool_name == "create_github_repo":
            github_token = os.environ.get('GITHUB_TOKEN', '')
            if not github_token:
                return "Error: GITHUB_TOKEN not set"
            repo_name = tool_input.get("name", "")
            description = tool_input.get("description", "")
            private = tool_input.get("private", True)

            import urllib.request
            api_url = "https://api.github.com/user/repos"
            repo_data = json.dumps({
                "name": repo_name,
                "description": description,
                "private": private,
                "auto_init": True,  # Creates with README
            }).encode()
            req = urllib.request.Request(api_url, data=repo_data, method="POST")
            req.add_header("Authorization", f"token {github_token}")
            req.add_header("Content-Type", "application/json")
            req.add_header("Accept", "application/vnd.github.v3+json")
            try:
                resp = urllib.request.urlopen(req, timeout=30)
                repo_resp = json.loads(resp.read().decode())
                repo_url = repo_resp.get('html_url', '')
                clone_url = repo_resp.get('clone_url', '')
                return f"Repository created: {repo_url}\nClone URL: {clone_url}\nPrivate: {private}"
            except Exception as api_err:
                return f"GitHub repo creation failed: {api_err}"

        elif tool_name == "create_workspace":
            ws_name = tool_input.get("name", "")
            ws_description = tool_input.get("description", "")
            git_remote = tool_input.get("git_remote_url", "")

            try:
                import django
                django.setup()
                from core.models_skin_layer import ProjectWorkspace
                from django.contrib.auth import get_user_model
                User = get_user_model()
                # Use the first superuser as workspace owner
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    return "Error: No superuser found to own the workspace"

                ws = ProjectWorkspace.objects.create(
                    user=user,
                    name=ws_name,
                    description=ws_description,
                    root_path=f'/app/workspaces/{ws_name.lower().replace(" ", "-")}',
                    git_remote_url=git_remote,
                    is_active=False,  # Don't make active by default
                    workspace_type='local',
                )
                return f"Workspace created: {ws.name} (id={ws.id})\nLinked repo: {git_remote or 'none'}\nActive: False (set active manually when ready)"
            except Exception as ws_err:
                return f"Workspace creation failed: {ws_err}"

        else:
            return f"Unknown tool: {tool_name}"

    except subprocess.TimeoutExpired:
        return f"Error: Tool {tool_name} timed out"
    except Exception as e:
        return f"Error in {tool_name}: {str(e)}"


def execute_engineering_task(
    task_description: str,
    conversation_id: str = None,
    requested_by: str = 'rigby',
    max_iterations: int = 500,
) -> Dict[str, Any]:
    """
    Execute an engineering task using Claude with codebase tools.

    Args:
        task_description: What to do (from Rigby or Chris)
        conversation_id: PA conversation to post results to
        requested_by: Who requested this (for attribution)
        max_iterations: Max tool-use iterations

    Returns:
        Dict with status, summary, files_changed, pr_url
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {'status': 'error', 'error': 'ANTHROPIC_API_KEY not set'}

    # Initialize git repo if not present (Railway containers don't include .git)
    _ensure_git_repo()

    try:
        # Session 1084 round 49: shared factory for timeout/retry config.
        import anthropic  # kept for anthropic.RateLimitError reference below
        from core.services.anthropic_client_factory import get_anthropic_client
        import time as _time
        client = get_anthropic_client(api_key=api_key)

        messages = [{"role": "user", "content": task_description}]
        files_changed = []
        pr_url = None

        for iteration in range(max_iterations):
            # Rate limit retry loop
            for retry in range(3):
                try:
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4096,
                        system=SYSTEM_PROMPT,
                        tools=TOOLS,
                        messages=messages,
                    )
                    break  # Success
                except anthropic.RateLimitError as rle:
                    wait = (retry + 1) * 30  # 30s, 60s, 90s
                    logger.warning(f"[ClaudeEngineer] Rate limited, waiting {wait}s (retry {retry+1}/3)")
                    _time.sleep(wait)
                    if retry == 2:
                        raise rle  # Give up after 3 retries

            # Check if we're done (no more tool calls)
            if response.stop_reason == "end_turn":
                # Extract final text response
                final_text = ''
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_text += block.text
                break

            # Process tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info(f"[ClaudeEngineer] Tool: {block.name} (iteration {iteration+1})")
                    result = _execute_tool(block.name, block.input)

                    # Track file changes
                    if block.name == "write_file":
                        files_changed.append(block.input.get("path", "?"))
                    elif block.name == "create_pr" and "github.com" in result:
                        pr_url = result.strip()

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result[:10000],  # Cap at 10KB per result to reduce token usage
                    })

            # Add assistant response + tool results to conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            # Trim old messages if context getting too large (keep first + last 10 turns)
            if len(messages) > 24:
                messages = [messages[0]] + messages[-20:]

        else:
            final_text = f"Reached max iterations ({max_iterations}). Task may be incomplete."

        # Post result to conversation if specified
        if conversation_id:
            _post_to_conversation(conversation_id, final_text, files_changed, pr_url)

        return {
            'status': 'success',
            'summary': final_text[:2000],
            'files_changed': files_changed,
            'pr_url': pr_url,
            'iterations': iteration + 1 if 'iteration' in dir() else 0,
        }

    except Exception as e:
        logger.error(f"[ClaudeEngineer] Task failed: {e}")
        error_msg = f"Engineering task failed: {str(e)}"

        if conversation_id:
            _post_to_conversation(conversation_id, error_msg, [], None)

        return {'status': 'error', 'error': str(e)}


def _post_to_conversation(conversation_id: str, summary: str, files_changed: list, pr_url: str = None):
    """Post engineering results back to the PA conversation."""
    from core.models import ChatConversation
    from django.contrib.auth import get_user_model

    # Build result message
    parts = [summary]
    if files_changed:
        parts.append(f"\n**Files changed:** {', '.join(files_changed)}")
    if pr_url:
        parts.append(f"\n**PR:** {pr_url}")

    content = '\n'.join(parts)

    # Resolve user
    User = get_user_model()
    user = ChatConversation.objects.filter(
        conversation_id=conversation_id, user__isnull=False
    ).values_list('user_id', flat=True).first()

    chat_row = ChatConversation.objects.create(
        user_id=user,
        conversation_id=conversation_id,
        user_message=content,
        assistant_response='',
        source='claude-code',
        platform='agent',
        metadata={'autonomous': True, 'agent': 'claude_code_engineer', 'files_changed': files_changed, 'pr_url': pr_url},
    )

    # Broadcast via WebSocket.
    # Session 1103c: loud on failure so Claude Code→ChatUI live-message
    # broadcast drops are visible. Previously if the channel layer
    # errored, the message was still saved to DB but the ChatUI never
    # got the WebSocket push, leaving users wondering why a message
    # "appeared later" instead of live.
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"pa_conversation_{conversation_id}",
                {
                    "type": "message.created",
                    "message": {
                        "id": str(chat_row.id),
                        "role": "user",
                        "content": content,
                        "source": "claude-code",
                        "timestamp": chat_row.created_at.isoformat(),
                    }
                }
            )
    except Exception as e:
        logger.warning(
            "claude_code_engineer: WebSocket broadcast failed for "
            "conversation %s (%s: %s) — message saved but ChatUI won't "
            "see it until next poll",
            conversation_id, type(e).__name__, e,
        )
