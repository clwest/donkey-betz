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


# ── Session 1262: Claude Code task receipt reliability ──────────────────
#
# Prior to S1262, claude_code_engineer_task ran without writing an
# ``AgentExecution`` row, so the canonical S1174 follow-up wake stack had
# no anchor to bind to AND ``_post_to_conversation`` silently no-op'd when
# ``conversation_id`` arrived as None (four call sites: success/error paths
# in both Anthropic + OpenAI). Five recent dispatches (task_ids
# 9d601010 / 068ee853 / bf7ca961 / 18734082 / f8a4d3c2) all returned
# CeleryTaskEvent.status=SUCCESS but produced ZERO AgentExecution rows
# and ZERO ChatConversation post-backs — the work happened, the result
# vanished. The fix below mirrors the canonical pattern from
# ``core/tasks_agents.py:2270-2325``: create an AgentExecution row at
# task entry, update it on terminal, wire ``create_implicit_followup_
# subscription`` so the existing S1174 stack delivers the completion.
#
# Per Rigby S1262 SIGN:
#   * Use a canonical agent-name resolver with alias fallback
#     (``"claude-code"`` preferred, ``"ClaudeCode"`` accepted) so this
#     PR does not couple to a later agent-row consolidation.
#   * ``conversation_id=None`` is NOT a raise — the LLM run succeeded;
#     ERROR-log it and persist the result on the AgentExecution row.
#   * ChatConversation write failure IS a raise (visible via
#     CeleryTaskEvent.status=FAILURE) but ``claude_code_engineer_task``
#     is configured with ``max_retries=0`` to avoid re-burning LLM
#     budget.

_CLAUDE_CODE_AGENT_NAMES = ("claude-code", "ClaudeCode")


def _resolve_claude_code_agent():
    """Resolve the canonical ``Agent`` row for claude_code_engineer_task.

    Tries names in ``_CLAUDE_CODE_AGENT_NAMES`` order. Returns the first
    active match, or any match (including inactive) as a last resort.
    Returns None if no row exists — the caller is expected to skip
    AgentExecution creation gracefully in that edge case (matches
    BaseAgent.run's behavior at base_agent.py:1215-1219).

    Emits a one-line WARN when more than one name resolves, so an
    operator notices the duplication without this fix becoming
    dependent on a consolidation PR.
    """
    from core.models import Agent

    matches = list(
        Agent.objects.filter(name__in=_CLAUDE_CODE_AGENT_NAMES)
    )
    if not matches:
        return None
    if len(matches) > 1:
        names = sorted({m.name for m in matches})
        logger.warning(
            "[CLAUDE_CODE_AGENT_DUP] multiple Agent rows match canonical "
            "claude_code names=%s — preferring 'claude-code'. Consolidate "
            "in a future hygiene PR.",
            names,
        )
    for preferred in _CLAUDE_CODE_AGENT_NAMES:
        for m in matches:
            if m.name == preferred and m.is_active:
                return m
    for preferred in _CLAUDE_CODE_AGENT_NAMES:
        for m in matches:
            if m.name == preferred:
                return m
    return matches[0]


