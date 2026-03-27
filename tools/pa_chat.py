#!/usr/bin/env python3
"""
Claude Code ↔ PA Chat Helper (3-Way Chat Edition)

Send messages to the Personal Assistant via the Railway API and get responses.
Used by Claude Code to participate in 3-way conversations with Chris and Rigby.

Usage:
    # Talk to Rigby (triggers PA processing)
    python tools/pa_chat.py "Your message here" --conversation pa-xxxxx

    # Talk without triggering Rigby (store-only, visible in ChatUI)
    python tools/pa_chat.py --say "Hey Chris, I can fix that" --conversation pa-xxxxx

    # Talk and trigger Rigby (explicit @rigby or --trigger-pa)
    python tools/pa_chat.py --say "@rigby can you check the deploy?" --conversation pa-xxxxx

    # Watch conversation in real-time (see all participants)
    python tools/pa_chat.py --watch pa-xxxxx

    # Legacy: show tool details
    python tools/pa_chat.py --tools "Check system health" --conversation pa-xxxxx

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
POLL_TIMEOUT = 300  # 5 minutes — matches Celery PA task hard limit
MAX_CONTENT_LENGTH = 5000  # truncate long responses
WATCH_POLL_INTERVAL = 2  # seconds for watch mode


def _get_token():
    """Resolve auth token from env, .env file, or raise."""
    token = os.environ.get("PA_API_TOKEN")
    if token:
        return token

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
    """Send a message to the PA and return the task_id (triggers Rigby)."""
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


def post_message(message, conversation_id, trigger_pa=None):
    """
    Post a message to the conversation (store-only by default).
    Auto-triggers Rigby if @rigby is mentioned, unless trigger_pa is explicitly set.
    """
    token = _get_token()
    base = _get_base_url()

    payload = {
        "message": message,
        "source": "claude-code",
    }
    if trigger_pa is not None:
        payload["trigger_pa"] = trigger_pa

    data, status = _http_request(
        f"{base}/api/pa/conversations/{conversation_id}/message/",
        "POST", payload, token
    )

    if status != 200 or not data.get("success"):
        return None, data.get("error", f"HTTP {status}")

    return data, None


def poll_result(task_id):
    """Poll for PA task completion."""
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
    """Send a message and wait for the full response."""
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


# ── Watch mode ─────────────────────────────────────────────────────────────


def watch(conversation_id, timeout=3600):
    """
    Watch a conversation in real-time. Shows all participants' messages.
    Polls the incremental messages endpoint every 2 seconds.
    """
    token = _get_token()
    base = _get_base_url()
    url = f"{base}/api/pa/conversations/{conversation_id}/messages/"

    # Get initial messages to establish baseline
    data, status = _http_request(url, "GET", token=token)
    if status != 200:
        yield {"error": f"Failed to load conversation: HTTP {status}"}
        return

    # Track seen message IDs
    seen_ids = set()
    for msg in data.get("messages", []):
        seen_ids.add(msg["id"])

    start = time.time()

    while time.time() - start < timeout:
        time.sleep(WATCH_POLL_INTERVAL)

        data, status = _http_request(url, "GET", token=token)
        if status != 200:
            continue

        for msg in data.get("messages", []):
            if msg["id"] in seen_ids:
                continue
            seen_ids.add(msg["id"])
            yield msg

    yield {"error": "Watch timed out"}


# ── Listen mode (legacy) ──────────────────────────────────────────────────


def listen(conversation_id, timeout=600, poll_interval=5):
    """Watch a conversation for new user messages from the browser (legacy)."""
    token = _get_token()
    base = _get_base_url()
    url = f"{base}/api/pa/conversations/{conversation_id}/"

    data, status = _http_request(url, "GET", token=token)
    if status != 200:
        yield {"error": f"Failed to load conversation: HTTP {status}"}
        return

    seen_ids = {m["id"] for m in data.get("messages", [])}
    start = time.time()

    while time.time() - start < timeout:
        time.sleep(poll_interval)
        data, status = _http_request(url, "GET", token=token)
        if status != 200:
            continue

        for msg in data.get("messages", []):
            if msg["id"] in seen_ids:
                continue
            seen_ids.add(msg["id"])
            role = msg.get("role", "")
            source = msg.get("source", "")
            if role == "user" and source in ("web", "api"):
                yield msg
            elif role == "assistant" and source == "pa":
                yield msg

    yield {"error": "Listen timed out"}


# ── CLI ─────────────────────────────────────────────────────────────────────

_SOURCE_LABELS = {
    'web': 'CHRIS',
    'claude-code': 'CLAUDE CODE',
    'pa': 'RIGBY',
    'api': 'API',
}

_SOURCE_COLORS = {
    'web': '\033[96m',       # Cyan for Chris
    'claude-code': '\033[92m',  # Green for Claude Code
    'pa': '\033[94m',        # Blue for Rigby
}
_RESET = '\033[0m'


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
            if len(formatted) > 2000:
                formatted = formatted[:2000] + "\n    ... (truncated)"
            lines.append(f"    Result: {formatted}")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="3-Way Chat: Claude Code ↔ Chris ↔ Rigby")
    parser.add_argument("message", nargs="?", help="Message to send (triggers Rigby)")
    parser.add_argument(
        "--say", "-s", metavar="MSG",
        help="Post message without triggering Rigby (store-only, visible in ChatUI). Auto-triggers if @rigby mentioned."
    )
    parser.add_argument(
        "--watch", "-w", metavar="CONV_ID",
        help="Watch conversation in real-time (see all participants)"
    )
    parser.add_argument(
        "--tools", action="store_true", help="Show tool run details"
    )
    parser.add_argument(
        "--raw", action="store_true", help="Show raw JSON response"
    )
    parser.add_argument(
        "--conversation", "--conversation-id", "-c", dest="conversation_id",
        help="Conversation ID to use"
    )
    parser.add_argument(
        "--trigger-pa", action="store_true",
        help="Force trigger Rigby even without @mention (with --say)"
    )
    # Legacy
    parser.add_argument(
        "--listen", "-l", metavar="CONV_ID",
        help="[Legacy] Watch for browser messages"
    )
    parser.add_argument("--listen-timeout", type=int, default=600)

    args = parser.parse_args()

    # ── Watch mode (3-way) ──
    if args.watch:
        conv_id = args.watch
        sys.stderr.write(f"Watching conversation {conv_id}...\n")
        sys.stderr.write("All participants' messages will appear here.\n\n")
        try:
            for msg in watch(conv_id):
                if "error" in msg:
                    sys.stderr.write(f"{msg['error']}\n")
                    break
                role = msg.get("role", "user")
                source = msg.get("source", "web")
                content = msg.get("content", "")
                label = _SOURCE_LABELS.get(source, source.upper())
                color = _SOURCE_COLORS.get(source, '')

                if len(content) > 3000:
                    content = content[:3000] + "\n... (truncated)"
                print(f"\n{color}[{label}]{_RESET}\n{content}")
                sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stderr.write("\nWatch ended.\n")
        sys.exit(0)

    # ── Say mode (store-only, 3-way chat) ──
    if args.say:
        if not args.conversation_id:
            print("Error: --say requires --conversation <id>", file=sys.stderr)
            sys.exit(1)

        result, err = post_message(
            args.say,
            args.conversation_id,
            trigger_pa=True if args.trigger_pa else None
        )
        if err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)

        triggered = result.get("trigger_pa", False)
        sys.stderr.write(f"Posted to {args.conversation_id}")
        if triggered:
            sys.stderr.write(" (Rigby triggered)")
            # Poll for Rigby's response
            task_id = result.get("task_id")
            if task_id:
                sys.stderr.write(f"\nTask: {task_id} — polling...\n")
                poll_data, poll_err = poll_result(task_id)
                if poll_err:
                    print(f"Error polling: {poll_err}", file=sys.stderr)
                elif poll_data:
                    content = poll_data.get("content", "")
                    if len(content) > MAX_CONTENT_LENGTH:
                        content = content[:MAX_CONTENT_LENGTH] + "\n... (truncated)"
                    print(content)
        else:
            sys.stderr.write(" (store-only, Rigby not triggered)")
        sys.stderr.write("\n")
        sys.exit(0)

    # ── Listen mode (legacy) ──
    if args.listen:
        sys.stderr.write(f"Listening for browser replies on {args.listen}...\n")
        sys.stderr.write("(Type a message in the PA chat window — it will appear here)\n\n")
        for msg in listen(args.listen, timeout=args.listen_timeout):
            if "error" in msg:
                sys.stderr.write(f"{msg['error']}\n")
                break
            role = msg.get("role", "user")
            ts = msg.get("timestamp", "")
            content = msg.get("content", "")
            if role == "user":
                print(f"\n[USER @ {ts}]\n{content}")
            else:
                if len(content) > 2000:
                    content = content[:2000] + "\n... (truncated)"
                print(f"\n[PA @ {ts}]\n{content}")
            sys.stdout.flush()
        sys.exit(0)

    # ── Default: send to Rigby (legacy behavior) ──
    if not args.message:
        if not sys.stdin.isatty():
            args.message = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)

    if not args.message:
        print("Error: No message provided", file=sys.stderr)
        sys.exit(1)

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
