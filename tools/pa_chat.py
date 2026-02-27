#!/usr/bin/env python3
"""
Claude Code ↔ PA Chat Helper

Send messages to the Personal Assistant via the Railway API and get responses.
Used by Claude Code to communicate with the PA during development sessions.

Usage:
    python tools/pa_chat.py "Your message here"
    python tools/pa_chat.py --tools "Check system health"
    python tools/pa_chat.py --raw "Show me video history"
    python tools/pa_chat.py --conversation-id pa-xxxxx "Follow up message"

Environment:
    PA_API_TOKEN: Auth token (falls back to .env TEST_AUTH_TOKEN, then Railway lookup)
    PA_API_URL: Base URL (default: https://donkey-betz-platform-production.up.railway.app)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"
POLL_INTERVAL = 3  # seconds
POLL_TIMEOUT = 180  # 3 minutes max
MAX_CONTENT_LENGTH = 5000  # truncate long responses


def _get_token():
    """Resolve auth token from env, .env file, or raise."""
    # 1. Direct env var
    token = os.environ.get("PA_API_TOKEN")
    if token:
        return token

    # 2. Read from .env file
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("PA_API_TOKEN="):
                    return line.split("=", 1)[1].strip().strip("'\"")

    raise RuntimeError(
        "No PA_API_TOKEN found. Set it via:\n"
        "  export PA_API_TOKEN=<your-token>\n"
        "Or add PA_API_TOKEN=<token> to .env"
    )


def _get_base_url():
    return os.environ.get("PA_API_URL", DEFAULT_BASE_URL)


def _http_request(url, method="GET", data=None, token=None):
    """Make an HTTP request and return parsed JSON."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Token {token}"

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        headers=headers,
        method=method,
    )

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        try:
            return json.loads(body), e.code
        except json.JSONDecodeError:
            return {"error": body}, e.code


# ── Public API ──────────────────────────────────────────────────────────────


def send_message(message, conversation_id=None, context=None):
    """
    Send a message to the PA and return the task_id.

    Returns: (task_id: str, error: str | None)
    """
    token = _get_token()
    base = _get_base_url()

    payload = {
        "message": message,
        "context": {**(context or {}), "source": "claude-code", "platform": "cli"},
        "source": "claude-code",
        "platform": "cli",
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    data, status = _http_request(f"{base}/api/pa/chat/", "POST", payload, token)

    if status != 200 or not data.get("success"):
        return None, data.get("error", f"HTTP {status}")

    return data["task_id"], None


def poll_result(task_id):
    """
    Poll for PA task completion.

    Returns: (result_dict, error: str | None)
    """
    token = _get_token()
    base = _get_base_url()
    start = time.time()

    while time.time() - start < POLL_TIMEOUT:
        data, status = _http_request(
            f"{base}/api/pa/chat/status/{task_id}/", "GET", token=token
        )

        task_status = data.get("status", "unknown")

        if task_status == "completed":
            return data, None
        elif task_status == "failed":
            err = data.get("error", "Task failed")
            # Session 1075: "Task not found" means celery hasn't picked it up yet
            # (e.g. during deploy). Retry instead of failing immediately.
            if "not found" in err.lower() and time.time() - start < POLL_TIMEOUT:
                time.sleep(POLL_INTERVAL)
                continue
            return None, err
        elif task_status == "processing":
            time.sleep(POLL_INTERVAL)
        else:
            return None, f"Unexpected status: {task_status}"

    return None, "Timed out waiting for PA response"


def chat(message, conversation_id=None, context=None):
    """
    Send a message and wait for the full response.

    Returns: {
        'content': str,
        'tool_runs': list,
        'conversation_id': str | None,
        'intent': str | None,
        'audio_url': str | None,
        'error': str | None,
    }
    """
    task_id, err = send_message(message, conversation_id, context)
    if err:
        return {"content": "", "error": err}

    result, err = poll_result(task_id)
    if err:
        return {"content": "", "error": err}

    return {
        "content": result.get("content", ""),
        "tool_runs": result.get("tool_runs", []),
        "conversation_id": result.get("conversation_id"),
        "intent": result.get("intent"),
        "audio_url": result.get("audio_url"),
        "error": None,
    }


# ── CLI ─────────────────────────────────────────────────────────────────────


def _format_tool_runs(tool_runs):
    """Format tool runs for CLI display."""
    if not tool_runs:
        return ""

    lines = ["\n--- Tool Runs ---"]
    for tr in tool_runs:
        status = "OK" if tr.get("ok") else "FAIL"
        tool = tr.get("tool", "?")
        latency = tr.get("latency_ms", 0)
        lines.append(f"  [{status}] {tool} ({latency}ms)")

        err = tr.get("error_message")
        if err:
            lines.append(f"        Error: {err}")

    return "\n".join(lines)


def _format_tool_runs_verbose(tool_runs):
    """Format tool runs with full result data."""
    if not tool_runs:
        return ""

    lines = ["\n--- Tool Runs (verbose) ---"]
    for tr in tool_runs:
        status = "OK" if tr.get("ok") else "FAIL"
        tool = tr.get("tool", "?")
        latency = tr.get("latency_ms", 0)
        lines.append(f"\n  [{status}] {tool} ({latency}ms)")

        result = tr.get("result")
        if result:
            formatted = json.dumps(result, indent=4, default=str)
            # Truncate very large results
            if len(formatted) > 2000:
                formatted = formatted[:2000] + "\n    ... (truncated)"
            lines.append(f"    Result: {formatted}")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Chat with the PA from CLI")
    parser.add_argument("message", nargs="?", help="Message to send")
    parser.add_argument(
        "--tools", action="store_true", help="Show tool run details"
    )
    parser.add_argument(
        "--raw", action="store_true", help="Show raw JSON response"
    )
    parser.add_argument(
        "--conversation-id", "-c", help="Continue existing conversation"
    )

    args = parser.parse_args()

    if not args.message:
        # Read from stdin if no argument
        if not sys.stdin.isatty():
            args.message = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)

    if not args.message:
        print("Error: No message provided", file=sys.stderr)
        sys.exit(1)

    # Send and wait
    sys.stderr.write("Sending to PA...\n")
    task_id, err = send_message(args.message, args.conversation_id)
    if err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    sys.stderr.write(f"Task: {task_id} — polling...\n")
    result, err = poll_result(task_id)
    if err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.raw:
        print(json.dumps(result, indent=2, default=str))
    else:
        content = result.get("content", "")
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "\n... (truncated)"
        print(content)

        if args.tools:
            print(_format_tool_runs_verbose(result.get("tool_runs", [])))
        else:
            print(_format_tool_runs(result.get("tool_runs", [])))

        cid = result.get("conversation_id")
        if cid:
            sys.stderr.write(f"\nConversation: {cid}\n")


if __name__ == "__main__":
    main()