def _create_engineer_execution_record(
    celery_task_id: str,
    task_description: str,
    conversation_id: Optional[str],
    requested_by: str,
    request_mode: str,
):
    """Create an ``AgentExecution`` row anchoring this dispatch.

    Mirror of ``core/tasks_agents.py:2270-2325`` canonical pattern.
    Returns the created row or None if no ``Agent`` row was resolvable
    (defensive — never raises; failure here must not stop the work).

    The row's ``input_data['celery_task_id']`` is the canonical query
    surface used by ``td_handlers_agents.py:5202`` for the
    ``schedule_followup(task_id=…)`` lookup. ``conversation_id`` is the
    S1174 PR-1 field that gates the agent-follow-up wake; setting it
    here lets ``create_implicit_followup_subscription`` arm a Phase-1
    follow-up the existing signal handler will fire on terminal.
    """
    from django.utils import timezone

    from core.models import AgentExecution

    agent = _resolve_claude_code_agent()
    if agent is None:
        logger.warning(
            "[CLAUDE_CODE_NO_AGENT_ROW] no Agent row matches names=%s — "
            "AgentExecution telemetry skipped for task_id=%s. Result "
            "still flows via CeleryTaskEvent + _post_to_conversation.",
            _CLAUDE_CODE_AGENT_NAMES, celery_task_id,
        )
        return None

    try:
        record = AgentExecution.objects.create(
            agent=agent,
            task=(task_description or '')[:500],
            status='in_progress',
            input_data={
                'task_description': (task_description or '')[:2000],
                'conversation_id': conversation_id or '',
                'requested_by': requested_by,
                'request_mode': request_mode,
                'celery_task_id': celery_task_id,
                'source': 'claude_code_engineer_task',
            },
            output_data={},
            last_heartbeat_at=timezone.now(),
            conversation_id=conversation_id or None,
        )
        logger.info(
            "[CLAUDE_CODE_EXECUTION_CREATED] execution_id=%s "
            "celery_task_id=%s conversation_id=%s agent=%s",
            record.id, celery_task_id, conversation_id or '<none>',
            agent.name,
        )
        return record
    except Exception as exc:
        logger.warning(
            "_create_engineer_execution_record: swallowed (%s: %s) — "
            "telemetry skipped for task_id=%s",
            type(exc).__name__, exc, celery_task_id,
        )
        return None


def _persist_engineer_terminal_state(
    execution_record,
    *,
    result: Optional[Dict[str, Any]] = None,
    exception: Optional[BaseException] = None,
    post_back_status: Optional[str] = None,
) -> None:
    """Update the AgentExecution row when the engineer task ends.

    Three callable contracts:

    * ``result=<dict>`` on normal completion. ``status`` is derived from
      the result envelope: ``'completed'`` when envelope status is
      'success' / 'contract_failure', ``'failed'`` for 'error'.
      ``output_data`` carries the full envelope (summary, files_changed,
      pr_url, provider, mode) so callers can retrieve the result even
      when the post-back was skipped.
    * ``exception=<exc>`` on raised exception. ``status='failed'``,
      ``error_message=str(exc)``. Used by the wrapping Celery task to
      preserve traceback context without re-raising inside this helper.
    * ``post_back_status='failed'`` — late-binding flag set by
      ``_post_to_conversation`` when the ChatConversation write raises
      AFTER the LLM run already produced a result. Marks the row
      ``status='failed'`` so the post-back failure is observable, but
      preserves the prior ``output_data`` (the summary IS retrievable
      from the row even though the user never saw it).

    Defensive — never raises. A failure persisting telemetry must not
    stop the wrapping task from running its own terminal handling.
    """
    from django.utils import timezone

    if execution_record is None:
        return

    update_fields = ['status', 'completed_at']
    try:
        execution_record.completed_at = timezone.now()

        if exception is not None:
            execution_record.status = 'failed'
            execution_record.error_message = str(exception)[:1000]
            update_fields.append('error_message')
        elif post_back_status == 'failed':
            # The LLM run completed, but the post-back write failed.
            # Preserve output_data so the result is still queryable.
            existing_output = execution_record.output_data or {}
            existing_output['post_back_status'] = 'failed'
            execution_record.output_data = existing_output
            execution_record.status = 'failed'
            update_fields.append('output_data')
        elif result is not None:
            envelope_status = result.get('status', 'success')
            if envelope_status in ('error',):
                execution_record.status = 'failed'
                err = result.get('error') or result.get('summary')
                if err:
                    execution_record.error_message = str(err)[:1000]
                    update_fields.append('error_message')
            else:
                execution_record.status = 'completed'
            execution_record.output_data = {
                'status': envelope_status,
                'summary': (result.get('summary') or '')[:2000],
                'files_changed': result.get('files_changed') or [],
                'pr_url': result.get('pr_url'),
                'provider': result.get('provider', 'anthropic'),
                'mode': result.get('mode'),
                'iterations': result.get('iterations'),
            }
            update_fields.append('output_data')
        else:
            # Defensive fallback — no exception, no result, no flag.
            # Mark completed with empty output so the row at least
            # closes; should not happen in practice.
            execution_record.status = 'completed'

        execution_record.save(update_fields=update_fields)
    except Exception as exc:
        logger.warning(
            "_persist_engineer_terminal_state: swallowed (%s: %s) — "
            "AgentExecution row may be stuck in_progress",
            type(exc).__name__, exc,
        )


def _mark_post_back_failed_on_execution(
    agent_execution_id: Optional[str], reason: str
) -> None:
    """Late-binding helper used by ``_post_to_conversation``.

    Called when ChatConversation write succeeds at the LLM-loop level
    but fails when persisting the user-facing message. Sets
    ``output_data['post_back_status']='failed'`` and ``status='failed'``
    on the AgentExecution row so the post-back failure is observable in
    ops surfaces.
    """
    if not agent_execution_id:
        return
    try:
        from core.models import AgentExecution

        record = AgentExecution.objects.filter(id=agent_execution_id).first()
        if record is None:
            return
        _persist_engineer_terminal_state(
            record, post_back_status='failed',
        )
        # Also stamp the reason into the existing output_data
        try:
            existing = record.output_data or {}
            existing['post_back_failure_reason'] = reason[:500]
            record.output_data = existing
            record.save(update_fields=['output_data'])
        except Exception:
            pass
    except Exception as exc:
        logger.warning(
            "_mark_post_back_failed_on_execution: swallowed (%s: %s)",
            type(exc).__name__, exc,
        )

REPO_ROOT = '/app'  # Railway container path — may be read-only
WRITABLE_ROOT = '/tmp/engineer-workspace'  # Writable clone for git operations

# Session 1230 P4 — Two-mode system prompts.
#
# Session 1229 Step 5 surfaced a behavioral delta on the OpenAI fallback path:
# given the task `"List 3 Python files in core/services/ + line counts (markdown
# table only)"`, gpt-5-mini ran 12 `read_file` iterations (on real files —
# correct readonly work) and then concluded `"I'm ready to make the change,
# but I don't yet know what you want me to do. Could you please clarify the
# engineering task?"`. The single SYSTEM_PROMPT was anchored to write-mode
# work ("Always create a branch", "Write clear commit messages", "summarize
# what you changed and provide the PR link"). Under tool pressure, gpt-5-mini
# pattern-matched the dominant write-mode framing and asked for clarification
# rather than producing the markdown-table answer the task asked for.
#
# Rigby's design call (Session 1230): two separate prompts, selected at
# dispatch via `request_mode`. Mode-branching inside one prompt is too easy
# for the model to mis-route under tool pressure. The dispatcher infers mode
# from task verbs when caller doesn't override (request_mode='auto').

CHANGE_SYSTEM_PROMPT = """You are Claude Code Engineer, an autonomous coding agent deployed inside the Donkey Betz platform.

You have been invoked by Rigby (the PA) to perform an engineering task that REQUIRES CODE CHANGES. You have REAL tools to read files, write code, search the codebase, and create git branches/commits/PRs.

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

ANSWER_SYSTEM_PROMPT = """You are Claude Code Engineer, an autonomous code-reading agent deployed inside the Donkey Betz platform.

You have been invoked by Rigby (the PA) to ANSWER A QUESTION about the codebase. This is a READONLY task — Rigby wants information, not a code change. Do NOT create branches, write files, commit, or open PRs.

You have REAL tools to read files, search code, and inspect git state. Use them to gather the information you need, then RETURN THE ANSWER DIRECTLY.

RULES:
- DO NOT ask for clarification. The task is the deliverable spec — read it carefully and produce the requested shape.
- DO NOT propose code changes. If you think a change is warranted, mention it as a single trailing sentence; the body of your response must be the answer.
- DO NOT say "I'm ready to make the change" — you are not making a change. You are answering a question.
- If the task asks for a specific output format (markdown table, bullet list, JSON, file path, line count, etc.), produce exactly that format. The format IS the contract.
- Tool budget: gather what you need, stop when you have enough. Avoid re-reading the same file twice.
- Report concisely. Rigby and Chris will see your response verbatim.

CODEBASE:
- Django 5.0 + PostgreSQL + Celery + Redis + React frontend
- core/ has agents, services, tasks, views, models
- frontend/src/ has React components, stores, hooks
- 82 agents, 77 spiders, 134 services

Your final message MUST be the requested answer in the requested shape. Do not hedge, do not request clarification, do not offer alternatives.
"""

# Mode → prompt mapping. `_infer_request_mode` resolves 'auto' to one of these.
_SYSTEM_PROMPT_BY_MODE = {
    'answer': ANSWER_SYSTEM_PROMPT,
    'change': CHANGE_SYSTEM_PROMPT,
}

# Verb-based heuristic for `request_mode='auto'`. If any change-verb appears in
# the task, treat as 'change'; otherwise default to 'answer' since answer mode
# is the safer default (avoids surprise PRs from ambiguous prompts).
#
# Match is case-insensitive, whole-word, matches at the start of a clause
# (start-of-string or after `.`/`!`/`?`/newline/colon/comma) so verbs embedded
# in nouns ("the create_pr tool") don't trigger change mode.
_CHANGE_VERBS = (
    'add', 'change', 'commit', 'create', 'delete', 'edit', 'fix',
    'implement', 'introduce', 'modify', 'patch', 'refactor', 'remove',
    'rename', 'rewrite', 'update', 'wire', 'write',
)

# Final-message stall markers — substrings that signal the engineer asked for
# clarification rather than producing the requested deliverable shape. Used by
# the answer-mode contract check to trigger a single retry with a stronger
# preamble.
_CLARIFICATION_STALL_MARKERS = (
    "could you please clarify",
    "could you clarify",
    "i'm not sure what you want",
    "i don't yet know what you want",
    "i'm ready to make the change",
    "please describe the",
    "what would you like me to",
    "let me know which",
)


def _infer_request_mode(task_description: str) -> str:
    """Return 'answer' or 'change' from a verb-based heuristic on `task_description`.

    Used when the caller passes `request_mode='auto'`. Explicit
    `request_mode='answer'` / `'change'` from the caller bypasses this.

    Conservative: defaults to 'answer' on ambiguity. The cost of misclassifying
    a change task as answer is one wasted dispatch (engineer reads files and
    returns text instead of opening a PR); the cost of misclassifying an
    answer task as change is the original Session 1229 stall bug.
    """
    import re

    task = (task_description or '').lower().strip()
    if not task:
        return 'answer'

    # Match each change verb at a clause boundary. The boundary chars cover
    # start-of-string, sentence terminators, and common punctuation.
    for verb in _CHANGE_VERBS:
        if re.search(r'(?:^|[.!?\n:,]\s*)' + re.escape(verb) + r'\b', task):
            return 'change'

    return 'answer'


def _looks_like_clarification_stall(final_text: str) -> bool:
    """True if the engineer's final message looks like a clarification stall.

    Used by the answer-mode contract: a stall on an answer task is a contract
    failure (the engineer was supposed to produce a deliverable shape, not
    ask back). One retry with a stronger preamble; if it stalls again, the
    caller surfaces a `status='contract_failure'` envelope.
    """
    if not final_text:
        return False
    text = final_text.lower()
    return any(marker in text for marker in _CLARIFICATION_STALL_MARKERS)

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


def _translate_tools_to_openai(anthropic_tools: List[dict]) -> List[dict]:
    """Convert Anthropic tool definitions to OpenAI function-call format.

    Session 1226 P4 — Workaround for exhausted Anthropic credits. Anthropic's
    `{"name": ..., "description": ..., "input_schema": {...}}` shape maps
    cleanly to OpenAI's `{"type": "function", "function": {"name": ...,
    "description": ..., "parameters": {...}}}`. JSON Schema bodies are
    compatible between providers, so input_schema → parameters is a
    rename, not a transformation.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        }
        for tool in anthropic_tools
    ]


_OPENAI_TOOLS = _translate_tools_to_openai(TOOLS)


def _execute_engineering_task_openai(
    task_description: str,
    max_iterations: int,
    system_prompt: str = CHANGE_SYSTEM_PROMPT,
) -> Dict[str, Any]:
    """OpenAI fallback path for execute_engineering_task.

    Session 1226 P4 workaround: when Anthropic credits are exhausted, route
    the autonomous engineer through gpt-5-mini via the existing
    openai_client_factory. Same TOOLS, different message format. Caller is
    responsible for git workspace setup + conversation post-back; this
    function only owns the LLM loop.

    Session 1230 P4: `system_prompt` is now caller-selected (ANSWER vs
    CHANGE) per the `request_mode` contract. Defaults to CHANGE_SYSTEM_PROMPT
    for backward compatibility on direct callers (tests, ad-hoc).

    Returns: {'final_text': str, 'files_changed': list, 'pr_url': str|None}
    """
    from core.services.openai_client_factory import get_openai_client

    client = get_openai_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task_description},
    ]
    files_changed: List[str] = []
    pr_url: Optional[str] = None
    final_text = ''

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model='gpt-5-mini',
            messages=messages,
            tools=_OPENAI_TOOLS,
            # Session 1224 memory rule: gpt-5* needs ≥2000 reasoning headroom;
            # 4000 leaves comfortable room for both reasoning + tool-call args.
            max_completion_tokens=4000,
        )
        choice = response.choices[0]
        msg = choice.message
        finish_reason = choice.finish_reason

        # Done — no more tool calls expected
        if finish_reason == 'stop' and not msg.tool_calls:
            final_text = msg.content or ''
            break

        # Tool calls path. Append the assistant message FIRST (with tool_calls
        # field populated) so the model's next turn sees its own tool_call_ids.
        if msg.tool_calls:
            assistant_msg = {
                'role': 'assistant',
                'content': msg.content or '',
                'tool_calls': [
                    {
                        'id': tc.id,
                        'type': 'function',
                        'function': {
                            'name': tc.function.name,
                            'arguments': tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            }
            messages.append(assistant_msg)

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_input = json.loads(tc.function.arguments or '{}')
                except json.JSONDecodeError:
                    tool_input = {}
                logger.info(f"[ClaudeEngineer:openai] Tool: {tool_name} (iteration {iteration+1})")
                result = _execute_tool(tool_name, tool_input)

                if tool_name == 'write_file':
                    files_changed.append(tool_input.get('path', '?'))
                elif tool_name == 'create_pr' and 'github.com' in result:
                    pr_url = result.strip()

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tc.id,
                    'content': result[:10000],  # cap per-result at 10KB
                })

            # Trim old messages to keep context size sane (mirror Anthropic path).
            if len(messages) > 24:
                # Keep system + the last 20 turns
                messages = [messages[0]] + messages[-20:]
        else:
            # Unexpected finish_reason without tool_calls — bail to avoid infinite loop
            final_text = (msg.content or '') or f"Engineer stopped with finish_reason={finish_reason} and no tool calls."
            break
    else:
        final_text = f"Reached max iterations ({max_iterations}). Task may be incomplete."

    return {
        'final_text': final_text,
        'files_changed': files_changed,
        'pr_url': pr_url,
    }


def execute_engineering_task(
    task_description: str,
    conversation_id: Optional[str] = None,
    requested_by: str = 'rigby',
    max_iterations: int = 500,
    request_mode: str = 'auto',
    agent_execution_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute an engineering task using Claude with codebase tools.

    Args:
        task_description: What to do (from Rigby or Chris)
        conversation_id: PA conversation to post results to
        requested_by: Who requested this (for attribution)
        max_iterations: Max tool-use iterations
        request_mode: 'answer' (readonly Q&A), 'change' (code change), or
            'auto' (verb-heuristic dispatch). Session 1230 P4. See module
            docstring for the original behavioral-delta incident.

    Returns:
        Dict with status, summary, files_changed, pr_url, provider, mode

    Session 1226 P4 — provider routing:
    When CLAUDE_CODE_ENGINE_PROVIDER='openai' the LLM loop runs through
    gpt-5-mini instead of claude-sonnet-4. Used as a temporary workaround
    when Anthropic credits are exhausted. Default 'anthropic' preserves
    prod behavior.

    Session 1230 P4 — request_mode + clarification-stall contract:
    On answer-mode tasks, after the primary LLM loop completes the dispatcher
    checks `final_text` against `_CLARIFICATION_STALL_MARKERS`. If matched,
    the loop is retried ONCE with a hard "do not ask for clarification"
    preamble prepended to `task_description`. If the retry also stalls, the
    return envelope flips `status` to `'contract_failure'` so callers can
    surface the behavioral delta rather than silently posting a stall.
    """
    # Resolve request_mode + select system prompt.
    requested_mode = (request_mode or 'auto').strip().lower()
    if requested_mode == 'auto':
        resolved_mode = _infer_request_mode(task_description)
    elif requested_mode in _SYSTEM_PROMPT_BY_MODE:
        resolved_mode = requested_mode
    else:
        logger.warning(
            "[ClaudeEngineer] unknown request_mode=%r — falling back to "
            "verb-heuristic auto-detect.", requested_mode,
        )
        resolved_mode = _infer_request_mode(task_description)
    system_prompt = _SYSTEM_PROMPT_BY_MODE[resolved_mode]
    logger.info(
        "[ClaudeEngineer] dispatch: requested_mode=%s resolved_mode=%s "
        "task_chars=%d max_iter=%d",
        requested_mode, resolved_mode, len(task_description or ''),
        max_iterations,
    )

    # Session 1226 P4 — OpenAI fallback path
    provider = os.environ.get('CLAUDE_CODE_ENGINE_PROVIDER', 'anthropic').strip().lower()
    if provider == 'openai':
        _ensure_git_repo()
        try:
            result = _execute_engineering_task_openai(
                task_description=task_description,
                max_iterations=max_iterations,
                system_prompt=system_prompt,
            )
            final_text = result['final_text']
            envelope_status = 'success'

            # Session 1230 P4 — answer-mode clarification-stall contract.
            # One retry with a stronger preamble. Only fires on answer mode
            # because change mode legitimately asks for clarification when
            # the task is ambiguous.
            if (resolved_mode == 'answer'
                    and _looks_like_clarification_stall(final_text)):
                logger.warning(
                    "[ClaudeEngineer:openai] clarification stall detected on "
                    "answer-mode task — retrying once with hard preamble. "
                    "Original first-line: %s",
                    (final_text or '').splitlines()[0][:120] if final_text else '',
                )
                hardened_task = (
                    'READONLY ANSWER TASK — do not ask for clarification, do '
                    'not propose code changes, do not say "I am ready to make '
                    'the change". Read the task carefully and produce exactly '
                    'the requested output format. The task is:\n\n'
                    + task_description
                )
                retry = _execute_engineering_task_openai(
                    task_description=hardened_task,
                    max_iterations=max_iterations,
                    system_prompt=ANSWER_SYSTEM_PROMPT,
                )
                final_text = retry['final_text']
                if _looks_like_clarification_stall(final_text):
                    envelope_status = 'contract_failure'
                    logger.warning(
                        "[ClaudeEngineer:openai] retry ALSO stalled — surfacing "
                        "contract_failure to caller.",
                    )
                else:
                    logger.info(
                        "[ClaudeEngineer:openai] retry resolved the stall.",
                    )
                # Re-use the retry's tool-call side effects (files_changed,
                # pr_url) since the original loop's side effects ran on the
                # original `task_description` and the retry ran on the same
                # underlying engineer.
                result = retry

            _post_to_conversation(
                conversation_id, final_text,
                result['files_changed'], result['pr_url'],
                agent_execution_id=agent_execution_id,
            )
            return {
                'status': envelope_status,
                'summary': final_text[:2000] if final_text else '',
                'files_changed': result['files_changed'],
                'pr_url': result['pr_url'],
                'provider': 'openai',
                'mode': resolved_mode,
            }
        except Exception as e:
            logger.error(f"[ClaudeEngineer:openai] Task failed: {e}")
            error_msg = f"Engineering task failed (openai path): {str(e)}"
            _post_to_conversation(
                conversation_id, error_msg, [], None,
                agent_execution_id=agent_execution_id,
            )
            return {
                'status': 'error',
                'error': str(e),
                'provider': 'openai',
                'mode': resolved_mode,
            }

    # Default Anthropic path (unchanged from prior behavior)
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
                        system=system_prompt,
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

        # Post result to conversation. Session 1262: _post_to_conversation
        # is now fail-loud — it ERROR-logs when conversation_id is None and
        # the AgentExecution row (queryable via agent_execution_id) carries
        # the result envelope so callers can recover. The legacy
        # ``if conversation_id:`` guards that produced silent drops on
        # None are removed (the guard now lives inside _post_to_conversation).
        _post_to_conversation(
            conversation_id, final_text, files_changed, pr_url,
            agent_execution_id=agent_execution_id,
        )

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

        _post_to_conversation(
            conversation_id, error_msg, [], None,
            agent_execution_id=agent_execution_id,
        )

        return {'status': 'error', 'error': str(e)}


def _post_to_conversation(
    conversation_id: Optional[str],
    summary: str,
    files_changed: list,
    pr_url: Optional[str] = None,
    *,
    agent_execution_id: Optional[str] = None,
):
    """Post engineering results back to the PA conversation.

    Session 1262 fail-loud contract (replaces the pre-S1262 silent
    no-op on ``conversation_id=None``):

    * If ``conversation_id`` is empty/None: ERROR-log with the greppable
      marker ``[CLAUDE_CODE_POSTBACK_DROPPED]`` and return cleanly. The
      LLM run itself succeeded; the result is queryable via the
      AgentExecution row (``agent_execution_id``). Do NOT raise — this
      is a dispatch metadata issue, not a task failure.
    * If ``ChatConversation`` creation raises: mark the AgentExecution
      row ``status='failed'`` + ``output_data['post_back_status']='failed'``,
      ERROR-log with marker ``[CLAUDE_CODE_POSTBACK_FAILED]``, then
      **raise** so ``CeleryTaskEvent.status=FAILURE`` is visible. The
      wrapping ``claude_code_engineer_task`` is configured with
      ``max_retries=0`` so the LLM budget is not re-burned.
    * WebSocket broadcast failure remains a WARN (S1103c handling
      preserved): the DB row exists, the ChatUI catches on next poll.
    """
    from core.models import ChatConversation

    if not conversation_id:
        logger.error(
            "[CLAUDE_CODE_POSTBACK_DROPPED] conversation_id is empty/None — "
            "ChatConversation post-back skipped. summary_len=%d "
            "files_changed=%s pr_url=%s agent_execution_id=%s. "
            "Result IS retrievable via AgentExecution.output_data when "
            "agent_execution_id is set.",
            len(summary or ''), files_changed, pr_url, agent_execution_id,
        )
        return

    # Build result message
    parts = [summary]
    if files_changed:
        parts.append(f"\n**Files changed:** {', '.join(files_changed)}")
    if pr_url:
        parts.append(f"\n**PR:** {pr_url}")

    content = '\n'.join(parts)

    # Resolve user
    user = ChatConversation.objects.filter(
        conversation_id=conversation_id, user__isnull=False
    ).values_list('user_id', flat=True).first()

    try:
        chat_row = ChatConversation.objects.create(
            user_id=user,
            conversation_id=conversation_id,
            user_message=content,
            assistant_response='',
            source='claude-code',
            platform='agent',
            metadata={'autonomous': True, 'agent': 'claude_code_engineer', 'files_changed': files_changed, 'pr_url': pr_url},
        )
    except Exception as exc:
        logger.error(
            "[CLAUDE_CODE_POSTBACK_FAILED] ChatConversation write raised "
            "for conversation_id=%s agent_execution_id=%s (%s: %s). "
            "Marking AgentExecution post_back_status=failed and re-raising "
            "so CeleryTaskEvent.status=FAILURE is visible. Task is "
            "configured with max_retries=0; the LLM budget is NOT "
            "re-spent.",
            conversation_id, agent_execution_id, type(exc).__name__, exc,
            exc_info=True,
        )
        _mark_post_back_failed_on_execution(
            agent_execution_id,
            reason=f"ChatConversation create raised: {type(exc).__name__}: {exc}",
        )
        raise

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
